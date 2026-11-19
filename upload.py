import os,sys,json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
s=Path('state.json');state=json.loads(s.read_text());cfg=json.loads(Path('studio.json').read_text());meta=json.loads(Path('output/meta.json').read_text());day=datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
if cfg['privacy'] not in ('private','unlisted','public') or type(cfg['made_for_kids']) is not bool:raise SystemExit('Choose privacy and made_for_kids in studio.json first')
c=Credentials.from_authorized_user_info(json.loads(os.environ['YT_AUTH']));yt=build('youtube','v3',credentials=c);channels=yt.channels().list(mine=True,part='id').execute().get('items',[])
if [x['id'] for x in channels]!=[os.environ['CHANNEL_ID']]:raise SystemExit('Wrong channel. No upload.')
if meta['episode']!=state['next']:raise SystemExit('Episode mismatch')
if sys.argv[1]=='reserve':
    if state['pending'] or state['last_day']==day:raise SystemExit('Already attempted or uploaded. Inspect state.json.')
    state['pending']={'episode':state['next'],'day':day,'title':meta['title']}
elif sys.argv[1]=='upload':
    if not state['pending'] or state['pending']['episode']!=meta['episode']:raise SystemExit('No matching reservation')
    req=yt.videos().insert(part='snippet,status',notifySubscribers=False,body={'snippet':{'title':meta['title'],'description':meta['description'],'categoryId':'27','defaultLanguage':'en','defaultAudioLanguage':'en'},'status':{'privacyStatus':cfg['privacy'],'selfDeclaredMadeForKids':cfg['made_for_kids']}},media_body=MediaFileUpload('output/short.mp4',mimetype='video/mp4',chunksize=4*1024*1024,resumable=True));result=None
    while result is None:_,result=req.next_chunk(num_retries=3)
    state.update(next=state['next']+1,pending=None,last_day=day,last_video=result['id']);print('Uploaded: https://youtu.be/'+result['id']+' ; returned visibility: '+result.get('status',{}).get('privacyStatus','unknown'))
else:raise SystemExit('Unknown operation')
s.write_text(json.dumps(state,indent=2)+'\n')
