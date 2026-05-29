# 멀티 테넌시 전환 작업 내역

**목표**: 특정 회사(빛드론/드론박스)에 종속된 코드를 누구나 사용할 수 있도록 범용화

---

## ✅ 작업 1 — 하드코딩된 브랜드명 제거 (2026-05-29)

### main_automation.py
- **변경 전**: `T_DB`, `T_BIT`, `T_COMP`가 드론박스/빛드론/다다사 등으로 고정 하드코딩
- **변경 후**: 환경변수 `MY_BRAND_1`, `MY_BRAND_2`, `COMPETITORS`에서 동적 로드
- **변경 전**: 쇼핑몰명 정규화 시 `"드론박스"`, `"빛드론"`, `"다다사"`, `"효로로"`, `"드론뷰"` 고정 문자열 사용
- **변경 후**: `T_DB[0]`, `T_BIT[0]`, `T_COMP` 리스트 기반 동적 정규화
- **변경 전**: 경쟁사 플래그 `is_da`, `is_hr`, `is_dv` 하드코딩
- **변경 후**: `is_comp_1`, `is_comp_2`, `is_comp_N` 동적 생성 (`COMPETITORS` 리스트 기준)

### streamlit_app.py
- 사이드바 브랜드 입력 기본값을 빈 문자열로 변경 (이전: 드론박스/빛드론 고정)
- `brand1_label`, `brand2_label` 전역 변수 추가 — 브랜드 첫 번째 이름을 UI 레이블에 사용
- Dashboard 메트릭 라벨: `"드론박스 (1-3위)"` → `f"{brand1_label} (1-3위)"`
- Dashboard 축하 이펙트: 하드코딩 패턴 → 동적 브랜드 패턴
- Dashboard HTML 리포트 제목: 브랜드명 변수화
- 안내 메시지 "현재 자사 브랜드(드론박스/빛드론) 중..." → 변수 사용
- SEO태그 생성기 `save_mall_name` 기본값: `"드론박스"` → `brand1_label`
- AI 프롬프트 "당사(드론박스/빛드론)" → `f"당사({brand1_label}/{brand2_label})"`
- Run & Sync 경쟁사 플래그 `is_da`, `is_hr`, `is_dv` → 동적 `is_comp_N`
- `get_clean_df` 정규화 로직: 하드코딩 문자열 비교 → 브랜드 변수 기반 비교

---

## ✅ 작업 2 — 설정 온보딩 UX 구성 (2026-05-29)

- `load_config()` / `save_config()` 함수 추가 — `.nshopping_config.json` 파일 기반 로컬 설정 저장
- `get_secret()` 함수 업그레이드 — Streamlit secrets → 로컬 config.json 순서로 fallback
- 온보딩 마법사 추가: `NAVER_CLIENT_ID` 또는 `MY_BRAND_1`이 없으면 앱 진입 전 설정 화면 표시
  - 네이버 검색 API / 광고 API / 브랜드 정보 / GAS 연동 / Gemini API 한 번에 입력
  - 저장 시 `.nshopping_config.json` 생성, 이후 `st.rerun()`으로 앱 정상 진입
  - "나중에 설정" 버튼으로 온보딩 건너뛰기 가능

---

## ✅ 작업 3 — 키워드 관리 UI 추가 (2026-05-29)

- 사이드바 메뉴에 `"⚙️ 키워드 관리"` 항목 추가
- 기능:
  - `keywords.txt` 현재 내용 텍스트 에디터로 편집 (한 줄에 하나씩)
  - 빠른 추가 입력창 (즉시 목록에 반영)
  - `💾 저장` 버튼으로 `keywords.txt` 덮어쓰기
  - `🔄 취소` 버튼으로 저장된 내용으로 되돌리기
  - `📥 다운로드` 버튼으로 현재 편집 내용 다운로드

---

## ✅ 작업 4 — 데이터 격리 구조 적용 (2026-05-29)

- `get_clean_df()` 함수 리팩터링: 쇼핑몰명 정규화 기준을 환경변수 기반 브랜드/경쟁사 목록으로 변경
  - 브랜드1 계열 → `brand1_label`로 통일 (예: "DroneBox Inc" → "MyBrand")
  - 브랜드2 계열 → `brand2_label`로 통일
  - 경쟁사 계열 → 경쟁사 이름 그대로 유지
- 각 회사가 자신의 `APPS_SCRIPT_URL`을 설정하여 데이터가 자사 Google Sheets에만 저장되도록 구조 확인 완료
- 경쟁사 플래그 컬럼명을 동적 생성(`is_comp_N`)으로 변경 — GAS 스크립트도 동일하게 업데이트 필요

---

## ✅ 작업 5 — README 및 배포 가이드 작성 (2026-05-29)

- `README.md` 전면 재작성 (기존 Streamlit 기본 템플릿 → 실제 사용 가이드)
- 포함 내용:
  - 주요 기능 목록
  - 로컬 실행 / Streamlit Cloud 배포 방법
  - 환경 변수 전체 목록 (필수/선택 구분)
  - 네이버 검색 API / 광고 API 발급 방법 링크 포함
  - Google Apps Script 연동 방법
  - GitHub Actions 자동 크롤링 설정 방법

---

## 주의사항 / 후속 작업

| 항목 | 설명 |
|---|---|
| GAS 스크립트 업데이트 | 경쟁사 플래그 컬럼이 `is_da/is_hr/is_dv` → `is_comp_1/2/3`으로 변경됨. GAS 측 컬럼 매핑 수정 필요 |
| `.nshopping_config.json` gitignore | API 키가 담긴 설정 파일이 공개 저장소에 올라가지 않도록 `.gitignore`에 추가 필요 |
| Streamlit Cloud | 클라우드 환경에서는 파일 쓰기 불가 → Secrets 사용 권장. 온보딩 마법사의 "저장" 버튼은 로컬 전용 |
