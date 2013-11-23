import os, sys, subprocess
import cv2
import pyimgur
import imgur
import pytumblr
import youtube as yt
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

def extract_death(vid, out_interval=0.16667, out_duration=4, use_roi=True, init_skip=45, quiet=False):
  """Search through a cv2.VideoCapture (using custom `CvVideo` class) for Spelunky death, write frames to GIF (via AVI)"""
  print "" #newline
  print vid.vid_id, vid.framecount, vid.fps, vid.fourcc, vid.width, vid.height, vid.aspect_ratio, "..."
  if not quiet:
    print "Using templates_[",["".join(str(n) for n in vid.aspect_ratio)],"]"
    print "Cropped dimensions (video):", vid.crop_width, vid.crop_height
    print "Cropped dimensions (frames):", vid._maxX - vid._minX, vid._maxY - vid._minY
  
  #Go `init_skip` sec from end, then by 15 sec until no template match
  #Scrub forward by 0.5s increment until "Game Over" template is found
  #Go back 6 seconds, then export `out_duration` at 1/`out_interval` fps
  #Call ImageMagick convert on for grayscale GIF, then remove temp AVI
  #TODO: Store 'last' called in CvVideo for more meaningful err in chain
  try:
    """
    #old logic checking against gameover text, leaderboard text, and vine background element from unpopulate leaderboard
    vid.set_frame(vid.framecount - 1).skip_back(init_skip) #.frame_to_file('dump/'+vid.vid_id+'/initskip-'+str(int(vid.frame))+'.png')
    vid.while_template(-15) #.frame_to_file('dump/'+vid.vid_id+'/notemplate-'+str(int(vid.frame))+'.png')
    vid.skip_back().while_template(-2) #.frame_to_file('dump/'+vid.vid_id+'/notemplate2'+str(int(vid.frame))+'.png')
    vid.until_template(0.5) #.frame_to_file('dump/'+vid.vid_id+'/gofound-'+str(int(vid.frame))+'.png')
    vid.skip_back(6).clip_to_output(interval=out_interval, duration=out_duration, use_roi=use_roi).gif_from_temp_vid().clear_temp_vid()
    """
    #new template finding logic: UI skull-based, more tightly targeted
    vid.set_frame(vid.framecount - 1).read()
    vid.until_template(-1, templates=vid.templates[-1:])
    vid.while_template(frame_skip=6, templates=vid.templates[-1:])
    vid.skip_back(3.85).clip_to_output(frame_skip=5, duration=4, use_roi=True).gif_from_temp_vid().clear_temp_vid()

  except cv2.error as e:
    print "\nSkipping",vid.input_file,"due to failure to extract (probably)\nmoving to problems/",vid.input_file_tail
    os.rename(vid.input_file, "problems/" + vid.input_file_tail)

def extract_and_upload(vid_path = 'vids', out_interval=0.16667, out_duration=4, use_roi=True, init_skip=45, quiet=False, remove_source = True, to_imgur=False, to_tumblr=False):
  input_file = [file for file in os.listdir(vid_path) if not file.endswith('part') and not file.startswith('.')][0]
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
    #if at first you don't succeed...
    return extract_and_upload(vid_path, out_interval, out_duration, use_roi, init_skip, quiet, remove_source, to_imgur, to_tumblr)

if __name__ == '__main__':
  print "Sorry, I'm not made to work that way (yet...)"
