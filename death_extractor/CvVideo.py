import os, sys, subprocess
import cv2
from templates import get_templates

class CvVideo(object):
  #Constructor for the CvVideo object (requires OpenCV2 with ffmpeg support)
  def __init__(self, input_file, gif_path='gifs', temp_path='tmp', splitter='___', scale_width=0.6, scale_height=0.5):
    self.input_file = input_file
    self.input_file_tail = os.path.split(input_file)[1]
    try:
      self.uploader, self.vid_id = os.path.splitext(self.input_file_tail)[0].split(splitter)[0:2]
    except ValueError as e:
      self.uploader, self.vid_id = 'Unknown', os.path.splitext(self.input_file_tail)[0]
      
    self.vid_link = "http://youtube.com/watch?v=" + self.vid_id
    self.out_gif = os.path.join(gif_path, self.vid_id + '.gif')
    self.temp_vid = os.path.join(temp_path, self.vid_id + '.avi')

    self.stream = stream = cv2.VideoCapture(input_file)
    self.framecount = stream.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    self.fps = stream.get(cv2.cv.CV_CAP_PROP_FPS)
    self.duration = self.framecount / self.fps
    self.width = stream.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    self.height = stream.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)   
    self.fourcc = stream.get(cv2.cv.CV_CAP_PROP_FOURCC)
    self.img = None
    self.gray = None

    self.crop_width, self.crop_height = [int(self.width*scale_width), int(self.height*scale_height)]
    self.output = cv2.VideoWriter(self.temp_vid,0,7,(self.crop_width,self.crop_height))
    self.roi_reset()

    #set approx. aspect ratio
    if self.width == 480:
      self.aspect_ratio = (4,3)
    elif self.width == 576:
      self.aspect_ratio = (8,5)
    else:
      self.aspect_ratio = (16,9)

    #and assign templates accordingly:
    self.template_key = "".join(str(n) for n in self.aspect_ratio)
    self.templates = get_templates(self.template_key)

  @property
  def roi_default(self):
    """return our default crop ROI"""
    self._minY, self._minX = [int( (self.height - self.crop_height) / 2), int( (self.width - self.crop_width) / 2)]
    self._maxY, self._maxX = [self._minY + self.crop_height, self._minX + self.crop_width]
    return (self._minX, self._minY, self._maxX, self._maxY)

  @property
  def frame(self):
    """A pass-through to VideoCapture.POS_FRAMES"""
    return self.stream.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)

  @frame.setter
  def frame(self, frame):
    #print "Setting 'frame' to",frame,"out of",self.framecount
    if frame < 0 or frame > self.framecount:
      raise cv2.error("Requested frame is out of bounds")
    else:  
      self.stream.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame)

  @property
  def time(self):
    """Current position in the video (in seconds)"""
    return self.frame / self.fps
    
  @time.setter
  def time(self, seconds):
    #self.stream.set(cv2.cv.CV_CAP_PROP_POS_MSEC, seconds * 1000.0)
    self.frame = int(self.fps * seconds)
  
  @property
  def roi_rect(self):
    """The frame we use for cropping (ROI)"""
    return self._roi_rect
  
  @roi_rect.setter
  def roi_rect(self, rect):
    minX, minY, maxX, maxY = rect
    if minX < 0 or minY < 0 or maxX < 0 or maxY < 0 or maxX < minX or maxY < minY or maxX > self.width or maxY > self.height:
      raise cv2.error("Invalid dimensions for crop/ROI rectangle.")
    else:
      self._roi_rect = (minX, minY, maxX, maxY)

  @property
  def roi(self, roi_rect=None):
    """Subset of pixels (ROI) from current frame"""
    if not roi_rect:
      roi_rect = self.roi_rect
    if self.img == None:
      self.read()
    return self.img[roi_rect[1]:roi_rect[3], roi_rect[0]:roi_rect[2]]
  
  @roi.setter
  def roi(self, rect):
    self.roi_rect = rect

  @property
  def roi_gray(self, roi_rect=None):
    """Subset of pixels (ROI) from current frame, in grayscale"""
    if not roi_rect:
      roi_rect = self.roi_rect
    if self.gray == None:
      self.read()
    return self.gray[roi_rect[1]:roi_rect[3], roi_rect[0]:roi_rect[2]]

  def roi_reset(self):
    """Reset roi_rect to default for GIF output"""
    self.roi_rect = self.roi_default
    return self #chainable

  def set_frame(self, frame=0):
    """A chainable alias for CvVideo.frame = `frame`"""
    self.frame = frame
    return self #chainable
  
  def get_roi(self, color=True, rect=None):
    """Function to get roi with custom params"""
    if self.img == None:
      self.read()
    if not rect:
      return self.roi if color else self.roi_gray
    else:
      source = self.img if color else self.gray
      rect = rect if rect else self.roi_default
      return source[rect[1]:rect[3], rect[0]:rect[2]]
  
  def _skip(self, frames=1):
    """Generic function for scrubbing back/forward by `frames`"""
    #print "Starting at",self.frame,"skipping",frames,"frames"
    self.frame += frames
    sys.stdout.write("+" if frames>0 else "-")
    sys.stdout.flush()
    return self #for chaining
    
  def read(self):
    """Read next frame from stream and save image to img/gray properties"""
    ret, self.img = self.stream.read()
    self.gray = cv2.cvtColor(self.img, cv2.cv.CV_BGR2GRAY)
    return self #for chaining
    
  def read_frame(self, frame):
    """Go to `frame` in stream, read image to img/gray properties"""
    self.frame = frame
    return self.read() #chainable

  def read_time(self, seconds):
    """Go to `seconds` in stream, read image to img/gray properties""" 
    frame = self.fps*seconds
    return self.read_frame(frame) #chainable

  def skip_frames(self, frames=1):
    """Public alias for `_skip(frames)`"""
    return self._skip(frames).read() #chainable

  def skip_time(self, seconds=1):
    """Turn `seconds` into frames and then `_skip` by that amount"""
    return self.skip_frames(self.fps*seconds) #chainable
    
  def skip_forward(self, seconds=1):
    """Convenience alias for `skip_frames`"""
    return self.skip_frames(self.fps*seconds) #chainable
    
  def skip_back(self, seconds=5):
    """Convenience function goes backwards by `seconds`"""
    return self.skip_frames(self.fps * seconds * -1) #chainable

  def frame_to_file(self, out_file='frame.png', color=True, frame=-1, use_roi=False, roi_rect=None):
    """Write current frame (or specified `frame`) to `out_file`, optionally in grayscale and/or cropped to `roi_rect`"""
    if use_roi and not roi_rect:
      roi_rect = self.roi_default
    
    if frame >= 0: #Target specific frame?
      self.frame = frame
    self.read()
    
    if use_roi and not color:
      cv2.imwrite(out_file, self.get_roi(False, roi_rect) )
    elif use_roi and color:
      cv2.imwrite(out_file, self.get_roi(True, roi_rect) )
    elif not color:
      cv2.imwrite(out_file, self.gray)
    else:
      cv2.imwrite(out_file, self.img)
    
    return self #chainable
  
  def frame_to_output(self, color=True, frame=-1, use_roi=False, roi_rect=None):
    """Write current frame (or specified `frame`) to `CvVideo.output` buffer, optionally in grayscale and/or cropped to `roi_rect`"""
    if not self.output:
      raise cv2.error("No output stream for writing!")
    
    if use_roi and not roi_rect:
      roi_rect = self.roi_default
    
    if frame >= 0: #Target specific frame?
      self.frame = frame
    self.read()
    
    #dump output frames
    #cv2.imwrite('dump/'+ self.vid_id + str(int(frame)) + '.png', self.roi)

    if use_roi and not color:
      self.output.write(self.get_roi(False, roi_rect) )
    elif use_roi and color:
      self.output.write(self.get_roi(True, roi_rect) )
    elif not color:
      self.output.write(self.gray)
    else:
      self.output.write(self.img)
  
    return self #chainable
  
  #interval is in seconds, can be negative.
  def clip_to_output(self, from_frame=-1, to_frame=-1, frame_skip=None, interval=None, duration=None, color=True, use_roi=False, roi_rect=None):
    """Take a clip of input `stream` and write to `output` buffer as series of frames"""
    if use_roi and not roi_rect:
      roi_rect = self.roi_rect
    
    if from_frame < 0: #no specific frame? start from where we are
        from_frame = self.frame
    
    if not frame_skip: #use frame_skip if specified
      frame_skip = interval*self.fps if interval else 1 #frame-by-frame default
    
    if to_frame >= 0: #use to_frame if specified
      duration = None
    elif duration: #otherwise use duration if given
      to_frame = from_frame + duration*self.fps
    else: #still no value? use last frame
      to_frame = self.framecount-1
    
    if to_frame < from_frame: #make sure our loop isn't infinite!
      frame_skip = abs(frame_skip) * -1
    else:
      frame_skip = abs(frame_skip)
    
    #set a timestamp where we start:
    self.clip_start = self.time
    
    #ensure ints
    from_frame = int(from_frame)
    to_frame = int(to_frame)
    frame_skip = int(frame_skip)
    
    #do it
    for frame in range(from_frame, to_frame, frame_skip):
      self.frame_to_output(color, frame, use_roi)
      
    return self #chainable
  
  def gif_from_temp_vid(self, out_file=None, color=False, brightness=100, saturation=100, hue=100, delay=10, fuzz="4%", layers="OptimizeTransparency", flush_map=True):
    """Call ImageMagick's `convert` from shell to create a GIF of video file found at `temp_vid`"""
    if not out_file:
      out_file = self.out_gif

    if not color:
      saturation = 0

    #values associated with `-modulate`
    bsh = map(str, [brightness, saturation, hue])
    
    try:
      if os.path.getsize(self.temp_vid) < 6000:
        raise cv2.error("Didn't write any frames to AVI. Wrong crop-size? Wrong codec?")
    except os.error as e:
      raise cv2.error("Temp AVI doesn't exist!")

    print "\nWriting to", out_file, "..."
    
    command = ['convert']
    if delay > 0:
      command.extend(['-delay', str(delay)])

    command.append(self.temp_vid)

    if not all([v == '100' for v in bsh]):
      command.extend(['-modulate', ",".join(bsh)])
    if fuzz:
      command.extend(['-fuzz', str(fuzz)])
    if layers:
      command.extend(['-layers', str(layers)])
    if flush_map:
      command.extend(['+map'])
    command.append(out_file)

    subprocess.call(command)

    print "Write done"
    return self #chainable

  def clear_temp_vid(self):
    """Delete the file at location `temp_vid`"""
    try:
      os.remove(self.temp_vid)
    except IOError as e:
      print e

    return self #chainable

  def upload_gif_imgur(self, imgur, album_id='T6X43'):
    """Upload file at location `out_gif` to Imgur with a description linking to original YouTube source"""
    imgur.refresh_access_token()
    uploaded_image = imgur.upload_image(self.out_gif, title=self.vid_id, album=album_id, description="Watch full: http://youtube.com/watch?v="+self.vid_id)
    print "Uploaded to:",uploaded_image.link
    return self #chainable

  def upload_gif_tumblr(self, tumblr, blog_name=None, link_timestamp=True):
    blog_name = blog_name if blog_name else os.getenv('TUMBLR_BLOG_NAME')
    if link_timestamp:
      self.vid_link += "&t=%is" % (self.clip_start or 0)

    print "Uploading",self.out_gif,"to",blog_name,"..."
    upload_response = tumblr.create_photo(
      blog_name,
      data=self.out_gif,
      #caption="Watch full: "+self.vid_link,
      slug=self.vid_id,
      link=self.vid_link,
      tags=["spelunky","daily challenge","death","gif","book of the dead",self.uploader]
    )
    print upload_response
    return self #chainable
    
  #template_check is NOT chainable!
  def template_check(self, templates=None, threshold=0.84, method=cv2.TM_CCOEFF_NORMED, use_roi=False, roi_rect=None):
    """Cycle through each image in `templates` and perform OpenCV `matchTemplate` until match found (or return False)"""
    #TODO: Enable checking against min_val for methods where that's more appropriate
    
    if templates == None and hasattr(self, 'templates'):
      templates = self.templates
    elif templates == None:
      raise cv2.error("No template(s) to match against!")
    
    roi_rect = roi_rect if roi_rect else self.roi_default
    
    target = self.get_roi(False, roi_rect) if use_roi else self.gray
    
    #dump checked frames
    cv2.imwrite('dump/'+ self.vid_id + '/' + str(int(self.frame)) + '.png', target)
    
    for template in templates:
      res = cv2.matchTemplate(target, template, method)
      min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
      if max_val >= threshold:
        #cv2.imwrite('dump/'+ self.vid_id + '/' + str(int(self.frame)) + '-found.png', target)
        return True
    
    return False
  
  def until_template(self, interval=0.5, templates=None, threshold=0.84, method=cv2.TM_CCOEFF_NORMED, frame_skip=None, use_roi=False, roi_rect=None):
    """Scrub through video until a template is found"""
    frame_skip = frame_skip if frame_skip else interval*self.fps
    
    while not self.template_check(templates, threshold, method):
      self.skip_frames(frame_skip)
      
    return self #chainable

  def while_template(self, interval=0.5, templates=None, threshold=0.84, method=cv2.TM_CCOEFF_NORMED, frame_skip=None, use_roi=False, roi_rect=None):
    """Scrub through video until no template is matched"""
    frame_skip = frame_skip if frame_skip else interval*self.fps
    
    while self.template_check(templates, threshold, method):
      self.skip_frames(frame_skip)
      
    return self #chainable
