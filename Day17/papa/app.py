"""
용도: Streamlit 기반 Restaurant Bot 대화 UI (with Guardrails)
사용법: uv run streamlit run app.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (streamlit 실행 환경에 무관하게 모듈 import 보장)
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from dotenv import load_dotenv
import streamlit as st
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from models import RestaurantContext
from triage_agent import triage_agent

load_dotenv()


# ─── 페이지 설정 ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍲 한식당 Restaurant Bot",
    page_icon="🍲",
    layout="wide",
)

st.title("🍲 한식당 Restaurant Bot")
st.caption("메뉴 문의 · 주문 · 예약 · 불만 접수를 도와드립니다.")


# ─── 세션 상태 초기화 ──────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "handoff_messages" not in st.session_state:
    st.session_state.handoff_messages = []

if "guardrail_alerts" not in st.session_state:
    st.session_state.guardrail_alerts = []

if "customer_name" not in st.session_state:
    st.session_state.customer_name = "고객"

if "is_regular" not in st.session_state:
    st.session_state.is_regular = False


# ─── 사이드바: 고객 정보 ───────────────────────────────────────────────
with st.sidebar:
    st.header("👤 고객 정보")
    st.session_state.customer_name = st.text_input(
        "이름", value=st.session_state.customer_name
    )
    st.session_state.is_regular = st.checkbox(
        "단골 고객", value=st.session_state.is_regular
    )

    st.markdown("---")
    st.markdown("### 💡 사용 예시")
    st.markdown(
        "- 메뉴 보여줘\n"
        "- 비빔밥에 뭐 들어가?\n"
        "- 채식 메뉴 있어?\n"
        "- 비빔밥 하나 주문할게\n"
        "- 내일 저녁 7시 2명 예약\n"
        "- 음식이 너무 별로였어"
    )


# ─── 기존 메시지 렌더링 ────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ─── Guardrail tripwire 응답 생성 ──────────────────────────────────────
def guardrail_response(exc: Exception) -> str:
    """Guardrail 차단 시 고객에게 돌려줄 안내 메시지 생성"""

    # Input guardrail
    if isinstance(exc, InputGuardrailTripwireTriggered):
        guardrail_name = ""
        try:
            guardrail_name = exc.guardrail_result.guardrail.get_name()
        except Exception:
            pass

        if "relevance" in guardrail_name.lower():
            st.session_state.guardrail_alerts.append(
                "🛡️ Input Guardrail: 레스토랑 외 주제 차단"
            )
            return (
                "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. "
                "메뉴를 확인하거나, 예약하거나, 음식을 주문할 수 있어요. "
                "또는 불편사항이 있으시면 말씀해 주세요."
            )

        if "safety" in guardrail_name.lower():
            st.session_state.guardrail_alerts.append(
                "🛡️ Input Guardrail: 부적절 언어 차단"
            )
            return (
                "조금 더 정중한 표현으로 요청해 주시면 도와드리겠습니다. "
                "어떤 도움이 필요하신가요?"
            )

        # 이름 매칭 실패 시 fallback
        st.session_state.guardrail_alerts.append("🛡️ Input Guardrail: 차단")
        return (
            "죄송합니다. 해당 요청은 도와드리기 어렵습니다. "
            "메뉴, 예약, 주문, 불편사항 중 어떤 것을 도와드릴까요?"
        )

    # Output guardrail
    if isinstance(exc, OutputGuardrailTripwireTriggered):
        st.session_state.guardrail_alerts.append(
            "🛡️ Output Guardrail: 응답 재생성 필요"
        )
        return (
            "죄송합니다. 응답을 정리하는 중 문제가 있었습니다. "
            "다시 한 번 질문해 주시겠어요?"
        )

    return f"죄송합니다. 처리 중 오류가 발생했습니다: {exc}"


# ─── 메시지 송수신 ─────────────────────────────────────────────────────
async def run_agent(user_input: str) -> str:
    """Triage Agent 실행 (guardrail 예외 처리 포함)"""
    context = RestaurantContext(
        name=st.session_state.customer_name,
        is_regular=st.session_state.is_regular,
    )

    # 대화 이력을 함께 전달 (멀티턴 유지)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    history.append({"role": "user", "content": user_input})

    try:
        result = await Runner.run(
            starting_agent=triage_agent,
            input=history,
            context=context,
        )
        return result.final_output

    except InputGuardrailTripwireTriggered as e:
        return guardrail_response(e)

    except OutputGuardrailTripwireTriggered as e:
        return guardrail_response(e)

    except Exception as e:
        return f"죄송합니다. 처리 중 오류가 발생했습니다: {e}"


if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 렌더링 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 이번 턴의 handoff·guardrail 메시지 초기화
    st.session_state.handoff_messages = []
    st.session_state.guardrail_alerts = []

    # 에이전트 실행
    with st.chat_message("assistant"):
        with st.spinner("응대 중..."):
            response = asyncio.run(run_agent(prompt))

        # guardrail 차단 알림 (있으면 최상단에 표시)
        for alert in st.session_state.guardrail_alerts:
            st.warning(alert)

        # handoff 전환 메시지 (과제 요구사항)
        for handoff_msg in st.session_state.handoff_messages:
            st.info(handoff_msg)

        # 에이전트 최종 응답
        st.markdown(response)

    # 응답을 이력에 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
