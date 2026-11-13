#!/usr/bin/env python3
"""Independent source replay, presence/type, all-date and preservation tests."""
from __future__ import annotations
import copy, hashlib, json, subprocess, sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from date_schema import (SPECS, REMOVE, apply, delta, fold, load, put, project,
                         read_card, resolve, validate_timeline, UncertainHistory, json_equal)
ROOT=Path(__file__).resolve().parents[1]
SOURCE='8073e268c660345a56e9b2dc745b42b9823a5c29'


def require_source_commit(root, commit):
    result=subprocess.run(['git','cat-file','-e',commit+':data'],cwd=root,capture_output=True)
    if result.returncode:
        raise RuntimeError('Pinned migration source commit unavailable: '+commit+
                           '. Fetch full history (checkout fetch-depth: 0) or explicitly fetch this commit; preservation checks cannot be skipped.')


def original(path):
    return json.loads(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT))


def independent_expected(document, day):
    raw=copy.deepcopy(document['card'])
    if day is not None and day<raw['releasedAt']:return None
    for event in raw.get('patches',[]):
        if day is None or event['date']<=day:
            raw.update(copy.deepcopy(event['changes']))
    # Independent field/presence oracle, not the migration's project/fold.
    fields={'id','dbfId','name','type','cardClass','classes','rarity','collectible',
            'cost','attack','health','durability','armor','text','races','race',
            'spellSchool','mechanics','legacyArt'}
    result={k:copy.deepcopy(v) for k,v in raw.items() if k in fields}
    keep={'MINION':{'cost','attack','health'},'SPELL':{'cost'},'WEAPON':{'cost','attack','durability'}}[raw['type']]
    for k in {'cost','attack','health','durability','armor'}-keep:result.pop(k,None)
    for k,empty in [('race',''),('races',[]),('spellSchool','')]:
        if k in result and result[k]==empty:del result[k]
    # Independently reviewed source corrections; not the migration mapping.
    actual_abilities = {'FP1_004':['DEATHRATTLE'], 'FP1_017':['AURA'],
                        'FP1_028':['TRIGGER_VISUAL'], 'FP1_031':['AURA']}
    if raw['id'] in actual_abilities:result['mechanics']=actual_abilities[raw['id']]
    # Approved 2026 display-only underscore repair (single FP1_002 text field).
    # Keep originalSource immutable; only canonical replay uses the correction.
    if raw['id']=='FP1_002':
        assert '죽음의_메아리' in result['text']
        result['text']=result['text'].replace('죽음의_메아리','죽음의 메아리')
    return result


def reverse(record, day):
    if record['releaseStatus']=='verified' and day<record['releasedAt']:return None
    state=copy.deepcopy(record['current']);state.pop('art',None)
    matching=[r for r in record['history'] if r.get('from','0001-01-01')<=day<r.get('before','9999-12-31')]
    assert len(matching)<=1,('overlapping intervals',record['id'],day)
    for rev in matching:
        # Independent implementation of exact reverse operations.
        for field in rev['changes'].get('__remove',[]):state.pop(field,None)
        state.update({k:copy.deepcopy(v) for k,v in rev['changes'].items() if k!='__remove'})
    return state

def fixtures():
    states=[
        {'id':'TEST','type':'MINION','cost':1,'attack':0,'health':3,'text':'Taunt','mechanics':['TAUNT']},
        {'id':'TEST','type':'SPELL','cost':0,'text':'','mechanics':[]},
        {'id':'TEST','type':'WEAPON','cost':0,'attack':1,'durability':0,'text':''},
        {'id':'TEST','type':'HERO','cost':0,'armor':5,'text':''},
        {'id':'TEST','type':'LOCATION','cost':1,'durability':2,'text':''},
        {'id':'TEST','type':'HERO_POWER','cost':0,'text':''},
        {'id':'TEST','type':'ENCHANTMENT','text':'','effectData':{'amount':0},'explicitNull':None},
    ]
    timeline={};previous={}
    for i,state in enumerate(states,1):
        timeline[f'2020-01-0{i}']=delta(previous,state);previous=state
    validate_timeline(timeline)
    assert fold(timeline,'2019-12-31') is None
    for i,state in enumerate(states,1):assert fold(timeline,f'2020-01-0{i}')==state
    assert 'attack' not in fold(timeline,'2020-01-02')
    assert fold(timeline,'2020-01-01')['attack']==0
    assert fold(timeline,'2020-01-02')['text']==''
    assert fold(timeline,'2020-01-07')['explicitNull'] is None
    assert apply({'x':None},{})=={'x':None}
    assert apply({'x':None},{REMOVE:['x']})=={}
    for before,after in ((False,0),(True,1),({'nested':[False,{'x':True}]},{'nested':[0,{'x':1}]})):
        patch=delta({'effect':before},{'effect':after})
        assert patch=={'effect':after} and patch
        assert apply({'effect':before},patch,validate=True)=={'effect':after}
    assert project({'id':'BASE','type':'HERO','health':30,'attack':0,'armor':0},native_tags=[{'id':45,'value':30}])=={'id':'BASE','type':'HERO','health':30}
    assert project({'id':'EN','type':'ENCHANTMENT','attack':0,'text':''})['attack']==0
    effect={'id':'EN','type':'ENCHANTMENT','effectData':{'amount':0},'text':'','actualZero':0,'nullableEffect':None}
    assert project(effect,gameplay_fields={'effectData','actualZero','nullableEffect'})==effect
    try:project(effect)
    except ValueError:pass
    else:raise AssertionError('Unclassified effect fields silently dropped or backdated')
    raw={'id':'RAW','type':'SPELL','cost':0,'nativeSetId':1635,'installed':True,
         'techLevel':0,'battlegroundsNormalDbfId':0,'isBattlegroundsBuddy':False,
         'nativeTags':[{'id':1720,'value':1}],'releasedAt':'2013-08-17','releaseStatus':'estimated'}
    assert project(raw)=={'id':'RAW','type':'SPELL','cost':0}
    for race in ('DEMON','BEAST'):
        spell={'id':'CHOICE','type':'SPELL','cost':0,'text':'','race':race,'races':[race]}
        assert project(spell)==spell
    assert project({'id':'NO','type':'SPELL','cost':0,'race':'','races':[],'spellSchool':''})=={'id':'NO','type':'SPELL','cost':0}
    # Attribute loss creates explicit removal, never a future empty placeholder.
    before=project({'id':'RACE','type':'MINION','race':'BEAST','races':['BEAST'],'cost':1,'attack':1,'health':1})
    after=project({'id':'RACE','type':'MINION','race':'','races':[],'cost':1,'attack':1,'health':1})
    assert delta(before,after)=={REMOVE:['race','races']}
    for bad in ({'2020-02-30':states[0]}, {'2020-01-01':states[0],'2020-01-02':{'attack':0}}, {'2020-01-01':states[0],'2020-01-02':{REMOVE:['missing']}}, {'2020-01-01':states[0],'2020-01-02':{REMOVE:['attack'],'attack':1}}):
        try:validate_timeline(bad)
        except ValueError:pass
        else:raise AssertionError('Invalid/redundant timeline accepted')
    for change in ({'id':'OTHER'}, {REMOVE:['id']}, {'dbfId':456}, {REMOVE:['dbfId']}):
        bad={'2020-01-01':dict(states[0],dbfId=123),'2020-01-02':change}
        try:validate_timeline(bad)
        except ValueError:pass
        else:raise AssertionError('Card identity mutation accepted')
    for field,value in (('nativeTags',[]),('installed',True),('nativeSetId',1635),('techLevel',0),('set','LEGACY')):
        try:validate_timeline({'2020-01-01':states[0],'2020-01-02':{field:value}})
        except ValueError:pass
        else:raise AssertionError('Current-only field dated directly: '+field)


def main():
    fixtures();require_source_commit(ROOT,SOURCE)
    current={c['id']:c for c in load(ROOT/'cards-date.json')['cards']}
    rendered={c['id']:c for c in load(ROOT/'render-date.json')['cards']}
    histories=load(ROOT/'history-date.json')['cards']
    source_catalog={c['id']:c for c in original('cards.json')['cards']}
    files=sorted((ROOT/'data').glob('*.json'))
    assert {p.stem for p in files}==set(current)==set(rendered)==set(source_catalog)
    assert len(current)==len(histories)==35
    assert len({c['dbfId'] for c in current.values()})==35
    assert {p.name for p in files}=={p.name for p in (ROOT/'metadata').glob('*.json')}
    originals={p.stem:original('data/'+p.name) for p in files}
    dates={'1900-01-01','2099-12-31','2026-11-09'}
    for doc in originals.values():
        for d in [doc['card']['releasedAt']]+[e['date'] for e in doc['card']['patches']]:
            dates.update((date.fromisoformat(d)+timedelta(days=n)).isoformat() for n in (-1,0,1))
    scope_ledger=load(ROOT/'tools/naxx-date-recheck.json')
    assert scope_ledger['dateScopeDecision']['status']=='confirmed'
    assert scope_ledger['dateScopeDecision']['dateChangesRequired'] is False
    checks=0;patches=0;types=Counter();losses=[]
    for p in files:
        cid=p.stem;timeline,meta=read_card(ROOT,cid);doc=originals[cid]
        assert meta['sourceCommit']==SOURCE
        assert meta['availabilityScope']==scope_ledger['dateBasis']
        assert json_equal(meta['originalSource'],doc),(cid,'original JSON loss')
        assert json_equal(meta['currentCatalog'],source_catalog[cid]),(cid,'current metadata loss')
        assert meta['baselineStatus']=='partially-verified'
        assert meta['release']=={'date':doc['card']['releasedAt'],'status':'verified'}
        assert list(timeline)==sorted(timeline)
        assert len(timeline)==1+len(doc['card']['patches'])
        validate_timeline(timeline)
        patches+=len(timeline)-1
        for day in sorted(dates):
            expected=independent_expected(doc,day)
            actual=resolve(timeline,meta,day)
            assert json_equal(actual,expected),(cid,day,'source replay',actual,expected)
            assert json_equal(reverse(histories[str(current[cid]['dbfId'])],day),expected),(cid,day,'history-date')
            render_current={k:v for k,v in rendered[cid].items() if k in SPECS}
            render_record={**histories[str(current[cid]['dbfId'])],'current':render_current,'history':rendered[cid]['history']}
            assert json_equal(reverse(render_record,day),expected),(cid,day,'render-date')
            checks+=1
        expected=independent_expected(doc,None)
        assert json_equal({k:v for k,v in current[cid].items() if k in SPECS},expected),(cid,'current')
        assert current[cid]['id']==doc['card']['id'] and current[cid]['dbfId']==doc['card']['dbfId']
        for field,value in source_catalog[cid].items():
            if field not in SPECS:assert json_equal(current[cid][field],value),(cid,field,'current-only loss')
        assert all(field not in change for change in timeline.values() for field in ('nativeTags','nativeRawText','set','portrait','installed','relatedDbfIds','flavor','art'))
        state={}
        for day,changes in timeline.items():
            next_state=apply(state,changes)
            assert json_equal(delta(state,next_state),changes),(cid,day,'redundant delta')
            if 'UNDEAD' in next_state.get('races',[]):assert day>='2022-11-30'
            if next_state.get('spellSchool'):assert day>='2021-03-26'
            if cid=='FP1_002t' and 'BEAST' in next_state.get('races',[]):assert day>='2022-11-30'
            state=next_state
        types[state['type']]+=1
        try:resolve(timeline,meta,'2026-11-09',strict=True)
        except UncertainHistory:pass
        else:raise AssertionError('Incomplete baseline silently promoted')
        removed={k:v for k,v in doc['card'].items() if k in SPECS and k not in next(iter(timeline.values()))}
        losses.append({'id':cid,'sourcePlaceholdersExcludedFromCanonical':removed})
    assert patches==37
    assert types=={'MINION':30,'SPELL':4,'WEAPON':1}
    # Real zero and no Legacy-only health decoder or Jaraxxus exception.
    assert current['FP1_007']['attack']==0
    assert current['FP1_021']['durability']==2 and 'health' not in current['FP1_021']
    assert current['FP1_025']['cost']==1 and 'attack' not in current['FP1_025']
    for name in ('date_schema.py','build_date_api.py','legacy_projection.py'):
        s=(ROOT/'tools'/name).read_text()
        assert 'EX1_323' not in s and 'WEAPON_HEALTH_ENCODED' not in s
    report={'result':'pass','sourceCommit':SOURCE,'cards':35,'sourceDocumentsPreserved':35,
            'events':patches,'releaseDatesVerified':35,'partialExactInitialTexts':23,
            'baselineFullyVerified':0,'globalDateSamples':len(dates),'exactSourceAndTransportChecks':checks,
            'types':dict(types),'newGameplayCorrections':[], 'baselineMechanicsCorrections':['FP1_004','FP1_017','FP1_028','FP1_031'],
            'projectionChanges':losses,'presenceFixturesPassed':True}
    put(ROOT/'tools/date-schema-validation.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='projectionChanges'}))

if __name__=='__main__':main()
