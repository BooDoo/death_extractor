import subprocess, urllib2, json, os.path

def req_url(q='spelunky+daily+challenge', start_index=1, max_results=50, orderby='published', duration='medium', v=2, alt='jsonc'):
  return 'https://gdata.youtube.com/feeds/api/videos?q=%s&start-index=%i&max-results=%i&orderby=%s&duration=%s&v=%i&alt=%s' % (q, start_index, max_results, orderby, duration, v, alt)

#Get new ids and merge with existing queue (uniques, not already downloaded)
def populate_queue(queueFile='vidIds', dl_log_file='alreadyhadem'):
  queue = open(queueFile, 'r+')
  dl_log = [line.rstrip().split(' ')[1] for line in open(dl_log_file, 'r')]
  old_ids = [line.rstrip() for line in queue]
  
  yt_result = json.load(urllib2.urlopen(urllib2.Request(req_url())))
  new_ids = [item.get('id') for item in yt_result.get('data').get('items')]

  new_queue = list(set(old_ids + new_ids) - set(dl_log))

  queue.seek(0)
  queue.write("\n".join(new_queue))
  queue.truncate()
  queue.close()
  
  return new_queue

def dl(max_downloads=5, vid_path='vids', queue_file='vidIds', dl_log_file='alreadyhadem', rate_limit="1.2M", threshold=6):
  if len([file for file in os.listdir(vid_path) if not file.endswith('part') and not file.startswith('.')]) < threshold:
    subprocess.call(['youtube-dl', '--restrict-filenames', '-f18', '-o', os.path.join(vid_path, '%(uploader)s___%(id)s.%(ext)s'), '--download-archive', dl_log_file, '--rate-limit', rate_limit, '--max-downloads', str(max_downloads), '-a', queue_file])
  else:
    print "Enough videos already! Skipping download this pass."
