#!/usr/bin/env python3
"""Regression checks for the bounded Naxxramas Korean history audit."""
from pathlib import Path
from datetime import date, timedelta
import copy, hashlib, importlib.util, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text())
spec=importlib.util.spec_from_file_location('api_builder',ROOT/'tools/wrapper_api_reference.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
fixture=load('tools/naxx-original-current.json')
original={c['id']:c for c in fixture['cards']}
current={c['id']:c for c in load('cards.json')['cards']}
render={c['id']:c for c in load('render.json')['cards']}
legacy=load('history.json')['cards']
policy=load('release-policy.json')
audit=load('tools/naxx-release-audit.json')
sources=load('tools/naxx-audit-sources.json')['events']
observations=load('tools/naxx-client-observations.json')['cards']
from date_schema import compatibility_card, read_card
# Raw evidence stays immutable; gameplay assertions are fed by canonical date maps.
docs={}
for p in (ROOT/'data').glob('*.json'):
    timeline, meta = read_card(ROOT, p.stem)
    doc = copy.deepcopy(meta['originalSource'])
    doc['card'] = compatibility_card(ROOT, p.stem)
    docs[p.stem] = doc
assert len(docs)==35 and set(docs)==set(current)==set(render)==set(original)
assert sum(c['collectible'] for c in current.values())==30
assert {c['dbfId'] for c in current.values()}=={c['dbfId'] for c in original.values()}
for p in ROOT.rglob('*.json'):json.loads(p.read_text())

def norm(text):
 return re.sub(r'<br\s*/?>\s*(?:</br\s*>)?|</br\s*>|\\r\\n|\\n|/n|\r\n|[\r\n]','<br></br>',text,flags=re.I)
def clean_display(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k in ('nativeTags','nativeRawText'):continue
   if k in ('text','flavor','name') and isinstance(v,str):
    assert norm(v)==v,(k,v)
   else:clean_display(v)
 elif isinstance(obj,list):
  for v in obj:clean_display(v)

def forward(c,day):
 if day<c['releasedAt']:return None
 state={k:copy.deepcopy(c[k]) for k in builder.SPEC_FIELDS if k in c}
 state['legacyArt']=c.get('legacyArt',False)
 for p in c['patches']:
  if p['date']<=day:state.update(p['changes'])
 return state

def reverse(c,day):
 if day<c['releasedAt']:return None
 state={k:copy.deepcopy(c[k]) for k in builder.SPEC_FIELDS if k in c}
 state['legacyArt']=c.get('legacyArt',False)
 matches=[]
 for h in c.get('history',[]):
  if ('from' not in h or h['from']<=day) and ('before' not in h or day<h['before']):matches.append(h)
 assert len(matches)<=1,(c['id'],day,matches)
 for h in matches:state.update(h['changes'])
 return state

release_cards=[]
for key,event in sources.items():
 if key.startswith('release-wing'):
  for cid in event['cards']:
   release_cards.append(cid)
   assert docs[cid]['card']['releasedAt']==event['date']
assert len(release_cards)==35 and len(set(release_cards))==35
checks=0
for cid,doc in docs.items():
 c=doc['card'];assert doc['schemaVersion']==2 and 'history' not in c
 assert c['dbfId']==current[cid]['dbfId']
 assert c['releasedAt']==policy['cards'][cid]['date']==original[cid]['releasedAt']
 assert c['releaseStatus']==original[cid]['releaseStatus']=='verified'
 builder.read_patches(c,cid)
 # Archive/native evidence must remain verbatim, even when display text changes.
 raw_hash=hashlib.sha256(json.dumps({k:c.get(k) for k in ('nativeRawText','nativeTags')},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 assert raw_hash==fixture['sourceEvidenceHashes'][cid],cid
 clean_display(c);clean_display(current[cid]);clean_display(render[cid])
 for observation in doc['historicalTextObservations']:
  match=next(x for x in observations[cid] if x['build']==observation['build'])
  assert observation['rawText']==match['rawText'] and observation['name']==match['name']
 expected=copy.deepcopy(original[cid]);expected.pop('history',None)
 for field in ('text','flavor'):
  if field in expected:expected[field]=norm(expected[field])
 # Only two non-formatting/current semantic corrections in this pass.
 if cid=='FP1_025':expected['text']=sources['37.0.2']['after']
 if cid=='FP1_008':expected['mechanics']=['ELUSIVE']
 expected.update({k:v for k,v in {'classes':[],'races':[],'race':'','spellSchool':''}.items() if k not in expected})
 actual=copy.deepcopy(current[cid]);actual.pop('history',None)
 assert actual==expected,(cid,{k:(expected.get(k),actual.get(k)) for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)})
 assert current[cid]['nativeTags']==original[cid]['nativeTags']
 dates={c['releasedAt'],'2026-11-09','2099-12-31'}
 dates.update(p['date'] for p in c['patches'])
 days=set()
 for day in dates:
  d=date.fromisoformat(day)
  days.update((d+timedelta(days=n)).isoformat() for n in (-1,0,1))
 for day in days:
  assert forward(c,day)==reverse(render[cid],day),(cid,day)
  checks+=1
 h=legacy.get(str(c['dbfId']),{}).get('history',[])
 assert h==render[cid].get('history',[])
 assert forward(c,'2099-12-31')==reverse(current[cid],'2099-12-31')
 # Selected raw-build numerical observations independently validate every ID.
 for o in observations[cid]:
  b=tuple(map(int,o['build'].split('.')))
  state={k:c.get(k,0) for k in ('cost','attack','health','durability')}
  if cid=='FP1_007t' and b>=(6,0,0,13921):state['cost']=4
  if cid=='FP1_019t':state['cost']=2 if (11,0,0,23966)<=b<(26,0,0,170824) else 1
  if cid=='FP1_012' and b>=(27,2,0,183876):state['health']=6
  if cid=='FP1_025' and b>=(27,2,0,183876):state['cost']=1
  raw={key:int(o['values'].get(tag,0)) for key,tag in [('cost','48'),('attack','47'),('health','45'),('durability','187')]}
  if c['type']=='WEAPON':raw['health']=raw['durability']
  assert state==raw,(cid,o['build'],state,raw)
 # First-build tribe state must not accidentally contain future Undead.
 v=observations[cid][0]['values'];r={20:'BEAST',15:'DEMON'}.get(int(v.get('200',0)))
 assert c.get('races',[])==([r] if r else []),(cid,c.get('races'),r)

# Explicit semantic regressions. These dates are Korean server days, not archive times.
def at(cid,day):return forward(docs[cid]['card'],day)
assert at('FP1_012','2023-08-22')['health']==5 and at('FP1_012','2023-08-23')['health']==6
assert at('FP1_025','2023-08-22')['cost']==2 and at('FP1_025','2023-08-23')['cost']==1
assert at('FP1_025','2026-11-03')['text']==sources['37.0.2']['before']
assert at('FP1_025','2026-11-04')['text']==sources['37.0.2']['after']
assert '+1/+1' in at('FP1_028','2015-01-29')['text']
assert '공격력을 +1' in at('FP1_028','2015-01-30')['text']
assert '공격력을 +1' in at('FP1_028','2021-03-25')['text']
assert '+1/+1' in at('FP1_028','2021-03-26')['text']
assert at('FP1_007t','2016-08-09')['cost']==3 and at('FP1_007t','2016-08-10')['cost']==4
assert at('FP1_019t','2018-04-10')['cost']==1 and at('FP1_019t','2018-04-11')['cost']==2
assert at('FP1_019t','2023-04-04')['cost']==2 and at('FP1_019t','2023-04-05')['cost']==1
assert at('FP1_012t','2020-03-26')['name']=='수액괴물'
assert at('FP1_012t','2020-03-27')['name']=='부패한 수액괴물'
assert at('FP1_002','2014-12-04')['legacyArt'] and not at('FP1_002','2014-12-05')['legacyArt']
assert at('FP1_030','2014-07-29') is None
assert '죽음의 메아리' in at('FP1_030','2014-07-30')['text']
assert '전투의 함성' in at('FP1_030','2014-08-01')['text']
for day in ('2014-07-30','2014-07-31','2014-08-01','2026-11-09'):
 assert at('FP1_030',day)['mechanics']==['BATTLECRY']
for o in observations['FP1_030'][:2]:assert o['values']['218']=='1' and o['values'].get('217','0')=='0'
assert at('FP1_002t','2022-11-29')['races']==[]
assert set(at('FP1_002t','2022-11-30')['races'])=={'BEAST','UNDEAD'}
assert 'ELUSIVE' not in at('FP1_008','2024-03-11')['mechanics']
assert at('FP1_008','2024-03-12')['mechanics']==['ELUSIVE']
assert sum('partial' in c['historicalDisplayTextStatus'] for c in audit['cards'])==23

# Rebuilding twice must leave all source and bundle bytes identical.
paths=[ROOT/p for p in ('cards.json','render.json','history.json','cards-date.json','render-date.json','history-date.json')]+list((ROOT/'data').glob('*.json'))
before={p:p.read_bytes() for p in paths}
subprocess.run([sys.executable,str(ROOT/'tools/build-api.py')],check=True,capture_output=True)
assert all(p.read_bytes()==b for p,b in before.items()),'non-idempotent builder'
print(json.dumps({'cards':len(docs),'collectible':30,'tokens':5,'releaseDatesVerified':35,'datedEvents':sum(len(d['card']['patches']) for d in docs.values()),'forwardReverseBoundaryChecks':checks,'clientNumericObservations':sum(map(len,observations.values())),'partialInitialTexts':23,'currentSemanticExceptions':['FP1_025 text','FP1_008 mechanics'],'rawEvidencePreserved':True,'buildIdempotent':True}))
