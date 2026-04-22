"""
용도: Restaurant Bot 샘플 데이터 및 임시 저장소
사용법: from data import MENU, ORDERS, RESERVATIONS
"""

# 메뉴 데이터 (한식당 컨셉)
# - vegetarian: 채식 가능 여부
# - vegan: 완전 채식 여부
# - allergens: 알레르기 유발 성분
MENU = {
    "메인": [
        {
            "name": "비빔밥",
            "price": 12000,
            "desc": "각종 나물과 고추장을 곁들인 밥",
            "vegetarian": True,
            "vegan": False,  # 계란 포함
            "allergens": ["계란", "대두"],
            "ingredients": ["밥", "시금치", "콩나물", "무채", "당근", "계란", "고추장"],
        },
        {
            "name": "김치찌개",
            "price": 10000,
            "desc": "돼지고기와 묵은지로 끓인 찌개",
            "vegetarian": False,
            "vegan": False,
            "allergens": ["돼지고기", "대두"],
            "ingredients": ["김치", "돼지고기", "두부", "파", "고춧가루"],
        },
        {
            "name": "된장찌개",
            "price": 9000,
            "desc": "두부와 야채가 들어간 구수한 찌개",
            "vegetarian": True,
            "vegan": True,
            "allergens": ["대두"],
            "ingredients": ["된장", "두부", "애호박", "감자", "양파", "파"],
        },
        {
            "name": "불고기",
            "price": 18000,
            "desc": "양념에 재운 소고기 구이",
            "vegetarian": False,
            "vegan": False,
            "allergens": ["소고기", "대두", "참깨"],
            "ingredients": ["소고기", "간장", "설탕", "배", "마늘", "참기름"],
        },
    ],
    "사이드": [
        {
            "name": "파전",
            "price": 14000,
            "desc": "파와 해물을 넣은 부침개",
            "vegetarian": False,
            "vegan": False,
            "allergens": ["밀", "계란", "갑각류", "오징어"],
            "ingredients": ["파", "새우", "오징어", "밀가루", "계란"],
        },
        {
            "name": "잡채",
            "price": 11000,
            "desc": "당면과 야채를 볶은 요리",
            "vegetarian": True,
            "vegan": False,  # 기본 계란 지단 포함
            "allergens": ["대두", "참깨", "계란"],
            "ingredients": ["당면", "시금치", "당근", "양파", "버섯", "간장", "계란"],
        },
        {
            "name": "두부김치",
            "price": 9000,
            "desc": "데친 두부에 볶은 김치",
            "vegetarian": True,
            "vegan": True,
            "allergens": ["대두"],
            "ingredients": ["두부", "김치", "파", "참기름"],
        },
    ],
    "음료": [
        {
            "name": "식혜",
            "price": 4000,
            "desc": "전통 쌀 음료",
            "vegetarian": True,
            "vegan": True,
            "allergens": [],
            "ingredients": ["쌀", "엿기름", "설탕"],
        },
        {
            "name": "수정과",
            "price": 4000,
            "desc": "계피와 생강으로 만든 음료",
            "vegetarian": True,
            "vegan": True,
            "allergens": [],
            "ingredients": ["계피", "생강", "설탕", "곶감"],
        },
        {
            "name": "막걸리",
            "price": 6000,
            "desc": "전통 탁주 (1병)",
            "vegetarian": True,
            "vegan": True,
            "allergens": ["밀"],
            "ingredients": ["쌀", "누룩", "밀"],
        },
    ],
}

# 주문/예약 임시 저장소 (실제 구현 시 DB로 대체)
ORDERS: list[dict] = []
RESERVATIONS: list[dict] = []

# 불만 처리 관련 저장소
DISCOUNTS: list[dict] = []       # 할인 쿠폰 발급 이력
CALLBACKS: list[dict] = []       # 매니저 콜백 요청 이력
REFUNDS: list[dict] = []         # 환불 처리 이력
ESCALATIONS: list[dict] = []     # 에스컬레이션 이력


def find_menu_item(item_name: str) -> dict | None:
    """메뉴명으로 아이템 조회 (부분일치 허용)"""
    for category_items in MENU.values():
        for item in category_items:
            if item_name in item["name"] or item["name"] in item_name:
                return item
    return None
