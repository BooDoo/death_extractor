death_extractor
===============

Download youtube videos of Spelunky Daily Challenge, extract death to GIF, post GIF.  
Written in/for Python 2.7.5

Dependencies: 
-------------

ImageMagick, youtube-dl, ffmpeg, opencv (with ffmpeg support), pyimgur  

Usage:
------

`imgur_secrets` should be populated with (1 per line): `client_id`, `client_secret`, `album_id`, `refresh_token`  
then run `daas.py` (_Deaths As A Service_)

How Does It Work?
-----------------

Search for YouTube videos (via REST) of "medium" length which match query "spelunky+daily+challenge".  
Maintain a queue of these video IDs, removing any we've already gotten.  
With a downloaded video as `cv2.VideoCapture` object:  
 - Go to 45s from the video's end
 - Scrub forward by 0.5s increments, check each for the "Game Over" UI element
 - Skip back 7 seconds from the frame where we find "Game Over"
 - Push 4 seconds at 6fps out to a temporary AVI container
 - Convert the temporary AVI to a grayscale GIF with ImageMagick (usually 300~600K)
 - Upload the resulting GIF into a gallery at Imgur, including a link to original YouTube video
 - Rinse. Repeat.

Why Do I Care?
--------------

Spelunky deaths are hilarious.  
GIF is the native language of the web at the moment.  
`CvVideo` is a useful, though limited, higher-level class for working with `cv2.VideoCapture` objects.

TODO:
------
 - Move secrets to environment variables (obviously)
 - Tumblr integration
 - Support setting parameters (e.g. intervals, imgur v. tumblr) via config/command line
 - Nested options (e.g. crop region, color/gray GIF) configurable via config/command line
