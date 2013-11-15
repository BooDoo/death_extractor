import os, sys, subprocess
import cv2
import pyimgur
import imgur
import pytumblr
import youtube as yt
from RepeatedTimer import RepeatedTimer as set_interval
from templates import get_templates

#Assign some custom utility functions to pyimgur module:
pyimgur.init_with_refresh = imgur.imgur_init_with_refresh
pyimgur.Imgur.manual_auth = imgur.imgur_manual_auth
#USE ENVIRONMENT VARIABLES, YOU CHUMP!
CLIENT_ID, CLIENT_SECRET, ALBUM_ID, REFRESH_TOKEN = [line.rstrip() for line in open('imgur_secrets','r')]
imgur = pyimgur.init_with_refresh(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
imgur.refresh_access_token()

CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_SECRET, BLOG_NAME = [line.rstrip() for line in open('tumblr_secrets','r')]
tumblr = pytumblr.TumblrRestClient(
  CONSUMER_KEY,
  CONSUMER_SECRET,
  OAUTH_TOKEN,
  OAUTH_SECRET
)


def extract_death(vid, out_interval=0.16667, out_duration=4, use_roi=True, init_skip=45, quiet=False):
  """Search through a cv2.VideoCapture (using custom `CvVideo` class) for Spelunky death, write frames to GIF (via AVI)"""
  print "" #newline
  print vid.vid_id, vid.framecount, vid.fps, vid.fourcc, vid.width, vid.height, vid.aspect_ratio, "..."
  if not quiet:
    print "Using templates_[",["".join(str(n) for n in vid.aspect_ratio)],"]"
    print "Cropped dimensions (video):", vid.crop_width, vid.crop_height
    print "Cropped dimensions (frames):", vid._maxX - vid._minX, vid._maxY - vid._minY
  
  vid.set_frame(vid.framecount - 1).skip_back(init_skip)

  try:
    while vid.template_check():
      vid.skip_back(15) #frame, grayframe = skip_back(vid, 15)
  except cv2.error as e:
    print "\nSkipping",vid.input_file,"due to failed template_check (probably)\nmoving to problems/",vid.input_file_tail
    os.rename(vid.input_file, "problems/" + vid.input_file_tail)
    return e
    
  try:
    while vid.template_check() == False:
      vid.skip_forward(0.5)
  except cv2.error as e:
    print "\nSkipping",vid.input_file,"due to no from_frame found... (probably)\nmoving to problems/",vid.input_file_tail
    os.rename(vid.input_file, "problems/" + vid.input_file_tail)
    return e
  
  vid.skip_back(7) #Do we really want to skip back 7 and then only capture 4?

  print "" #newline
  if not quiet:
    print "'from_frame':", vid.frame, " at ", vid.time
  
  print "Making video from_frame->to_frame..."
  try:
    vid.clip_to_output(interval=out_interval, duration=out_duration, use_roi=use_roi).gif_from_temp_vid().clear_temp_vid()
  except cv2.error as e:
    print "\nSkipping",vid.input_file,"due to problem with temp_vid...\nmoving to problems/",vid.input_file_tail
    os.rename(vid.input_file, "problems/" + vid.input_file_tail)
    return e
  
  if not quiet:
    print "'to_frame':", vid.frame, " at ", vid.time

class CvVideo(object):
  #Constructor for the CvVideo object (requires OpenCV2 with ffmpeg support)
  def __init__(self, input_file, gif_path='gifs', temp_path='tmp', splitter='___', scale_width=0.6, scale_height=0.5):
    self.input_file = input_file
    self.input_file_tail = os.path.split(input_file)[1]
    self.uploader, self.vid_id = os.path.splitext(self.input_file_tail)[0].split(splitter)[0:2]
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
    #So "0" is device, but what is "7"?
    self.output = cv2.VideoWriter(self.temp_vid,0,7,(self.crop_width,self.crop_height))
    
    #For ROI/crop:
    self._minY, self._minX = [int( (self.height - self.crop_height) / 2), int( (self.width - self.crop_width) / 2)]
    self._maxY, self._maxX = [self._minY + self.crop_height, self._minX + self.crop_width]
    self.roi_rect= (self._minX, self._minY, self._maxX, self._maxY)
    
    #set approx. aspect ratio
    if self.width == 480:
      self.aspect_ratio = (4,3)
    elif self.width == 576:
      self.aspect_ratio = (8,5)
    else:
      self.aspect_ratio = (16,9)
    
    #and assign templates accordingly:
    self.template_key = ["".join(str(n) for n in self.aspect_ratio)]
    self.templates = get_templates(self.template_key)

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
    return self.__roi_rect
  
  @roi_rect.setter
  def roi_rect(self, rect):
    minX, minY, maxX, maxY = rect
    if minX < 0 or minY < 0 or maxX < 0 or maxY < 0 or maxX < minX or maxY < minY or maxX > self.width or maxY > self.height:
      raise cv2.error("Invalid dimensions for crop/ROI rectangle.")
    else:
      self.__roi_rect = (minX, minY, maxX, maxY)

  @property
  def roi(self):
    """Subset of pixels (ROI) from current frame"""
    if self.img == None:
      self.read()
    return self.img[self.roi_rect[1]:self.roi_rect[3], self.roi_rect[0]:self.roi_rect[2]]
  
  @roi.setter
  def roi(self, rect):
    self.roi_rect = rect

  @property
  def roi_gray(self):
    """Subset of pixels (ROI) from current frame, in grayscale"""
    if not self.gray:
      self.read()
    return self.gray[self.roi_rect[1]:self.roi_rect[3], self.roi_rect[0]:self.roi_rect[2]]
  
  #chainable alias for frame = ...
  def set_frame(self, frame=0):
    """A chainable alias for CvVideo.frame = `frame`"""
    self.frame = frame
    return self #chainable
  
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

  def frame_to_file(self, out_file='frame.png', color=True, frame=-1, use_roi=False):
    """Write current frame (or specified `frame`) to `out_file`, optionally in grayscale and/or cropped to `roi_rect`"""
    if frame >= 0: #Target specific frame?
      self.frame = frame
    self.read()
    
    if use_roi and not color:
      cv2.imwrite(out_file, self.roi_gray)
    elif use_roi and color:
      cv2.imwrite(out_file, self.roi)
    elif not color:
      cv2.imwrite(out_file, self.gray)
    else:
      cv2.imwrite(out_file, self.img)
    
    return self #chainable
  
  def frame_to_output(self, color=True, frame=-1, use_roi=False):
    """Write current frame (or specified `frame`) to `CvVide.output` buffer, optionally in grayscale and/or cropped to `roi_rect`"""
    if not self.output:
      raise cv2.error("No output stream for writing!")
    
    if frame >= 0: #Target specific frame?
      self.frame = frame
    self.read()
    
    #dump output frames
    #cv2.imwrite('dump/'+ self.vid_id + str(frame) + '.png', self.roi)

    if use_roi and not color:
      self.output.write(self.roi_gray)
    elif use_roi and color:
      self.output.write(self.roi)
    elif not color:
      self.output.write(self.gray)
    else:
      self.output.write(self.img)
  
    return self #chainable
  
  #interval is in seconds, can be negative.
  def clip_to_output(self, from_frame=-1, to_frame=-1, frame_skip=None, interval=None, duration=None, color=True, use_roi=False):
    """Take a clip of input `stream` and write to `output` buffer as series of frames"""
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
    
    #ensure ints
    from_frame = int(from_frame)
    to_frame = int(to_frame)
    frame_skip = int(frame_skip)
    
    #do it
    for frame in range(from_frame, to_frame, frame_skip):
      self.frame_to_output(color, frame, use_roi)
      
    return self #chainable
  
  def gif_from_temp_vid(self, color=False, out_file=None):
    """Call ImageMagick's `convert` from shell to create a GIF of video file found at `temp_vid`"""
    if not out_file:
        out_file = self.out_gif
    
    try:
      if os.path.getsize(self.temp_vid) < 6000:
        raise cv2.error("Didn't write any frames to AVI. Wrong crop-size? Wrong codec?")
    except os.error as e:
      raise cv2.error("Temp AVI doesn't exist!")

    print "Writing to", out_file, "..."
    
    if color:
      subprocess.call(['convert', self.temp_vid, '-delay', '20', '-fuzz', '4%', '-layers', 'OptimizeTransparency', '+map', out_file])
    else:
      subprocess.call(['convert', self.temp_vid, '-delay', '20', '-modulate', '130,0,100', '-fuzz', '4%', '-layers', 'OptimizeTransparency', '+map', out_file])
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

  def upload_gif_tumblr(self, tumblr, blog_name=None):
    blog_name = blog_name if blog_name else BLOG_NAME
    print "Attempting to upload",self.out_gif,"to",blog_name,"..."
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
  #TODO?: Enable next()/cb() style to make it chainable?
  #Or create wrapper functions? "until_template" / "unless_template"?
  def template_check(self, templates=None, threshold=0.84, method=cv2.TM_CCOEFF_NORMED):
    """Cycle through each image in `templates` and perform OpenCV `matchTemplate` until match found (or return False)"""
    #TODO: Enable checking against min_val for methods where that's more appropriate
    
    if templates == None and hasattr(self, 'templates'):
      templates = self.templates
    elif templates == None:
      raise cv2.error("No template(s) to match against!")
    
    for template in templates:
      res = cv2.matchTemplate(self.gray, template, method)
      min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
      if max_val >= threshold:
        return True
    
    return False

def extract_and_upload(vid_path = 'vids', out_interval=0.16667, out_duration=4, use_roi=True, init_skip=45, quiet=False, remove_source = True, to_imgur=False, to_tumblr=False):
  input_file = [file for file in os.listdir(vid_path) if not file.endswith('part')][0]
  try:
    vid = CvVideo(os.path.join(vid_path, input_file))
    extract_death(vid, out_interval, out_duration, use_roi, init_skip, quiet)
    if to_imgur:
      vid.upload_gif_imgur(imgur)
    if to_tumblr:
      vid.upload_gif_tumblr(tumblr)
    if remove_source:
      os.remove(os.path.join(vid_path, input_file))
  except (cv2.error, IOError, TypeError) as e:
    print e
    return e

if __name__ == '__main__':
  print "Sorry, I'm not made to work that way (yet...)"
