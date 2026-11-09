# Curse-of-Naxxramas

Korean constructed-card API. Canonical gameplay data lives in `data/<CARD_ID>.json`.

## History format

- `schemaVersion: 2`: `card.releasedAt` is the first Korean constructed reward availability day, not client preload or arena preview.
- `card` holds the release numeric/type baseline. `card.patches` contains only changed fields, in increasing Korean effective-date order. Unchanged cards still have a dated baseline and an empty patches array.
- Korean Naxxramas wing dates remain July 23, July 30, August 6, August 13 and August 20, 2014. Class challenges and generated tokens use their corresponding reward availability.
- **Exact historical Korean wording is not fully verified.** For 23 cards, dated functional changes are modeled using normalized wording while the exact initial/intermediate cosmetic wording remains incomplete. Do not interpret those texts as certified original wording. `tools/naxx-release-audit.json` records each card's status, original text and observed build ranges.
- `historicalTextObservations`, `nativeRawText` and `nativeTags` preserve raw evidence. Archive build observations are not patch dates. Installed native tags are not the date-effective gameplay specification.
- Display strings use `<br></br>`. Raw evidence is deliberately unchanged.

## Generated bundles

Run `python3 tools/build-api.py`, then `python3 tools/test-naxx-history.py`.

`cards.json` is the current catalog. `render.json` contains current rendering data and sparse, bounded historical overrides. `history.json` is retained for existing clients. Do not hand-edit these generated bundles.

The shared builder is pinned to `qxwd565/legacy@fd9de0e345c0c3730070427e1d42db1046f222e1`. CI rebuilds the same files and runs release, patch boundary, raw-evidence and current-value regressions. See `BALANCE-AUDIT.md` for the bounded audit scope and remaining gaps.
