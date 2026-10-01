import urllib.request,json,time,urllib.error,os
import pathlib; S=str(pathlib.Path(__file__).resolve().parent.parent/'data')
H={'User-Agent':'gorillaz-graph/0.1 (stef.gugler@gmail.com)'}
def get(u):
    for i in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=90))
        except urllib.error.HTTPError as e:
            if e.code==404: return None
            time.sleep(3+i*3)
        except Exception: time.sleep(3+i*3)
    return None
GID='e21857d5-3256-4547-afb3-4b6ded592596'
recs=json.load(open(S+'/recordings.json'))
ids={}
for r in recs:
    for ac in r['artist-credit']:
        if isinstance(ac,dict) and ac['artist']['id']!=GID: ids[ac['artist']['id']]=ac['artist']['name']
# Gorillaz members (real people behind it) are relevant too
ids['ba550d0e-adac-4864-b88b-407cab5e76af']='Damon Albarn'
out=json.load(open(S+'/artists.json')) if os.path.exists(S+'/artists.json') else {}
log=open(S+'/fetch.log','a')
for n,(aid,name) in enumerate(ids.items()):
    if aid in out and out[aid].get('done'): continue
    a=get(f'https://musicbrainz.org/ws/2/artist/{aid}?inc=artist-rels+url-rels+tags&fmt=json'); time.sleep(1.1)
    if not a: continue
    rec_ids=set(); co={}; titles={}
    off=0; total=None
    while off<1000:
        d=get(f'https://musicbrainz.org/ws/2/recording?artist={aid}&inc=artist-credits&limit=100&offset={off}&fmt=json'); time.sleep(1.1)
        if not d: break
        total=d['recording-count']
        for r in d['recordings']:
            for ac in r['artist-credit']:
                if isinstance(ac,dict) and ac['artist']['id'] not in (aid,):
                    co.setdefault(ac['artist']['id'],{'name':ac['artist']['name'],'titles':[]})
                    if len(co[ac['artist']['id']]['titles'])<8 and r['title'] not in co[ac['artist']['id']]['titles']: co[ac['artist']['id']]['titles'].append(r['title'])
        off+=100
        if off>=total: break
    out[aid]={'name':a['name'],'sort':a.get('sort-name'),'type':a.get('type'),'country':a.get('country'),'area':(a.get('area') or {}).get('name'),
              'begin':(a.get('life-span') or {}).get('begin'),'disambiguation':a.get('disambiguation'),
              'tags':sorted([t['name'] for t in a.get('tags',[]) if t.get('count',0)>0],key=lambda x:-next(t['count'] for t in a['tags'] if t['name']==x))[:6],
              'wikidata':next((u['url']['resource'] for u in a.get('relations',[]) if u.get('type')=='wikidata'),None),
              'wikipedia':next((u['url']['resource'] for u in a.get('relations',[]) if u.get('type')=='wikipedia'),None),
              'rels':[{'type':r['type'],'id':r['artist']['id'],'name':r['artist']['name'],'dir':r.get('direction')} for r in a.get('relations',[]) if r.get('target-type')=='artist'],
              'recordings_total':total,'co':co,'done':True}
    json.dump(out,open(S+'/artists.json','w'),ensure_ascii=False)
    log.write(f'{n} {name} total={total} co={len(co)}\n'); log.flush()
log.write('ALL DONE\n'); log.close()
