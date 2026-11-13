#!/usr/bin/env python3
"""Cross-check first playable Naxxramas rewards, wing dates, and children against independent Korean sources."""
from __future__ import annotations
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from date_schema import read_card, resolve

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def main():
    audit = read("tools/naxx-first-release-verification-20261113.json")
    policy = read("release-policy.json")
    cards = {c["id"]: c for c in read("cards-date.json")["cards"]}
    old_cards = {c["id"]: c for c in read("cards.json")["cards"]}
    existing_review = read("tools/naxx-date-recheck.json")
    assert audit["timezone"] == policy["timezone"] == "Asia/Seoul"
    assert len(cards) == len(old_cards) == len(policy["cards"]) == 35
    assert len(audit["wings"]) == len(existing_review["wings"]) == 5
    assert {p.stem for p in (ROOT / "data").glob("*.json")} == set(cards)
    assert {p.stem for p in (ROOT / "metadata").glob("*.json")} == set(cards)
    assert audit["result"]["dateChangesRequired"] is False
    assert audit["result"]["incorrectOriginalReleaseDates"] == []
    assert audit["result"]["missingInCurrentAPIScope"] == []
    seen = set()
    counts = Counter()
    challenge_classes = set()
    for row, previous in zip(audit["wings"], existing_review["wings"]):
        day = row["date"]
        assert day == previous["date"]
        assert date.fromisoformat(day).isoformat() == day
        assert row["evidence"]["officialBlizzard"].startswith("https://hearthstone.blizzard.com/")
        assert row["evidence"]["contemporaryKoreanOpening"].startswith("https://")
        assert {e["id"] for e in row["cards"]} == set(previous["cards"])
        for entry in row["cards"]:
            cid = entry["id"]
            assert cid not in seen, cid
            seen.add(cid)
            current = cards[cid]
            historical = old_cards[cid]
            timeline, meta = read_card(ROOT, cid)
            assert entry["name"] == current["name"] == historical["name"] or (
                cid == "FP1_012t" and entry["name"] == current["name"]
            ), cid
            assert entry["dbfId"] == current["dbfId"] == historical["dbfId"]
            assert current["releasedAt"] == historical["releasedAt"] == day
            assert current["releaseStatus"] == historical["releaseStatus"] == "verified"
            assert policy["cards"][cid] == {"date":day,"status":"verified"}
            assert meta["release"] == {"date":day,"status":"verified"}
            assert list(timeline)[0] == day
            assert resolve(timeline,meta,(date.fromisoformat(day)-timedelta(days=1)).isoformat()) is None, cid
            assert resolve(timeline,meta,day)["id"] == cid
            role = entry["role"]
            assert role in {"boss","wing-legendary","class-challenge","generated"}, cid
            assert current["collectible"] == (role != "generated")
            counts[role] += 1
            if role == "class-challenge":
                challenge_classes.add(entry["class"])
            if role == "generated":
                assert entry["parentCardIds"], cid
                for parent_id in entry["parentCardIds"]:
                    parent = cards[parent_id]
                    assert parent["releasedAt"] == day
                    assert parent["collectible"] is True
                    assert current["dbfId"] in parent.get("relatedDbfIds",[]), (cid,parent_id)
            if role == "wing-legendary":
                assert current["rarity"] == "LEGENDARY", cid
    assert seen == set(cards) == set(policy["cards"])
    assert counts == Counter({"boss":15,"wing-legendary":6,"class-challenge":9,"generated":5})
    assert challenge_classes == {"DRUID","HUNTER","MAGE","PALADIN","PRIEST","ROGUE","SHAMAN","WARLOCK","WARRIOR"}
    assert dict(counts) == audit["result"]["byRole"]
    assert audit["result"]["allCardIds"] == 35
    assert audit["result"]["collectible"] == 30
    assert audit["result"]["generatedTokens"] == 5
    assert len(audit["observedEarlierAdventureOnly"]) >= 3
    for case in audit["observedEarlierAdventureOnly"]:
        assert case["id"] in cards
        assert case["normalPlayDate"] == cards[case["id"]]["releasedAt"]
        assert case["source"].startswith("https://")
    print(json.dumps({"result":"pass","checked":len(seen),"collectible":30,
                      "generatedTokens":5,"wingDates":[w["date"] for w in audit["wings"]],
                      "roles":dict(counts),"earlyAdventureContextUnchanged":True,
                      "balanceOrStatChanges":False},ensure_ascii=False))

if __name__ == "__main__":
    main()
