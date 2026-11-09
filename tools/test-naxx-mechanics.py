#!/usr/bin/env python3
"""Fresh selected client-tag cross-check, including referenced-keyword separation."""
import json,sys
from pathlib import Path
from date_schema import read_card,resolve,load,put
ROOT=Path(__file__).resolve().parents[1]
evidence=load(ROOT/'tools/naxx-mechanics-evidence.json')
checks=0;mechanics=0
# Known effective milestones, not XML commit timestamps. Early archive data
# may preload future wings; compare the release baseline independent of gating.
for snapshot in evidence['builds']:
    build=tuple(map(int,snapshot['build'].split('.')))
    day='2014-08-20'
    for minimum,when in [((2,0,0,7234),'2014-12-05'),((2,1,0,7628),'2015-01-30'),
                         ((6,0,0,13921),'2016-08-10'),((11,0,0,23966),'2018-04-11'),
                         ((17,0,0,44222),'2020-03-27'),((20,0,0,77662),'2021-03-26'),
                         ((25,0,0,158725),'2022-11-30'),((26,0,0,170824),'2023-04-05'),
                         ((27,2,0,183876),'2023-08-23'),((31,2,0,212197),'2024-12-04'),
                         ((37,0,2,256589),'2026-11-04')]:
        if build>=minimum:day=when
    for cid,entry in snapshot['cards'].items():
        timeline,meta=read_card(ROOT,cid);state=resolve(timeline,meta,day);tags=entry['Tag']
        assert state['type']=={'4':'MINION','5':'SPELL','7':'WEAPON'}[tags['202']],(cid,snapshot['build'],'type')
        assert state['cost']==int(tags.get('48',0)),(cid,snapshot['build'],'cost')
        for field,tag in [('attack','47'),('health','45'),('durability','187')]:
            if field not in state:continue
            raw=int(tags.get(tag,0))
            if cid=='FP1_021' and snapshot['build']=='37.0.2.256589' and field=='durability':
                # This specific modern archive uses HEALTH for weapons. The
                # original Naxx baseline already has real durability=2; do not
                # install a truthy runtime fallback or Legacy source decoder.
                assert '187' not in tags and tags['45']=='2'
                raw=int(tags['45'])
            assert state[field]==raw,(cid,snapshot['build'],field)
        assert state['cardClass']=={'2':'DRUID','3':'HUNTER','4':'MAGE','5':'PALADIN','6':'PRIEST','7':'ROGUE','8':'SHAMAN','9':'WARLOCK','10':'WARRIOR','12':'NEUTRAL'}[tags.get('199','12')]
        assert state['collectible']==(tags.get('321')=='1')
        tribes=set()
        race={'11':'UNDEAD','15':'DEMON','20':'BEAST'}.get(tags.get('200'))
        if race:tribes.add(race)
        if tags.get('2542')=='1':tribes.add('BEAST')
        assert set(state.get('races',[]))==tribes,(cid,snapshot['build'],'tribes',state.get('races'),tags)
        school={'1':'ARCANE','2':'FIRE','3':'FROST','4':'NATURE','5':'HOLY','6':'SHADOW','7':'FEL'}.get(tags.get('1635'))
        assert state.get('spellSchool')==school,(cid,snapshot['build'],'school')
        assert set(state.get('mechanics',[]))==set(entry['actualMechanics']),(cid,snapshot['build'],'mechanics',state.get('mechanics'),entry['actualMechanics'])
        checks+=1
        if cid in evidence['baselineCorrections']:
            correction=evidence['baselineCorrections'][cid]
            assert state['mechanics']==correction['canonical']
            assert meta['originalSource']['card']['mechanics']==correction['original']
            assert meta['currentCatalog']['mechanics']==correction['original']
            current_tags={str(t['id']):str(t.get('value')) for t in meta['originalSource']['card']['nativeTags']}
            current_abilities={name for tag,name in evidence['mechanicTags'].items() if current_tags.get(tag)=='1'}
            latest=evidence['builds'][-1]['cards'][cid]
            flattened={**latest['Tag'],**latest['ReferencedTag']}
            flattened_abilities={name for tag,name in evidence['mechanicTags'].items() if flattened.get(tag)=='1'}
            # Retained exporter nativeTags merge actual and referenced tags.
            # Verify that evidence honestly; never call it an ability oracle.
            assert current_abilities==flattened_abilities,(cid,'installed merged native-tag evidence')
            mechanics+=1
report={'result':'pass','selectedBuilds':len(evidence['builds']),'cardNumericTypeClassRaceSchoolAbilityObservations':checks,
        'correctedAbilityObservations':mechanics,'scope':'Selected client snapshots, not an exhaustive every-build chronology.'}
put(ROOT/'tools/naxx-mechanics-validation.json',report)
print(json.dumps(report))
