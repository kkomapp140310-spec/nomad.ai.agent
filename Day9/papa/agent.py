"""
Life Coach Agent 모듈
"""

from agents import Agent, Runner
from tools import web_search

# 라이프 코치 시스템 프롬프트
LIFE_COACH_INSTRUCTIONS = """당신은 따뜻하고 전문적인 라이프 코치입니다.

## 역할
- 사용자의 목표 달성, 습관 형성, 자기개발을 돕는 코치
- 격려와 공감을 기반으로 실질적인 조언 제공
- 과학적 근거가 있는 방법론을 우선 추천

## 행동 지침
1. 사용자의 상황에 공감하며 시작하세요
2. 웹 검색 도구를 적극 활용하여 근거 있는 조언을 제공하세요
3. 조언은 구체적이고 실행 가능한 단계로 나누어 설명하세요
4. 사용자가 이미 시도한 것을 인정하고 칭찬하세요
5. 한 번에 너무 많은 변화를 권하지 마세요 - 작은 시작을 강조하세요

## 응답 스타일
- 한국어로 답변하세요
- 친근하지만 전문적인 톤을 유지하세요
- 이모지는 적절히 사용하세요 (과도하지 않게)
- 핵심 조언은 명확하게 구분하여 전달하세요

## 주요 코칭 영역
- 습관 형성 및 루틴 구축
- 목표 설정 및 달성 전략
- 시간 관리 및 생산성
- 동기부여 및 마인드셋
- 스트레스 관리 및 웰빙
- 대인관계 및 커뮤니케이션
"""

# 에이전트 정의
life_coach = Agent(
    name="Life Coach",
    instructions=LIFE_COACH_INSTRUCTIONS,
    tools=[web_search],
)


async def run_agent(user_input: str, history: list | None = None) -> str:
    """에이전트를 실행하고 응답을 반환한다.

    Args:
        user_input: 사용자 입력 메시지
        history: 이전 대화 이력 (to_input_list() 형식)

    Returns:
        에이전트의 응답 텍스트
    """
    try:
        # 대화 이력이 있으면 이력 + 새 입력을 합쳐서 전달
        if history:
            input_data = history + [{"role": "user", "content": user_input}]
        else:
            input_data = user_input

        result = await Runner.run(
            starting_agent=life_coach,
            input=input_data,
        )

        return result.final_output, result.to_input_list()

    except Exception as e:
        error_msg = f"에이전트 실행 중 오류가 발생했습니다: {e}"
        # 오류 시에도 이력 유지를 위해 수동으로 구성
        fallback_history = history or []
        fallback_history.append({"role": "user", "content": user_input})
        fallback_history.append({"role": "assistant", "content": error_msg})
        return error_msg, fallback_history
