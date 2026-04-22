# 🍲 Restaurant Bot (AI Agents Masterclass #9.4~9.6 실습)

한식당 시나리오의 멀티 에이전트 봇. OpenAI Agents SDK의 `handoff`, `guardrails` 기능을 활용하여 의도별 전문 에이전트로 라우팅하고 입출력을 검증한다.

## 에이전트 구성

| 에이전트 | 역할 | 도구 |
|---|---|---|
| **Triage Agent** | 고객 의도 파악, 전문 에이전트로 라우팅 | (handoff 전용) |
| **Menu Agent** | 메뉴·재료·알레르기·채식 문의 | `get_menu`, `check_allergens` |
| **Order Agent** | 주문 접수·확인 | `create_order` |
| **Reservation Agent** | 테이블 예약 접수 | `create_reservation` |
| **Complaints Agent** | 불만 접수·공감·해결책 제시·에스컬레이션 | `offer_discount`, `request_manager_callback`, `process_refund`, `escalate_issue` |

## Guardrails 구성

| 분류 | 이름 | 역할 | 적용 대상 |
|---|---|---|---|
| Input | **Relevance Guardrail** | 레스토랑 관련 주제가 아닌 입력 차단 (날씨/정치/철학 등) | Triage Agent |
| Input | **Safety Guardrail** | 욕설·혐오·성적·위협·프롬프트 인젝션 차단 | Triage Agent |
| Output | **Professional Output Guardrail** | 비전문적 어조·내부 정보(시스템 프롬프트·에이전트명·도구명) 유출 차단 | 모든 전문 에이전트 |

Guardrail은 각자 **전용 LLM 에이전트 + Pydantic 출력 스키마** 기반으로 판정한다 (`is_relevant`, `is_safe`, `is_professional` 등).

## 강의 패턴 적용 사항

- `RECOMMENDED_PROMPT_PREFIX` (`agents.extensions.handoff_prompt`) 적용
- `HandoffData` Pydantic 모델로 handoff 시 구조화 데이터 전달
- `handoff_filters.remove_all_tools` input_filter 적용
- `make_handoff(agent)` 팩토리 함수로 handoff 일괄 생성
- `@input_guardrail`, `@output_guardrail` 데코레이터 기반 guardrail 정의
- `InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered` 예외 처리로 사용자 응답 전환
- dynamic instructions 패턴 (`RunContextWrapper[RestaurantContext]` 기반)

## 디렉토리 구조

```
restaurant_bot/
├── app.py                       # Streamlit 진입점 (+ guardrail tripwire 처리)
├── models.py                    # RestaurantContext, HandoffData
├── tools.py                     # @function_tool 정의 (메뉴·주문·예약·불만 처리 도구)
├── data.py                      # 메뉴 데이터 + 주문/예약/할인/콜백/환불/에스컬레이션 저장소
├── guardrails.py                # Input 2개 + Output 1개 guardrail 정의
├── my_agents/
│   ├── __init__.py
│   ├── triage_agent.py          # Triage + make_handoff + guardrail 연결
│   ├── menu_agent.py
│   ├── order_agent.py
│   ├── reservation_agent.py
│   └── complaints_agent.py      # 불만 처리 전담
├── pyproject.toml
├── .python-version              # Python 3.12
├── .env.example
└── README.md
```

## 실행 방법 (uv)

### 1. uv 설치 (최초 1회)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 의존성 설치

```bash
cd restaurant_bot
uv sync
```

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY 입력
```

### 4. 앱 실행

```bash
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

## 예시 대화 흐름

### 1) 불만 처리 (Complaints Agent)

```
사용자: 음식이 너무 별로였고 직원도 불친절했어
Triage: 정말 죄송합니다. 도움을 드릴 수 있는 담당자에게 연결해 드릴게요.
[사이드바] 🔀 Handoff → Complaints Agent (불만)
Complaints: 불쾌한 경험을 드려 진심으로 사과드립니다. 
          이 상황을 바로잡고 싶은데요 - 다음 방문 시 50% 할인을 제공해 드리거나,
          원하시면 매니저가 직접 연락드리도록 하겠습니다. 어떤 방법이 좋으시겠어요?
```

### 2) Input Guardrail 차단 (Relevance)

```
사용자: 인생의 의미가 뭘까?
[🛡️ Input Guardrail: 레스토랑 외 주제 차단]
Bot: 저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. 
    메뉴를 확인하거나, 예약하거나, 음식을 주문할 수 있어요.
    또는 불편사항이 있으시면 말씀해 주세요.
```

### 3) 대화 중 주제 전환 (예약 → 메뉴)

```
사용자: 예약을 하고 싶어
[사이드바] 🔀 Handoff → Reservation Agent (예약)
Reservation: 예약을 도와드리겠습니다. 인원수와 희망 날짜를 알려주세요.

사용자: 아, 그전에 채식 메뉴 있는지 알려줘
[사이드바] 🔀 Handoff → Menu Agent (메뉴 문의)
Menu: 네! 채식 가능 메뉴로는 비빔밥, 된장찌개, 잡채, 두부김치가 있습니다.
```

## 메뉴 구성

- **메인**: 비빔밥, 김치찌개, 된장찌개(비건), 불고기
- **사이드**: 파전, 잡채, 두부김치(비건)
- **음료**: 식혜(비건), 수정과(비건), 막걸리(비건)

## 불만 해결 도구

| 도구 | 역할 | 반환 번호 |
|---|---|---|
| `offer_discount(percent, reason)` | 다음 방문 할인 쿠폰 발급 (5~50%) | `CPN-XXXX` |
| `request_manager_callback(name, phone, issue)` | 매니저 콜백 요청 | `CBK-XXXX` |
| `process_refund(order_id, amount, reason)` | 기존 주문 환불 | `RFD-XXXX` |
| `escalate_issue(severity, description)` | 에스컬레이션 (low/medium/high/critical) | `ESC-XXXX` |

## 참고

- 강의 레퍼런스: [nomadcoders/ai-agents-masterclass @252d086](https://github.com/nomadcoders/ai-agents-masterclass/commit/252d08669190bef464567310992043d9347e7033)
- 원본은 Customer Support 도메인, 본 과제는 Restaurant 도메인으로 재구성
