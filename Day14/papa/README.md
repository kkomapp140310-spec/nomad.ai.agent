# 🌱 Life Coach Agent

Streamlit UI + 웹 검색 + 파일 검색 + 이미지 생성 기능을 갖춘 AI 라이프 코치 에이전트.

## 기술 스택

| 구성요소 | 기술 |
|---------|------|
| UI | Streamlit (`st.chat_input`, `st.chat_message`, `st.image`) |
| Agent | OpenAI Agents SDK (`Agent` + `Runner` + `FileSearchTool`) |
| 웹 검색 | DuckDuckGo (`@function_tool`) |
| 파일 검색 | OpenAI Vector Store + `FileSearchTool` |
| 이미지 생성 | OpenAI DALL-E 3 (`@function_tool`) |
| 일기 기록 | `save_journal_entry` → Vector Store 자동 저장 |
| 세션 메모리 | `st.session_state` + `to_input_list()` |
| 패키지 관리 | uv |

## 설치 및 실행

```bash
cd life-coach-agent
uv sync
cp .env.example .env            # OPENAI_API_KEY 설정
uv run python setup_vector_store.py   # Vector Store 생성 (최초 1회)
uv run streamlit run app.py
```

## 파일 구조

```
life-coach-agent/
├── pyproject.toml           # uv 프로젝트 설정 + 의존성
├── app.py                   # Streamlit 메인 앱 (채팅 UI + 이미지 렌더링 + 사이드바)
├── agent.py                 # Life Coach Agent 정의 (4개 도구 + Multi-Tool Chaining)
├── tools.py                 # 웹 검색 + 일기 기록 + 이미지 생성 도구
├── setup_vector_store.py    # Vector Store 초기 설정 스크립트
├── data/
│   ├── my_goals.md          # 샘플 목표/일기 문서
│   └── exercise_goals.txt   # 운동 목표 문서
├── .env.example
└── README.md
```

## 4가지 도구

| 도구 | 용도 | 트리거 |
|------|------|--------|
| `web_search` | 동기부여, 습관 형성 최신 정보 검색 | 조언/팁 요청 |
| `file_search` | 개인 목표, 일기, 진행 기록 조회 | 목표 확인/진행 상황 질문 |
| `save_journal_entry` | 활동/감정을 Vector Store에 기록 | 사용자가 활동 공유 |
| `generate_image` | 비전 보드, 축하 카드, 동기부여 포스터 생성 | 이미지/비전보드 요청, 목표 달성 보고 |

## 이미지 스타일

| 스타일 | 설명 | 사이즈 |
|--------|------|--------|
| 비전보드 | 목표를 콜라주 형태로 시각화 | 1792x1024 (가로) |
| 동기부여포스터 | 핵심 메시지 + 배경 이미지 | 1024x1792 (세로) |
| 축하카드 | 목표 달성 축하 | 1024x1024 |
| 진행상황 | 성장 여정 인포그래픽 | 1792x1024 (가로) |
| 마일스톤 | 단계 달성 배지/메달 | 1024x1024 |

## 도구 조합 시나리오

```
비전 보드 요청:
  file_search(목표) → 정리 → generate_image(비전보드)

목표 달성 축하:
  축하 메시지 → save_journal_entry(기록) → generate_image(축하카드)

진행 상황 리뷰:
  file_search(일기) → 분석 → web_search(팁) → generate_image(진행상황)

슬럼프 극복:
  file_search(성공기록) → web_search(동기부여) → generate_image(동기부여포스터)
```
