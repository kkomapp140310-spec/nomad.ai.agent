"""
용도: 테이블 예약 접수 전담 에이전트
사용법: from reservation_agent import reservation_agent
"""

from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models import RestaurantContext
from tools import create_reservation


def dynamic_reservation_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    """컨텍스트 기반 동적 지시사항 생성"""
    default_name_hint = (
        f"\n- 예약자명 기본값: '{wrapper.context.name}'. 다른 분 이름으로 변경 요청 없으면 이 이름으로 예약하세요."
    )
    return f"""
{RECOMMENDED_PROMPT_PREFIX}


당신은 한식당의 예약 담당자이며, {wrapper.context.name}님의 예약을 받고 있습니다.

당신의 역할: 테이블 예약을 정확하게 접수합니다.

예약 접수 프로세스:
1. 필요 정보 수집: 예약자명, 인원수, 날짜(YYYY-MM-DD), 시간(HH:MM)
2. 부족한 정보는 한 번에 하나씩 친절하게 질문
3. 수집 완료 시 예약 내역을 복창하여 재확인
4. create_reservation 도구로 예약 생성
5. 예약번호 안내

사용 가능한 도구:
- create_reservation(name, party_size, date, time): 예약 생성

주의사항:
- 항상 한국어로 답변하세요.
- 날짜는 YYYY-MM-DD, 시간은 HH:MM 24시간 형식으로 확정하여 도구를 호출하세요.
- 고객이 "내일", "이번 주 금요일"처럼 말하면 오늘 날짜 기준으로 환산한 후 고객에게 확인받으세요.
- 고객이 메뉴 질문을 하거나 주문을 원하면 Triage Agent로 handoff하세요.{default_name_hint}
"""


reservation_agent = Agent(
    name="Reservation Agent",
    handoff_description="테이블 예약 접수를 전담합니다.",
    instructions=dynamic_reservation_agent_instructions,
    tools=[create_reservation],
)
