# Date-first Naxxramas data

Scope: `qxwd565/Curse-of-Naxxramas`, 35 existing API IDs (30 collectible cards and five generated tokens), migrated from `8073e268c660345a56e9b2dc745b42b9823a5c29`. No other expansion, plugin, site, database or import configuration is changed.

## Canonical representation

Every existing `data/<CARD_ID>.json` filename stays in place. Its top-level keys are ascending KST calendar dates. The first key contains the available release gameplay baseline; subsequent keys contain only changed fields. All 37 prior events remain, on their existing dates. Actual field names such as `cost` remain unchanged.

- Omitted fields in later records inherit their previous value.
- `__remove: ["field"]` explicitly removes a field. A removal cannot overlap a value written by the same record.
- Literal zero, false, null, empty strings and empty arrays are values, not removal operations. Objects and arrays replace the entire prior field.
- Existing empty `race`, `races` and `spellSchool` exporter placeholders represent absent attributes and are omitted from canonical states. They are preserved in immutable source evidence and restored only at the old-client boundary.
- A minion retains attack/health, a spell has no invented combat stats, and Death's Bite retains attack/durability without the former health mirror. The actual zero attack of Nerubian Egg remains zero.
- Display text uses exactly `<br></br>`. Raw native and archived text is not normalized or rewritten.
- Future tribe/school/keyword properties are not backdated. Original Spectral Spider has no tribe, gains Beast plus Undead on 2022-11-30, and four spells gain their schools on 2021-03-26.

`fold` is an exact chronological fold and returns no card before its first date. `resolve` preserves the established verified/estimated/pending confidence behavior. All Naxxramas reward dates are verified, but that does not make every historical baseline field verified. All 35 full baselines remain `partially-verified`; 23 exact initial Korean descriptions are explicitly incomplete. The other 12 matching descriptions do not establish an exhaustive cosmetic history. Opt-in strict lookup refuses unverified full baselines.

## What the dates mean

The user-selected rule is **actual normal-match play availability in Korea**. For this dataset, the existing Korean constructed reward dates implement that rule: class-challenge reward cards become usable in normal matches after unlocking, and generated tokens follow their parent cards. Adventure-only fixed-deck previews and client preloading are excluded. All five prior wing dates remain: 2014-07-23, 2014-07-30, 2014-08-06, 2014-08-13 and 2014-08-20.

Official Korean wing posts corroborate rewards and class-challenge structure, but their rendered publication headers are a day earlier than the Korean opening. Contemporary Korean reports establish the KST dates. The official final-wing post also contains a two-challenge template error; the actual final wing has the Paladin/Avenge challenge only. The additive source ledger `tools/naxx-date-recheck.json` explains these distinctions.

A contemporary August 6 Shaman challenge guide mentions Feugen and Stalagg before their August 13 constructed reward opening. The described conditional Deathrattles and 11/11 Thaddius generation strongly match the FP1 cards, unlike same-name heroic NPC minions. Direct challenge-deck/log binding remains unlocated. That observation is retained separately rather than silently shifting release keys. Additional Druid/Rogue/Mage challenge guides name earlier Ooze, Stoneskin Gargoyle, Loatheb, Mad Scientist or Undertaker entries. These are separate candidates, not invented first-use dates; boss-copy/steal routes were not exhaustively checked. The user has selected normal-match use rather than adventure-only appearances. These observations are historical context only and do not change the constructed reward dates; no date-scope decision remains pending.

## Lossless sidecars and source corrections

`metadata/<ID>.json` holds the complete immutable `originalSource`, pinned `sourceCommit`, unchanged `currentCatalog`, release confidence, baseline evidence and undated observations. Parent/child links, raw native tags, native text, set/exporter metadata, provenance, portraits, artwork and all other original JSON remain present. Current-only metadata is not claimed to have existed on release day. Observation ranges are not converted into invented patch dates.

Four inherited `mechanics` lists mixed keywords mentioned by the card with abilities it actually has. The canonical baselines now use actual abilities:

| ID | Prior exporter annotations | Actual abilities |
| --- | --- | --- |
| FP1_004 | DEATHRATTLE, SECRET | DEATHRATTLE |
| FP1_017 | BATTLECRY | AURA |
| FP1_028 | TRIGGER_VISUAL, DEATHRATTLE | TRIGGER_VISUAL |
| FP1_031 | DEATHRATTLE | AURA |

These are source-annotation corrections, not new gameplay patches. `tools/naxx-mechanics-evidence.json` distinguishes XML `Tag` from `ReferencedTag` in 15 selected builds from 1.1.0.6024 through 37.0.2.256589. All 60 affected card/build observations agree. The retained installed `nativeTags` merge actual and referenced tags; they are preserved as evidence, not used as an authoritative historical ability list. Loatheb remains BATTLECRY even when its old Korean description erroneously said Deathrattle. The official Plague Quarter post explicitly confirms the 2014-08-01 text correction.

No Legacy-only Jaraxxus exception or weapon source decoder is applied. The original Naxxramas Death's Bite baseline already has genuine durability 2. The selected 37.0.2 XML archive encodes that same weapon durability in native HEALTH tag 45 instead of tag 187; only the archive comparison recognizes this explicit build-specific representation. It does not create a runtime truthiness fallback or reinterpret a canonical zero.

## Dual root transports

All six bundles are siblings at the repository root, so existing `art/<ID>` paths keep their original base.

Existing consumers continue to use:

- `cards.json`: schema 1 current import catalog. It is regenerated from canonical values plus the explicit compatibility boundary and remains byte-identical to the pinned original in this migration.
- `render.json`: schema 1 current rendering fields plus ordinary sparse reverse intervals.
- `history.json`: schema 1 DBF-keyed history with the existing `id`/`history` contract.

Precise consumers opt into:

- `cards-date.json`: current type-specific values with the four corrected ability lists and separately retained current metadata.
- `render-date.json`: `historySchema: 2`, explicit removal operations, confidence and current-only metadata labels.
- `history-date.json`: `historySchema: 2`, complete authoritative current gameplay for all 35 IDs and disjoint reverse intervals.

The old plugin must not be pointed at the precise endpoints. Its whitelist cannot express arbitrary removal, field presence or a complete authoritative snapshot. The root boundary restores numeric zero placeholders, empty race/school sentinels, Death's Bite's health mirror and the four original keyword-annotation conventions. This preserves existing imports and historical behavior while leaving exact states correct in canonical and precise outputs. It is deliberately lossy, not described as precise rendering. The compatibility mapper translates only each reviewed exact ability state, not every future change back to a frozen list.

No new existence gate is enabled for old clients; their established before-release fallback remains unchanged. The installed raw tags can still influence an old renderer. These limits are explicit in `tools/legacy-compatibility-losses.json`. Plugin changes remain separate.

## Rebuilding and checks

Run from this repository:

1. `python3 tools/migrate-date-schema.py`
2. `python3 tools/build-api.py`
3. `python3 tools/test-naxx-history.py`
4. `python3 tools/test-date-schema.py`
5. `python3 tools/test-naxx-mechanics.py`
6. `python3 tools/test-legacy-compatibility.py`
7. `python3 tools/test-build-idempotence.py`
8. `python3 tools/test-clean-migration.py`
9. `git diff --check`

The previous wrapper builder remains as `tools/wrapper_api_reference.py` for read-only regression helpers. Executing its writer is explicitly disabled. CI uses the local date-aware builder, no longer overwrites it with a remote wrapper builder, and checks out full history (`fetch-depth: 0`). Preservation checks fail with an explicit fetch instruction when the pinned source is absent; they are not skipped.

The reports cover all 35 original JSON documents, 37 preserved events, 1,960 all-card/global-date source and precise-transport cases, 1,960 old-consumer behavior cases, 455 retained numeric observations and 525 newly extracted numeric/type/class/race/school/ability observations. There are 214 unchanged artwork/golden asset files and 210 root-art URL checks. Current root catalog equivalence is checked at the byte level. A clean pinned-source regeneration reproduces all 76 canonical/sidecar/bundle files byte-for-byte; missing pinned source fails explicitly. Generic fixtures test null/zero/empty/absence, removals, identity protection and all supported type transitions.

For the actual unchanged PHP parser, generate a fixture using `python3 tools/test-legacy-compatibility.py --fixture /tmp/naxx-compatibility.json`, then run `php tools/test-legacy-plugin.php /path/to/unmodified/plugin /tmp/naxx-compatibility.json`. The offline harness checks all 35 imported records, complete equality with the old import result, asset resolution and all 1,960 date cases. It performs no network, WordPress or database writes. Local validation used PHP WASM 8.5.12 with unmodified HSdeck-plugin `78ce6fdc4e70f689880a70d6f22aa77a6c75e337`; this does not claim a live browser or deployed-site test.

These checks are bounded evidence, not an exhaustive every-build, exact-wording, artwork or rule-engine bug chronology. Full baseline confidence is not promoted by migration success. Future approved canonical gameplay changes must review the expected-difference tests instead of freezing the current builder.
