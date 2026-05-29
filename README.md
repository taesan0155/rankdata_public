# 🛒 네이버 쇼핑 통합 관제 시스템

네이버 쇼핑 키워드별 순위를 자동으로 수집·분석하고, 경쟁사 동향 및 AI 기반 SEO 전략을 제공하는 Streamlit 웹앱입니다.

> **누구나 쓸 수 있습니다.** 자신의 브랜드/경쟁사 정보와 네이버 API 키만 있으면 됩니다.

---

## 주요 기능

- 네이버 쇼핑 키워드 순위 실시간 수집
- 자사 브랜드 1~3위 노출 현황 Dashboard
- 일자별 순위 추이 차트 (히트맵 / 선그래프 / AI 예측 트렌드)
- 경쟁사 점유율 정밀 분석
- 틈새 키워드 발굴기 (네이버 광고 API 연동)
- SEO & GEO 메타태그 자동 생성 (Gemini AI)
- Google Sheets 자동 동기화 (Apps Script 연동)
- 키워드 관리 UI (keywords.txt 편집)

---

## 빠른 시작

### 1. 저장소 Fork 또는 Clone

```bash
git clone https://github.com/your-org/nshopping-manager.git
cd nshopping-manager
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

**로컬 실행**: 앱을 처음 실행하면 초기 설정 마법사가 나타납니다. 아래 항목을 입력하면 `.nshopping_config.json`에 자동 저장됩니다.

**Streamlit Cloud 배포**: 앱 설정 → Secrets에 아래 키를 등록하세요.

| 키 | 설명 | 필수 |
|---|---|---|
| `NAVER_CLIENT_ID` | 네이버 검색 API Client ID | ✅ |
| `NAVER_CLIENT_SECRET` | 네이버 검색 API Secret | ✅ |
| `NAVER_AD_API_KEY` | 네이버 광고 API Key | ✅ |
| `NAVER_AD_SECRET_KEY` | 네이버 광고 API Secret | ✅ |
| `NAVER_CUSTOMER_ID` | 네이버 광고 Customer ID | ✅ |
| `MY_BRAND_1` | 내 브랜드 1 (쉼표 구분, 예: `MyBrand, My Brand`) | ✅ |
| `MY_BRAND_2` | 내 브랜드 2 (없으면 공백) | |
| `COMPETITORS` | 경쟁사 목록 (쉼표 구분) | |
| `APPS_SCRIPT_URL` | Google Apps Script 웹앱 URL | |
| `APPS_SCRIPT_TOKEN` | GAS 인증 토큰 | |
| `GEMINI_API_KEY` | Google Gemini API Key (AI 기능 사용 시) | |
| `WORKS_CLIENT_ID` | 네이버웍스 API Client ID | |
| `WORKS_CLIENT_SECRET` | 네이버웍스 API Client Secret | |
| `WORKS_SERVICE_ACCOUNT` | 네이버웍스 서비스 계정 (Service Account) | |
| `WORKS_PRIVATE_KEY` | 네이버웍스 RSA Private Key (개인키) | |
| `WORKS_BOT_ID` | 네이버웍스 알림 봇 ID | |
| `WORKS_ROOM_ID` | 네이버웍스 수신 대화방 Room ID | |

### 4. 앱 실행

```bash
streamlit run streamlit_app.py
```

---

## 네이버 API 발급 방법

### 검색 API (NAVER_CLIENT_ID / SECRET)
1. [네이버 개발자 센터](https://developers.naver.com/apps/#/register) 접속
2. 애플리케이션 등록 → 사용 API: **쇼핑** 선택
3. Client ID / Secret 복사

### 광고 API (AD_API_KEY / SECRET / CUSTOMER_ID)
1. [네이버 광고](https://searchad.naver.com/) 로그인
2. 도구 → API 사용 관리 → API 키 발급
3. API Key, Secret Key, 고객 ID 복사

### 네이버웍스 봇 API (WORKS_CLIENT_ID / SECRET / SA / PKEY / BOT_ID / ROOM_ID)
1. [네이버웍스 Developers Console](https://developers.worksmobile.com/) 접속 및 로그인
2. **API 2.0 ➡️ App 추가** 클릭하여 앱 생성 후, Client ID 및 Client Secret 복사
3. **OAuth Scopes**에 `bot` 및 `bot.message` 권한 선택 후 저장
4. **Service Account ➡️ 서비스 계정 추가** 클릭하여 메일 형식의 주소(Service Account) 복사
5. **Private Key ➡️ 발행** 클릭하여 개인키 파일(`.key`)을 다운로드하고 에디터로 열어 텍스트 전체(`-----BEGIN PRIVATE KEY-----` 포함)를 복사
6. **Bot ➡️ 등록**에서 봇을 등록하고 발급된 Bot ID 복사
7. 생성한 봇을 메신저 대화방에 멤버로 초대하고, 해당 대화방의 Room ID를 확인하여 입력

---

## Google Sheets 연동 (선택)

수집 데이터를 Google Sheets에 자동 저장하려면 Google Apps Script 설정이 필요합니다.

1. Google Sheets 새 문서 생성
2. 확장 프로그램 → Apps Script 편집기 열기
3. 스크립트 작성 후 웹앱으로 배포 (액세스: 모든 사용자)
4. 웹앱 URL을 `APPS_SCRIPT_URL`에 입력

---

## 자동 크롤링 (GitHub Actions)

`.github/workflows/daily_crawl.yml`이 매일 KST 06:00에 자동 실행됩니다.

GitHub 저장소 설정 → Secrets and variables → Actions에서 아래 시크릿을 등록하세요:
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`
- `NAVER_AD_API_KEY`, `NAVER_AD_SECRET_KEY`, `NAVER_CUSTOMER_ID`
- `MY_BRAND_1`, `MY_BRAND_2`, `COMPETITORS`
- `APPS_SCRIPT_URL`, `APPS_SCRIPT_TOKEN`

---

## Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 연동 후 저장소 선택
3. Main file: `streamlit_app.py`
4. Advanced settings → Secrets에 환경변수 입력

---

## 라이선스

MIT License
