"""
용도: Triage Agent 정의 + handoff 생성 팩토리 + handoff 콜백
사용법: from triage_agent import triage_agent
"""

import streamlit as st
from agents import Agent, RunContextWrapper, handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import RestaurantContext, HandoffData
from menu_agent import menu_agent
from order_agent import order_agent
from reservation_agent import reservation_agent


# 에이전트명 → 사용자 친화적 표시명 매핑
AGENT_DISPLAY_NAMES = {
    "Menu Agent": "메뉴 전문가",
    "Order Agent": "주문 담당",
    "Reservation Agent": "예약 담당",
}


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    """컨텍스트 기반 동적 지시사항 생성"""
    regular_note = "(단골 고객입니다)" if wrapper.context.is_regular else ""
    return f"""
{RECOMMENDED_PROMPT_PREFIX}


당신은 한식당의 안내 담당자이며, {wrapper.context.name}님 {regular_note}을 응대하고 있습니다.
고객의 요청을 파악하고 적절한 전문 담당자에게 연결하는 것이 당신의 역할입니다.

라우팅 규칙:
- 메뉴/재료/알레르기/채식 관련 질문 → Menu Agent
- 주문 접수 요청 → Order Agent
- 테이블 예약 요청 → Reservation Agent

handoff 수행 시 HandoffData에 다음을 정확히 채우세요:
- to_agent_name: "Menu Agent" | "Order Agent" | "Reservation Agent" 중 하나
- request_type: "메뉴 문의" | "주문" | "예약" 중 하나
- description: 고객 요청 요약 (한 문장)
- reason: 해당 에이전트로 연결하는 이유 (한 문장)

주의사항:
- 항상 한국어로 답변하세요.
- 간단한 인사나 식당 소개는 직접 답변하세요.
- 고객 요청이 명확하면 불필요한 재확인 없이 즉시 handoff하세요.
- 요청이 애매한 경우에만 한 번 확인한 후 handoff하세요.
"""


def handle_handoff(
    wrapper: RunContextWrapper[RestaurantContext],
    input_data: HandoffData,
):
    """handoff 발생 시 Streamlit 사이드바에 표시 (강의 패턴)"""
    display_name = AGENT_DISPLAY_NAMES.get(input_data.to_agent_name, input_data.to_agent_name)

    # 메인 채팅 영역에도 전환 메시지 노출 (과제 요구사항)
    if "handoff_messages" not in st.session_state:
        st.session_state.handoff_messages = []
    st.session_state.handoff_messages.append(
        f"🔀 {display_name}에게 연결합니다..."
    )

    # 사이드바에 상세 정보 표시
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 🔀 Handoff")
        st.markdown(f"**대상:** {input_data.to_agent_name} ({display_name})")
        st.markdown(f"**유형:** {input_data.request_type}")
        st.markdown(f"**설명:** {input_data.description}")
        st.markdown(f"**사유:** {input_data.reason}")


def make_handoff(agent: Agent):
    """handoff 생성 팩토리 (강의 패턴)"""
    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(order_agent),
        make_handoff(reservation_agent),
    ],
)
