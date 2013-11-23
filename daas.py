import os
from death_extractor import youtube as yt
from death_extractor import set_interval
from death_extractor import extract_and_upload
    
def death_as_a_service(vid_path = 'vids', post_interval=3600*2, search_interval=3600*6, dl_interval=3600*3, max_downloads=4, to_imgur=True, to_tumblr=True):
  """Run periodic search/download/extract_and_upload operations"""
  print "Fetching new videos and consolidating queue..."
  yt.populate_queue()
  if len([file for file in os.listdir(vid_path) if not file.endswith('part') and not file.startswith('.')]) < 4:
    print "Downloading up to",max_downloads,"videos..."
    yt.dl(max_downloads)
  extract_and_upload(vid_path, to_imgur, to_tumblr)
  
  if search_interval:
    search_timer = set_interval(search_interval, yt.populate_queue)
  if dl_interval:
    dl_timer = set_interval(dl_interval, yt.dl, max_downloads)
  if post_interval:
    post_timer = set_interval(post_interval, extract_and_upload, vid_path, to_imgur, to_tumblr)
     
if __name__ == '__main__':
  print "Running from console..."
  death_as_a_service()
