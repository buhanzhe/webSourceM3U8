"""Fetch every playlist entry and retain reproducible, conservative audit evidence.
HTTP success is never treated as proof that a channel is selected or playable.
"""
import argparse, concurrent.futures, hashlib, html, json, os, re
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
CACHE = Path(os.environ.get('TEMP', '.')) / 'webview-channel-audit-20261022'

def fetch(url, refresh=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    meta, body = CACHE / (key+'.json'), CACHE / (key+'.html')
    if meta.exists() and not refresh:
        result=json.loads(meta.read_text(encoding='utf8'));result['cache_file']=str(body);return result
    parsed=urlsplit(url)
    encoded=urlunsplit((parsed.scheme, parsed.netloc,quote(parsed.path,safe='/%:@'),quote(parsed.query,safe='=&%/:?+,;@'),''))
    result={'url':url,'checked_at':'2026-10-22','http_status':None,'final_url':None}
    try:
        with urlopen(Request(encoded,headers={'User-Agent':UA}),timeout=10) as r:
            raw=r.read(1800000)
            charset=r.headers.get_content_charset() or ('gb18030' if re.search(b'charset=["\x27]?(?:gb2312|gbk|gb18030)',raw[:5000],re.I) else 'utf8')
            content=raw.decode(charset,errors='replace')
            result.update(http_status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type',''))
            body.write_text(content,encoding='utf8')
            title=re.search(r'<title[^>]*>(.*?)</title>',content,re.I|re.S)
            result['title']=html.unescape(re.sub('<[^>]+>','',title.group(1))).strip() if title else ''
            result['hls_manifest']=content.lstrip().startswith('#EXTM3U')
            result['player_markup']=bool(re.search(r'<(?:video|iframe)\b|ckplayer|videojs|TCPlayer|Aliplayer|jwplayer|DPlayer',content,re.I))
            result['selector_in_url']=bool(re.search(r'[?&#](?:pid|id|channelId|channelIndex|liveRoomNumber|station_id|tag|index|code|liveid)=|/liveTV/\d+|/tv/\d+|/tvChannelDetail/\d+',url,re.I))
            result['media_urls']=list(dict.fromkeys(html.unescape(x) for x in re.findall(r'https?://[^\s"\x27<>\\]+\.m3u8(?:\?[^\s"\x27<>\\]*)?',content)))[:30]
            result['body_sha256']=hashlib.sha256(content.encode()).hexdigest()
            result['bytes']=len(raw)
    except HTTPError as e:result.update(http_status=e.code,error=str(e),final_url=e.url)
    except Exception as e:result['error']=str(e)
    meta.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');result['cache_file']=str(body)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--playlist',default='webview.txt');parser.add_argument('--output',default='webview-audit-network.json');parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    entries=[];group=''
    for n,line in enumerate(Path(args.playlist).read_text(encoding='utf-8-sig').splitlines(),1):
        if not line.strip():continue
        if line.endswith(',#genre#'):group=line.split(',')[0];continue
        if ',' not in line:
            entries.append({'line':n,'group':group,'raw':line,'format_error':True});continue
        name,url=line.split(',',1);entries.append({'line':n,'group':group,'name':name,'source':url,'url':url.removeprefix('webview://')})
    results={}
    urls=list(dict.fromkeys(e['url'] for e in entries if 'url' in e))
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        futures={pool.submit(fetch,u,args.refresh):u for u in urls}
        for i,f in enumerate(concurrent.futures.as_completed(futures),1):
            results[futures[f]]=f.result()
            if i%50==0:print(f'Fetched {i}/{len(urls)}',flush=True)
    for e in entries:
        if 'url' in e:e['probe']=results[e['url']]
    Path(args.output).write_text(json.dumps({'date':'2026-10-22','scope':'All non-empty channel entries; network/player configuration evidence, not device playback certification','playlist_sha256':hashlib.sha256(Path(args.playlist).read_bytes()).hexdigest(),'entries':entries},ensure_ascii=False,indent=2),encoding='utf8')
    print('DONE',len(entries),'entries',dict(Counter(str(x.get('http_status')) for x in results.values())),flush=True)
if __name__=='__main__':main()
