import os
from death_extractor import youtube as yt
from death_extractor import set_interval
from death_extractor import extract_and_upload


def death_as_a_service(vid_path='vids', max_downloads=4,
                       to_imgur=False, to_tumblr=True, to_snapchat=True):
    """Run periodic search/download/extract_and_upload operations"""
    print "Fetching new videos and consolidating queue..."
    yt.populate_queue()
    yt.dl(max_downloads)
    extract_and_upload(vid_path, to_imgur=to_imgur,
                       to_tumblr=to_tumblr, to_snapchat=to_snapchat)

if __name__ == '__main__':
    print "Running from console..."
    death_as_a_service()
    post_timer = set_interval(3600*2, death_as_a_service)
