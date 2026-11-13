# Curse of Naxxramas

Korean card API with date-first canonical data in `data/<CARD_ID>.json` and lossless evidence in `metadata/<CARD_ID>.json`.

- Initial date: available type-specific historical baseline. Later dates: changed fields only, in KST order. Explicit `__remove` distinguishes deletion from omission and literal zero/empty values.
- Scope: 35 API IDs, 30 collectible cards, five tokens and 37 preserved events.
- The selected date rule is **actual normal-match play availability in Korea**, represented here by the existing constructed reward dates and five separate wing openings. Adventure-only previews and client preloading do not move those dates. Generated tokens follow their parent cards.
- Exact initial Korean wording remains incomplete for 23 cards. All full baseline confidence stays partial. No unknown cosmetic date is invented.
- Four source `mechanics` annotation errors are corrected in canonical/precise states using 15 archived client snapshots. Original JSON and old-client behavior remain preserved.

Existing clients keep `cards.json`, `render.json` and `history.json`. The current root catalog is byte-identical to the pinned pre-migration catalog. Precise opt-in clients use `cards-date.json`, `render-date.json` and `history-date.json`, with `historySchema: 2` for authoritative state and field removal. All six remain at the root so artwork links retain their base. Do not configure the old plugin to use the precise endpoints.

Run `python3 tools/build-api.py` and the validation commands in [docs/date-schema.md](docs/date-schema.md). No plugin, database or site changes are required for the existing endpoints. [BALANCE-AUDIT.md](BALANCE-AUDIT.md) records the earlier bounded audit; [tools/naxx-date-recheck.json](tools/naxx-date-recheck.json) adds the new date-source review and limitations.

## 최초 출시일 재검증 (2026-11-13)

거미·역병·군사·피조물·서리고룡 각 지구의 한국 실제 개방일과 보스 보상·직업 도전·생성 토큰을 독립적인 동시대 국내 기사 및 블리자드 공식 보상표와 교차 검증했습니다. 전체 35개 ID(수집 가능 30, 생성 토큰 5)의 날짜와 부모 연결이 일치해 **날짜 수정은 필요하지 않았습니다**. 자세한 카드별 근거는 [최초 출시일 검증 기록](tools/naxx-first-release-verification-20261113.json), 재발 방지 CI 검사는 `python3 tools/test-naxx-first-release.py`에 있습니다. 앞선 지구에서 고정 도전 덱에만 등장한 카드의 관찰 기록은 일반 대전에서 수집·사용 가능한 최초 날짜로 소급하지 않습니다. 능력치·밸런스 패치·원본 클라이언트 기록은 이번 검증에서 변경하지 않았습니다.
