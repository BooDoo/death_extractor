import os
import sys
import subprocess
import traceback
import imp
import time
import cv2
import pyimgur
import imgur as my_imgur
import pytumblr
import youtube as yt
import util
from CvVideo import CvVideo
from RepeatedTimer import RepeatedTimer as set_interval
from templates import get_templates
try:
    #Maybe someday pysnap will actually be in pypi?
    from pysnap import Snapchat
except ImportError as e:
    f, filename, desc =
    imp.find_module('pysnap',
                    ['./pysnap', './death_extractor/pysnap'])
    pysnap = imp.load_module('pysnap', f, filename, desc)
    Snapchat = pysnap.Snapchat
    #TEMP WORKAROUND:
last_snapchat = 0
last_tumblr = 0
last_imgur = 0

#Assign some custom utility functions to pyimgur module:
pyimgur.init_with_refresh = my_imgur.imgur_init_with_refresh
pyimgur.Imgur.manual_auth = my_imgur.imgur_manual_auth

IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET,
IMGUR_ALBUM_ID, IMGUR_REFRESH_TOKEN =
[os.getenv(line.rstrip()) for line in open('imgur_secrets', 'r')]

TUMBLR_CONSUMER_KEY, TUMBLR_CONSUMER_SECRET,
TUMBLR_OAUTH_TOKEN, TUMBLR_OAUTH_SECRET, TUMBLR_BLOG_NAME =
[os.getenv(line.rstrip()) for line in open('tumblr_secrets', 'r')]

SNAPCHAT_USER, SNAPCHAT_PASS =
[os.getenv(line.rstrip()) for line in open('snapchat_secrets', 'r')]

try:
    imgur = pyimgur.init_with_refresh(
        IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_REFRESH_TOKEN)
    imgur.refresh_access_token()

    tumblr = pytumblr.TumblrRestClient(
        TUMBLR_CONSUMER_KEY,
        TUMBLR_CONSUMER_SECRET,
        TUMBLR_OAUTH_TOKEN,
        TUMBLR_OAUTH_SECRET
    )

    snapchat = Snapchat()
    snapchat.login(SNAPCHAT_USER, SNAPCHAT_PASS)

except pyimgur.requests.exceptions.ConnectionError as e:
    imgur = None
    tumblr = None
    snapchat = None
    print "No internet?"


class SpelunkyVideo(CvVideo):
    def __init__(self, input_file,
                 gif_path='gifs', temp_path='tmp', splitter='___',
                 crop_factor=(0.6, 0.45), crop_width=None, crop_height=None,
                 from_youtube=True, avi_codec=0, avi_fps=7):
        super(SpelunkyVideo, self)
        .__init__(input_file, gif_path=gif_path, splitter=splitter,
                  crop_factor=crop_factor, crop_width=crop_width,
                  crop_height=crop_height, from_youtube=from_youtube,
                  avi_codec=avi_codec, avi_fps=avi_fps)
        self.tumblr_tags = ["spelunky", "daily challenge", "death", "gif",
                            "book of the dead", self.uploader.replace("_", "")]
        self.death_frame = None
        self.gif_start = None


def upload_gif_imgur(vid, imgur=imgur, album='T6X43',
                     description=None, link_timestamp=True):
    """
    Upload file at location `vid.out_gif` to Imgur
    with a description linking to original YouTube source
    """
    if link_timestamp:
        vid_link = vid.vid_link + "&t=%is" % (vid.clip_start or 0)
    if description is None:
        description = "Watch full: " + vid_link

    imgur.refresh_access_token()
    uploaded_image =
    imgur.upload_image(vid.out_gif, title=vid.vid_id,
                       album=album, description=description)
    sys.stdout.write("Uploaded to: " + uploaded_image.link + "\n")
    sys.stdout.flush()
    return uploaded_image.link


def upload_gif_tumblr(vid, tumblr=tumblr, blog_name=None,
                      link_timestamp=True, tags=None):
    blog_name = blog_name if blog_name else os.getenv('TUMBLR_BLOG_NAME')
    if tags is None:
        tags = vid.tumblr_tags
    if link_timestamp:
        vid_link = vid.vid_link + "&t=%is" % (vid.clip_start or 0)

    if os.path.getsize(vid.out_gif) > 1010000:
        sys.stdout.write("Output GIF is too large. Using frame_skip 5...\n")
        sys.stdout.flush
        vid.reset_output().read_frame(vid.gif_start)
        vid.clip_to_output(frame_skip=5, duration=4, use_roi=True)
        vid.gif_from_out_avi(color=False, delay=10)

    sys.stdout.write("Uploading "+vid.out_gif+" to "+blog_name+"...")
    sys.stdout.flush()
    upload_response = tumblr.create_photo(
        blog_name,
        data=vid.out_gif,
        #caption="Watch full: "+vid.vid_link,
        slug=vid.vid_id,
        link=vid_link,
        tags=tags
    )
    sys.stdout.write("%s.\n\n" % upload_response)
    sys.stdout.flush()
    return upload_response


def send_snapchat(vid, snapchat=snapchat, recipients=None, duration=6):
    if recipients is None:
        #recipients = snapchat.username
        recipients = [friend['name'] for friend in snapchat.get_friends()]

    if type(recipients) == list:
        recipients = ", ".join(recipients)

    vid.clip_to_mp4(from_frame=vid.gif_start-30, duration=6, transpose=1,
                    scale_height=360, crop="out_w=in_w*.5:out_h=in_h*.5")
    media_id = snapchat.upload(vid.out_mp4)
    return snapchat.send(media_id, recipients, time=6)


def snapchat_followback(snapchat=snapchat):
    updates = snapchat.get_updates()
    recent_friends = [user['name'] for user in updates.get('requests')]
    recent_friends.extend(
        [user['name'] for user in updates.get('added_friends')]
    )
    old_friends = [user['name'] for user in snapchat.get_friends()]
    new_friends = set(recent_friends).difference(set(old_friends))
    if len(new_friends):
        results = [snapchat.add_friend(name) for name in new_friends]
        sys.stdout.write("SNAPCHAT: " + str(results.count(True)) +
                         " of " + str(len(results)) + " new friends added\n")
        sys.stdout.flush()
        return all(results)

    sys.stdout.write("SNAPCHAT: No new friends.")
    sys.stdout.flush()
    return True


def extract_death(vid, out_frame_skip=3, out_duration=4, use_roi=True,
                  gif_color=False, gif_delay=None, quiet=False):
    """
    Search through a video for Spelunky death, make GIF (via temp AVI)
    """
    print ""
    print vid.vid_id, vid.framecount, vid.fps, vid.fourcc, vid.width,
    vid.height,
    "%i:%i" % (vid.aspect_ratio.numerator, vid.aspect_ratio.denominator), "..."

    if gif_delay < 0:
        gif_delay = int(round(100.0 / (vid.fps / out_frame_skip)))

    if not quiet:
        print "ROI/Cropped dimensions:", vid.crop_width, vid.crop_height

    #Start at last frame, step back 1s at a time looking for skull UI element
    #Scrub forward by ~0.2s increment until skull is gone
    #Back 3.85 sec, then export `out_duration`@`vid.fps`/`out_frame_skip` fps
    #Call ImageMagick convert on for grayscale GIF, then remove temp AVI
    #TODO: Store 'last' called in CvVideo for more meaningful err in chain

    #new template finding logic: UI skull-based, more tightly targeted
    vid.read_frame(vid.framecount - 1)
    vid.template_until(-1, templates=vid.templates[-3:])
    if vid.template_found == "skull":
        vid.template_while(frame_skip=6, templates=vid.templates[-3:],
                           max_length=300)
        vid.death_frame = vid.frame
        vid.skip_back(3.75)
        vid.gif_start = vid.frame
        vid.clip_to_output(frame_skip=out_frame_skip,
                           duration=out_duration, use_roi=use_roi)
        vid.gif_from_out_avi(color=gif_color, delay=gif_delay)
        vid.clear_out_avi()
    else:
        sys.stdout.write("I guess they won? "+vid.template_found+"\n\n")
        sys.stdout.flush()
        raise IOError("No death to extract!")

    #Find stage of death
    #NOTE: Using ROI in template_check did not noticably improve speed.
    #Scrub back for the "circle wipe" signaling a new stage,
    #Scrub ahead for the stage label (MINES, JUNGLE, MOTHERSHIP, et c.)
    #If numbered world, run second check for if -1, -2, -3 or -4
    vid.skip_back(out_duration)
    init_sum, init_frame = vid.gray.sum(), vid.frame
    while (vid.gray.sum() > min((init_sum / 4.0), 2500000)
           and vid.frame > (init_frame - 5*60*30)):
        vid.skip_frames(-20)
    vid.skip_frames(60)
    if vid.template_until(frame_skip=10, templates=vid.templates[4:-3],
                          max_length=3):
        vid.tumblr_tags.append(vid.template_found)
        worlds = {"Mines": 1, "Jungle": 2, "Ice Caves": 3,
                  "Temple": 4, "Hell": 5}
        #ALTERNATE?: # dict((t[0], i+1) for i,t in enumerate(templates[4:9]))
        if vid.template_found in worlds.keys():
            level_key = "%i" % worlds[vid.template_found]
            if vid.template_best(templates=vid.templates[:4]):
                level_key += vid.template_found
                vid.tumblr_tags.append(level_key)
        else:
            level_key = vid.template_found
        sys.stdout.write("\nDeath level was: "+level_key+"\n")
        sys.stdout.flush()


#TODO: Clean up these rat's nests of arguments!
def extract_and_upload(vid_path='vids', out_frame_skip=3, out_duration=4,
                       use_roi=True, gif_color=False, gif_delay=8, quiet=False,
                       remove_source=True, to_imgur=False, to_tumblr=False,
                       to_snapchat=False):
    input_file = [file for file in os.listdir(vid_path)
                  if not file.endswith('part')
                  and not file.startswith('.')][0]
    #TEMP WORKAROUND:
    global last_snapchat
    global last_tumblr
    global last_imgur
    try:
        vid = SpelunkyVideo(os.path.join(vid_path, input_file))
        vid.templates = get_templates(vid.template_scale)
        extract_death(vid, out_frame_skip=out_frame_skip,
                      out_duration=out_duration, use_roi=use_roi,
                      gif_color=gif_color, gif_delay=gif_delay, quiet=quiet)
        if to_imgur and time.time() - last_imgur > 0:
            upload_gif_imgur(vid)
            last_imgur = time.time()
        if to_tumblr and time.time() - last_tumblr > 0:
            upload_gif_tumblr(vid)
            last_tumblr = time.time()
        if to_snapchat and time.time() - last_snapchat >= 60*60*8:
            snapchat.login(SNAPCHAT_USER, SNAPCHAT_PASS)
            snapchat_followback()
            send_snapchat(vid)
            last_snapchat = time.time()
            os.remove(vid.out_mp4)
        if remove_source:
            os.remove(os.path.join(vid_path, input_file))
    except (cv2.error, OSError, IOError, TypeError, AttributeError) as e:
        print e
        print "\nSkipping", vid.input_file, "likely due to failure to extract"
        print "moving to problems/", vid.input_file_tail
        os.rename(vid.input_file, "problems/" + vid.input_file_tail)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=None, file=sys.stderr)
        sys.stderr.flush()
        util.recall(extract_and_upload)
        # ^^^ limit how many retries?

if __name__ == '__main__':
    print "Sorry, I'm not made to work that way (yet...)"
