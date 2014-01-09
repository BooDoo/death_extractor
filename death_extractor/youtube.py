import subprocess
import urllib2
import json
import os.path
import sys


def req_url(q, start_index=1, max_results=50, order_by='published',
            duration=None, v=2, alt='jsonc'):
    url = "https://gdata.youtube.com/feeds/api/videos?q=%s" % q
    if start_index:
        url += "&start-index=%i" % start_index
    if max_results:
        url += "&max-results=%i" % max_results
    if order_by:
        url += "&orderby=%s" % order_by
    if duration:
        url += "&duration=%s" % duration
    if v:
        url += "&v=%i" % v
    if alt:
        url += "&alt=%s" % alt

    return url


#Get new ids, merge with existing queue (uniques not already downloaded)
def populate_queue(queue_file='yt_queue', dl_log_file='yt_log'):
    try:
        queue = open(queue_file, 'r+')
    except IOError as e:
        sys.stdout.write("File " + queue_file + " doesn't exist? "
                         + e.message + "\nCreating...\n")
        sys.stdout.flush()
        queue = open(queue_file, 'w')
    old_ids = [line.rstrip() for line in queue]

    try:
        dl_log = [line.rstrip().split(' ')[1]
                  for line in open(dl_log_file, 'r')]
    except IndexError as e:
        sys.stdout.write("No records in " + dl_log_file + "? "
                         + e.message + "\n")
        sys.stdout.flush()
        dl_log = ['']
    yt_url = req_url("spelunky+daily+challenge")
    yt_request = urllib2.Request(yt_url)
    yt_result = json.load(urllib2.urlopen(yt_request))
    new_ids = [item.get('id')
               for item in yt_result.get('data').get('items')]

    new_queue = list(set(old_ids + new_ids) - set(dl_log))

    queue.seek(0)
    queue.write("\n".join(new_queue))
    queue.truncate()
    queue.close()

    return new_queue


def dl(max_downloads=5, dl_target=None, vid_format='18',
       vid_path='vids', output=None, queue_file='yt_queue',
       dl_log_file='yt_log', rate_limit="1.2M", threshold=6):
    vids = [file for file in os.listdir(vid_path)
            if not file.endswith('part') and not file.startswith('.')]
    if len(vids) < threshold:
        call_args = ['youtube-dl', '--restrict-filenames']
        if not output:
            output = os.path.join(vid_path,
                                  '%(uploader)s___%(id)s.%(ext)s')
        call_args.extend(['-o', output])

        if vid_format:
            call_args.extend(['-f', str(vid_format)])
        if dl_log_file:
            call_args.extend(['--download-archive', dl_log_file])
        if rate_limit:
            call_args.extend(['--rate-limit', rate_limit])
        if max_downloads:
            call_args.extend(['--max-downloads', str(max_downloads)])

        if queue_file:
            call_args.extend(['-a', queue_file])
        elif dl_target:
            call_args.append(dl_target)
        #Now call it:
        subprocess.call(call_args)

    else:
        print "Enough videos already! Skipping download this pass."
