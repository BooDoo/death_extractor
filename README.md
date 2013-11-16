death_extractor
===============

Download youtube videos of Spelunky Daily Challenge, extract death to GIF, post GIF.  
Written in/for Python 2.7.5

Dependencies: 
-------------

ImageMagick, youtube-dl, ffmpeg, opencv (with ffmpeg support), pyimgur, pytumblr  

Usage:
------

 `imgur_secrets` and `tumblr_secrets` list environment variables which should be populated with your access information for these APIs
then run `daas.py` (_Deaths As A Service_)

How Does It Work?
-----------------

Search for YouTube videos (via REST) of "medium" length which match query "spelunky+daily+challenge".  
Maintain a queue of these video IDs, removing any we've already gotten.  
With a downloaded video as `cv2.VideoCapture` object:  
 - Go to 45s from the video's end
 - Scrub forward by 0.5s increments, checking for post-death UI elements
 - Skip back 7 seconds from the frame where we find post-death UI
 - Push 4 seconds at 6fps out to a temporary AVI container
 - Convert temp AVI to grayscale GIF with ImageMagick (usually 300~600K)
 - Upload resulting GIF to Imgur/Tumblr, with link to source video
 - Rinse. Repeat (periodically)

Why Do I Care?
--------------

Spelunky deaths are hilarious.  
GIF is the native language of the web at the moment.  
`CvVideo` is a useful, though limited, class for working with `cv2.VideoCapture` objects.

TODO:
------
 [x] Move secrets to environment variables (obviously)
 [x] Tumblr integration
 [ ] Map color palettes over grayscale? (e.g. cave/jungle/ice/temple/hell palettes)
 [ ] Add `last_called` to `CvVideo` to get more meaningful errors from `try:` around chained use
 [ ] `CvVideo.template_check()`: enable checking against `min_val` for methods where that's appropriate
 [ ] Read death level/cause/etc for Tumblr tag purposes
 [ ] Support setting parameters (e.g. intervals, imgur v. tumblr) via config/command line
 [ ] Nested options (e.g. crop region, color/gray GIF) configurable via config/command line
