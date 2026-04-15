# 🌱 Life Coach Agent

Streamlit UI + 웹 검색 + 파일 검색(Vector Store) 기능을 갖춘 AI 라이프 코치 에이전트.

## 기술 스택

| 구성요소 | 기술 |
|---------|------|
| UI | Streamlit (`st.chat_input`, `st.chat_message`) |
| Agent | OpenAI Agents SDK (`Agent` + `Runner` + `FileSearchTool`) |
| 웹 검색 | DuckDuckGo (`@function_tool`로 래핑) |
| 파일 검색 | OpenAI Vector Store + `FileSearchTool` |
| 일기 기록 | `save_journal_entry` → Vector Store에 자동 저장 |
| 세션 메모리 | `st.session_state` + `to_input_list()` |
| 패키지 관리 | uv |

## 설치 및 실행

```bash
# 1. 프로젝트 디렉토리 이동
cd life-coach-agent

# 2. 의존성 설치
uv sync

# 3. 환경변수 설정
cp .env .env
# .env 파일을 열어 OPENAI_API_KEY 값 설정

# 4. Vector Store 초기 설정 (최초 1회)
#    - 기본 샘플 목표 문서(data/my_goals.md) 업로드
uv run python setup_vector_store.py

#    - 또는 커스텀 파일 지정
uv run python setup_vector_store.py my_plan.pdf journal.txt

# 5. 앱 실행
uv run streamlit run app.py
```

## 파일 구조

```
life-coach-agent/
├── pyproject.toml           # uv 프로젝트 설정 + 의존성
├── app.py                   # Streamlit 메인 앱 (UI + 사이드바 파일 관리)
├── agent.py                 # Life Coach Agent 정의 (FileSearchTool 포함)
├── tools.py                 # 웹 검색 + 일기 기록 도구
├── setup_vector_store.py    # Vector Store 초기 설정 스크립트
├── data/
│   └── my_goals.md          # 샘플 목표/일기 문서
├── .env.example             # 환경변수 템플릿
└── README.md
```

## 동작 흐름

1. **초기 설정**: `setup_vector_store.py`로 Vector Store 생성 + 목표 문서 업로드
2. **채팅**: 사용자 메시지 → Agent가 도구 선택
   - 목표/진행 상황 질문 → `file_search`로 Vector Store 검색
   - 조언/팁 요청 → `web_search`로 최신 정보 검색
   - 활동/감정 공유 → `save_journal_entry`로 일기 저장
3. **파일 관리**: 사이드바에서 PDF/TXT/MD/DOCX 파일 추가 업로드 가능
4. **진행 추적**: 저장된 일기와 목표를 기반으로 시간에 따른 변화 분석

## 예시 대화

```
User: 내 운동 목표 달성은 잘 되어가고 있어?
Coach: [파일 검색 수행] → 목표: 주 3회 운동. 1/10 기준 3회 달성, 1/15은 2회.
Coach: [웹 검색: "운동 루틴 유지 방법"] → 최신 팁 결합하여 조언

User: 오늘 러닝 30분 하고 스쿼트 50개 했어! 기분 좋아
Coach: [일기 기록] → Vector Store에 저장
Coach: 꾸준히 하고 계시네요! 기록을 보면 점점 운동 빈도가 올라가고 있어요.
```
