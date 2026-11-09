# Curse of Naxxramas

Korean card API with date-first canonical data in `data/<CARD_ID>.json` and lossless evidence in `metadata/<CARD_ID>.json`.

- Initial date: available type-specific historical baseline. Later dates: changed fields only, in KST order. Explicit `__remove` distinguishes deletion from omission and literal zero/empty values.
- Scope: 35 API IDs, 30 collectible cards, five tokens and 37 preserved events.
- The selected date rule is **actual normal-match play availability in Korea**, represented here by the existing constructed reward dates and five separate wing openings. Adventure-only previews and client preloading do not move those dates. Generated tokens follow their parent cards.
- Exact initial Korean wording remains incomplete for 23 cards. All full baseline confidence stays partial. No unknown cosmetic date is invented.
- Four source `mechanics` annotation errors are corrected in canonical/precise states using 15 archived client snapshots. Original JSON and old-client behavior remain preserved.

Existing clients keep `cards.json`, `render.json` and `history.json`. The current root catalog is byte-identical to the pinned pre-migration catalog. Precise opt-in clients use `cards-date.json`, `render-date.json` and `history-date.json`, with `historySchema: 2` for authoritative state and field removal. All six remain at the root so artwork links retain their base. Do not configure the old plugin to use the precise endpoints.

Run `python3 tools/build-api.py` and the validation commands in [docs/date-schema.md](docs/date-schema.md). No plugin, database or site changes are required for the existing endpoints. [BALANCE-AUDIT.md](BALANCE-AUDIT.md) records the earlier bounded audit; [tools/naxx-date-recheck.json](tools/naxx-date-recheck.json) adds the new date-source review and limitations.
