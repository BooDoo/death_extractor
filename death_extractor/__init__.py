import os, sys, subprocess
import cv2
import pyimgur
import imgur
import pytumblr
import youtube as yt
import util
from CvVideo import CvVideo
from RepeatedTimer import RepeatedTimer as set_interval

#Assign some custom utility functions to pyimgur module:
pyimgur.init_with_refresh = imgur.imgur_init_with_refresh
pyimgur.Imgur.manual_auth = imgur.imgur_manual_auth

IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_ALBUM_ID, IMGUR_REFRESH_TOKEN = [os.getenv(line.rstrip()) for line in open('imgur_secrets','r')]
TUMBLR_CONSUMER_KEY, TUMBLR_CONSUMER_SECRET, TUMBLR_OAUTH_TOKEN, TUMBLR_OAUTH_SECRET, TUMBLR_BLOG_NAME = [os.getenv(line.rstrip()) for line in open('tumblr_secrets','r')]
try:
  imgur = pyimgur.init_with_refresh(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_REFRESH_TOKEN)
  imgur.refresh_access_token()

  tumblr = pytumblr.TumblrRestClient(
    TUMBLR_CONSUMER_KEY,
    TUMBLR_CONSUMER_SECRET,
    TUMBLR_OAUTH_TOKEN,
    TUMBLR_OAUTH_SECRET
  )
except pyimgur.requests.exceptions.ConnectionError as e:
  print "No internet?"

def extract_death(vid, out_frame_skip=3, out_duration=4, use_roi=True, gif_color=False, gif_delay=None, quiet=False):
  """Search through a cv2.VideoCapture (using custom `CvVideo` class) for Spelunky death, write frames to GIF (via AVI)"""
  print "" #newline
  print vid.vid_id, vid.framecount, vid.fps, vid.fourcc, vid.width, vid.height, vid.aspect_ratio, "..."

  if gif_delay < 0:
    gif_delay = int(round(100.0 / (vid.fps / out_frame_skip)))

  if not quiet:
    print "Using templates_[",["".join(str(n) for n in vid.aspect_ratio)],"]"
    print "Cropped dimensions (video):", vid.crop_width, vid.crop_height
    print "Cropped dimensions (frames):", vid._maxX - vid._minX, vid._maxY - vid._minY
  
  #Start at last frame, step back 1s at a time looking for skull UI element
  #Scrub forward by ~0.2s increment until skull is gone
  #Go back 3.85 seconds, then export `out_duration` at `vid.fps`/`out_frame_skip` fps
  #Call ImageMagick convert on for grayscale GIF, then remove temp AVI
  #TODO: Store 'last' called in CvVideo for more meaningful err in chain

  #new template finding logic: UI skull-based, more tightly targeted
  vid.read_frame(vid.framecount - 1)
  vid.until_template(-1, templates=vid.templates[-3:])
  if vid.template_found=="skull":
    vid.while_template(frame_skip=6, templates=vid.templates[-3:])
    vid.skip_back(3.75)
    vid.clip_to_output(frame_skip=out_frame_skip, duration=out_duration, use_roi=use_roi)
    vid.gif_from_temp_vid(color=gif_color,delay=gif_delay)
    vid.clear_temp_vid()
  else:
    sys.stdout.write("I guess they won?"+vid.template_found+"\n\n")
    sys.stdout.flush()
    raise IOError("No death to extract!")
    
  #Find stage of death
  #NOTE: Using ROI in template_check did not noticably improve speed.
  #Scrub back for the "circle wipe" signaling a new stage,
  #Scrub ahead for the stage label (MINES, JUNGLE, MOTHERSHIP, et c.)
  #If numbered world, run second check for if -1, -2, -3 or -4
  vid.skip_back(out_duration)
  while vid.gray.sum() > 2500000:
    vid.skip_frames(-20)
  vid.skip_frames(60)
  #vid.frame_to_file("dump/%s_%i.png" % (vid.vid_id, vid.frame))
  vid.until_template(frame_skip=10, templates=vid.templates[4:-3])
  vid.tumblr_tags.append(vid.template_found)
  worlds = {"Mines": 1, "Jungle": 2, "Ice Caves": 3, "Temple": 4, "Hell": 5} # dict( (t[0], i+1) for i,t in enumerate(templates[4:9]) )
  if vid.template_found in worlds.keys():
    level_key = "%i" % worlds[vid.template_found]
    if vid.template_best(templates=vid.templates[:4]):
      level_key += vid.template_found
      vid.tumblr_tags.append(level_key)
  sys.stdout.write("\nDeath level was:"+level_key+"\n")
  sys.stdout.flush()

#TODO: Clean up these rat's nests of arguments!
def extract_and_upload(vid_path = 'vids', out_frame_skip=3, out_duration=4, use_roi=True, gif_color=False, gif_delay=8, quiet=False, remove_source=True, to_imgur=False, to_tumblr=False):
  input_file = [file for file in os.listdir(vid_path) if not file.endswith('part') and not file.startswith('.')][0]
  try:
    vid = CvVideo(os.path.join(vid_path, input_file))
    extract_death(vid, out_frame_skip=out_frame_skip, out_duration=out_duration, use_roi=use_roi, gif_color=gif_color, gif_delay=gif_delay, quiet=quiet)
    if to_imgur:
      vid.upload_gif_imgur(imgur)
    if to_tumblr:
      vid.upload_gif_tumblr(tumblr)
    if remove_source:
      os.remove(os.path.join(vid_path, input_file))
  except (cv2.error, OSError, IOError, TypeError, AttributeError) as e:
    print e
    print "\nSkipping",vid.input_file,"due to failure to extract (probably)\nmoving to problems/",vid.input_file_tail
    os.rename(vid.input_file, "problems/" + vid.input_file_tail)
    util.recall(extract_and_upload)

if __name__ == '__main__':
  print "Sorry, I'm not made to work that way (yet...)"
