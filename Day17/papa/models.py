"""
용도: 레스토랑 봇 컨텍스트 및 handoff 데이터 모델
사용법: from models import RestaurantContext, HandoffData
"""

from pydantic import BaseModel


class RestaurantContext(BaseModel):
    """고객 컨텍스트 (강의의 UserAccountContext 대응)"""

    name: str
    is_regular: bool = False  # 단골 여부


class HandoffData(BaseModel):
    """handoff 시 전달되는 구조화 데이터 (강의 패턴)"""

    to_agent_name: str
    request_type: str  # 예: "메뉴 문의", "주문", "예약"
    description: str
    reason: str
