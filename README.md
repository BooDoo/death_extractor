death_extractor
===============

Download youtube videos of Spelunky Daily Challenge, extract death to GIF, post GIF.  
Written in/for Python 2.7.5

Dependencies: 
-------------

ImageMagick, youtube-dl, ffmpeg, opencv (with ffmpeg support), pyimgur, pytumblr, pysnap (via submodule)  

Usage:
------

```
git clone ...  
cd death_extractor  
git submodule init --update  
```

 `imgur_secrets`, `tumblr_secrets` and `snapchat_secrets` list environment variables which should be populated with your access information for these 
APIs  
then run `daas.py` (_Deaths As A Service_)

How Does It Work?
-----------------

Search for YouTube videos which match query "spelunky+daily+challenge".  
Maintain a queue of these video IDs, removing any we've already gotten.  
With a downloaded video as `cv2.VideoCapture` object:  
 - Start at the last frame of the video  
 - Scrub back by ~1sec increments 
 - If giant chest found (winner) then move on. If the "skull" UI element is found:
 - Scrub forward by ~0.2s increments until skull is no longer visible  
 - Jump back ~3.75sec  
 - Push ~4 seconds at ~10fps out to a temporary AVI container  
 - Convert temp AVI to grayscale GIF with ImageMagick (usually 800K~1100K)  
 - Scrub back from point of death until sum of frame suggests "circular wipe" at stage start  
 - Move ahead a bit and look for world label (e.g. MINES, WORM, OLMEC'S LAIR)
 - If world has stages (e.g. MINES 1-2, TEMPLE 4-3) identify which of the stages this is
 - Upload resulting GIF to Imgur/Tumblr linking source video (at timestamp) and tagged with world/stage of death  
 - Optionally post a video (cropped, rotated and resized for mobile screen) to Snapchat friends
 - Rinse. Repeat (periodically)  

Why Do I Care?
--------------

Spelunky deaths are hilarious.  
GIF is the native language of Tumblr.  
[`CvVideo`](https://github.com/BooDoo/CvVideo) is a useful, though limited, class for working with `cv2.VideoCapture` objects.

TODO:
------
See GitHub repo's Issues page.
