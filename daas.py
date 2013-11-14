"""
TODO:
  - Test timers, then GO!
  - Set up git repo with .gitignore to keep out binaries and imgur_secrets, alreadyhadem, queue
  ? Make a Tumblr/Integrate post to Tumblr
  X Make gallery available directly at http://img.whistlingfish.org/spelunky/
  X Develop custom color palettes to lay over the greyscale (e.g. cave/jungle/ice/temple/hell palettes. or less specific?)
"""

from death_extractor import youtube as yt
from death_extractor import set_interval
from death_extractor import extract_and_imgur
    
def death_as_a_service(vid_path = 'vids', post_interval=3600*2, search_interval=3600*12, dl_interval=3600*6, max_downloads=5):
  """Run periodic search/download/extract_and_upload operations"""
  print "Fetching new videos and consolidating queue..."
  yt.populate_queue()
  print "Downloading up to",max_downloads,"videos..."
  yt.dl(max_downloads)
  extract_and_imgur(vid_path)
  
  if search_interval:
    search_timer = set_interval(search_interval, yt.populate_queue)
  if dl_interval:
    dl_timer = set_interval(dl_interval, yt.dl, max_downloads)
  if post_interval:
    post_timer = set_interval(post_interval, extract_and_imgur, vid_path)
     
if __name__ == '__main__':
  print "Running from console..."
  death_as_a_service()
