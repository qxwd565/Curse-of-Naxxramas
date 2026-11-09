# Naxxramas balance and release audit

This pass covers all 35 API IDs: 30 collectible cards and five generated tokens. It verifies initial numerical/type data against the 1.1.0.6024 client archive, checks thirteen selected client snapshots, preserves independently verified Korean wing reward dates, and publishes 37 sourced dated events on 28 cards. It is **not an exhaustive exact-text, artwork, rule-engine bug-fix or temporary format-ban chronology**.

## Corrected histories

- Loatheb: Korean text typo fixed August 1, 2014, after its July 30 reward opening. The actual mechanic remains BATTLECRY on both sides. No Deathrattle effect is invented. Unverified cosmetic phrasing remains separately qualified.
- Haunted Creeper: old-art boundary corrected from the US December 4 date to the Korean December 5, 2014 patch. This was before GvG's constructed release.
- Undertaker: +1/+1 to +1 Attack on January 30, 2015 in Korea; reverted March 26, 2021.
- Nerubian token: cost 3 to 4 on August 10, 2016.
- Maexxna: existing lethal-damage text becomes Poisonous on March 1, 2017. The effect is not treated as newly added.
- Poison Seeds' Treant: cost 1 to 2 on April 11, 2018, then back to 1 on April 5, 2023.
- Sludge Belcher's token: Korean name changes from 수액괴물 to 부패한 수액괴물 on March 27, 2020.
- Four spell schools: March 26, 2021. Undead tags: November 30, 2022. Spectral Spider gains both Beast and Undead from an originally untyped state; it was not originally a Beast.
- Sludge Belcher: 3/5 to 3/6 on August 23, 2023. Reincarnate: cost 2 to 1 the same day.
- Spectral Knight: existing targeting restriction becomes Elusive on March 12, 2024. The missing current ELUSIVE mechanics field is also supplied.
- Reincarnate: November 4, 2026 Korean 37.0.2 changes the target to non-Legendary minions. This intentionally fixes the stale current bundle, not only historical lookup. Exact official Korean wording is in the source ledger.

Every event's sources and Korean date rationale are in `tools/naxx-audit-sources.json`. Official Korean notes are primary. Contemporary Korean reports resolve server/region differences; wiki history is a secondary index. Client commit timestamps are never used as application dates.

## Limits and pending work

`tools/naxx-release-audit.json` lists all 35 IDs and their status. Twenty-three initial display texts remain only functionally reconstructed: exact release text and intervening Korean cosmetic edits differ from the normalized API wording. The original text and observed before/after build ranges are saved, without assigning invented dates. These cards are **not certified complete original-spec reconstructions**. Even cards whose baseline wording matches may have unexamined intervening cosmetic edits.

`tools/naxx-client-observations.json` preserves raw text, names and numerical tags from thirteen selected builds, not every client build. Extra cosmetic transitions require adjacent-build and Korean deployment verification. Changes absent from these sampled states or official notes could remain; no exhaustive completion claim is made.

All existing wing dates and raw native evidence are retained. The generated catalog intentionally changes current gameplay content only for Reincarnate's latest text and Spectral Knight's missing ELUSIVE field, plus requested display-break normalization and empty API defaults. Numerical current values otherwise remain unchanged.

## Validation

`tools/test-naxx-history.py` checks all source JSON, numeric baselines, 13-build numerical observations, exact release/patch boundaries, forward/reverse equivalence, current regression exceptions, retained native evidence and display-break syntax. CI performs the same checks. A second build must make no byte changes. Commit and CI URLs are reported after publication; this document does not pre-claim a successful push.
