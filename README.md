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
 - Rinse. Repeat (periodically)  

Why Do I Care?
--------------

Spelunky deaths are hilarious.  
GIF is the native language of Tumblr.  
`CvVideo` is a useful, though limited, class for working with `cv2.VideoCapture` objects.

TODO:
------
 [x] Move secrets to environment variables (obviously)  
 [x] Tumblr integration  
 [ ] Map color palettes over grayscale? (e.g. cave/jungle/ice/temple/hell palettes)  
 [ ] Add `last_called` to `CvVideo` to get more meaningful errors from `try:` around chained use?  
 [ ] `CvVideo.template_check()`: enable checking against `min_val` for methods where that's appropriate  
 [ ] Move project-specific features/defaults of `CvVideo` to sub-class  
 [X] Limit how far to scrub looking for template(s) [optional]  
 [X] Test `template_check()` with ROI v. without for efficiency purposes? -- No better.  
 [X] Read death level  
 [ ] Read money at time of death  
 [ ] Read which character  
 [ ] Enable download/processing at higher res (-f36 instead of -f18 in `yt.dl()`)  
 [ ] Support setting parameters (e.g. intervals, imgur v. tumblr) via config/command line  
 [ ] Nested options (e.g. crop region, color/gray GIF) configurable via config/command line  
 [ ] Refactor everything  
