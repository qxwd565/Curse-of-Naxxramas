# Curse of Naxxramas

Korean card API with date-first canonical data in `data/<CARD_ID>.json` and lossless evidence in `metadata/<CARD_ID>.json`.

- Initial date: available type-specific historical baseline. Later dates: changed fields only, in KST order. Explicit `__remove` distinguishes deletion from omission and literal zero/empty values.
- Scope: 35 API IDs, 30 collectible cards, five tokens and 37 preserved events.
- The selected date rule is **actual normal-match play availability in Korea**, represented here by the existing constructed reward dates and five separate wing openings. Adventure-only previews and client preloading do not move those dates. Generated tokens follow their parent cards.
- Exact initial Korean wording remains incomplete for 23 cards. All full baseline confidence stays partial. No unknown cosmetic date is invented.
- Four source `mechanics` annotation errors are corrected in canonical/precise states using 15 archived client snapshots. Original JSON and old-client behavior remain preserved.

API 제공 파일은 `cards.json`(카드 목록 및 현재 표시 정보), `data/<카드ID>.json`(한국 날짜별 최초 사용 및 변경 내용), `art/`, `golden/`, `frame/`(존재하는 경우)입니다. 이전 집계용 `render.json`, `history.json`, `cards-date.json`, `render-date.json`, `history-date.json`은 게시하지 않습니다. 생성기의 임시 검증 출력으로만 사용합니다. HSdeck-plugin은 카드별 날짜 JSON을 직접 사용합니다.

## 편집 및 경량화 지침

- 사용 가능한 첫날을 **한국 날짜(YYYY-MM-DD)**로 기록합니다. 베타는 북미 첫 실사용을 한국 시간으로 변환하고, 모험모드는 각 지구 실제 개방일, 이벤트는 실제 개시일을 사용합니다. 사전 클라이언트 탑재일을 출시일로 기록하지 않습니다.
- `data/<카드ID>.json`의 첫 날짜에는 최초 상태, 후속 날짜에는 변경된 필드만 기록합니다. 과거 오기입은 새 키만 추가하지 말고 **오류 키 자체를 삭제·통합**합니다. 토큰·자식 카드도 검증합니다.
- 카드 능력치·효과·직업·종족·설명·원화 링크·일반/황금 카드·애니메이션·프레임 의존성은 무손실 보존합니다. `<br></br>` 줄바꿈을 사용하고 실제 원시 증거는 임의 치환하지 않습니다.
- `cards.json`은 카드 ID/DBF ID 및 현재 목록 표시용이고, 날짜별 정보의 단일 원본은 `data/`입니다. `render*.json`, `history*.json`, `cards-date.json`을 다시 커밋하지 않습니다. 불필요한 schema/호환 래퍼를 새로 만들지 않습니다.
- `metadata/`, `tools/`, `.github/`에는 **날짜 근거 검증과 빌드 재현을 위해 실제 참조되는 내용만** 유지합니다. 검증을 완료하지 않은 근거를 임의 삭제하거나 추정 날짜를 '검증됨'으로 변경하지 않습니다.
- 공개 카드 데이터 외의 진단·호환용 집계 파일이 다시 만들어지는 경우 저장소에서 제외하고 빌드 및 테스트를 수정합니다. 프레임/황금 애니메이션 바이너리는 임의 재인코딩하지 않습니다.


## 최초 출시일 재검증 (2026-11-13)

거미·역병·군사·피조물·서리고룡 각 지구의 한국 실제 개방일과 보스 보상·직업 도전·생성 토큰을 독립적인 동시대 국내 기사 및 블리자드 공식 보상표와 교차 검증했습니다. 전체 35개 ID(수집 가능 30, 생성 토큰 5)의 날짜와 부모 연결이 일치해 **날짜 수정은 필요하지 않았습니다**. 자세한 카드별 근거는 [최초 출시일 검증 기록](tools/naxx-first-release-verification-20261113.json), 재발 방지 CI 검사는 `python3 tools/test-naxx-first-release.py`에 있습니다. 앞선 지구에서 고정 도전 덱에만 등장한 카드의 관찰 기록은 일반 대전에서 수집·사용 가능한 최초 날짜로 소급하지 않습니다. 능력치·밸런스 패치·원본 클라이언트 기록은 이번 검증에서 변경하지 않았습니다.
