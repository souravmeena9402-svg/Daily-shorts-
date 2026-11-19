"""Run on the owner's computer, not in Actions. No token files are written."""
import argparse, json, subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
p=argparse.ArgumentParser();p.add_argument('client',help='Downloaded Desktop OAuth client JSON');p.add_argument('repo',help='owner/repo');args=p.parse_args()
scopes=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.readonly']
f=InstalledAppFlow.from_client_secrets_file(args.client,scopes)
c=f.run_local_server(port=0,access_type='offline',prompt='consent');assert c.refresh_token,'No refresh token. Reauthorize with consent.'
a=build('youtube','v3',credentials=c).channels().list(part='id,snippet',mine=True).execute()['items'];assert len(a)==1,'Select one channel identity and try again.'
i=a[0]['id'];print('Channel:',a[0]['snippet']['title'],i,'  Repository:',args.repo)
if input('Type the channel ID to confirm: ').strip()!=i: raise SystemExit('Cancelled')
subprocess.run(['gh','secret','set','YT_AUTH','--repo',args.repo],input=c.to_json(),text=True,check=True)
subprocess.run(['gh','variable','set','CHANNEL_ID','--repo',args.repo,'--body',i],check=True);print('Connected. Scheduled upload is NOT enabled by this script.')
