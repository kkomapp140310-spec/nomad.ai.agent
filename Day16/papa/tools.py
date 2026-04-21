"""
용도: 에이전트가 사용할 function tools 정의
사용법: from tools import get_menu, check_allergens, create_order, create_reservation
"""

from datetime import datetime
from agents import function_tool
from data import MENU, ORDERS, RESERVATIONS, find_menu_item


@function_tool
def get_menu(category: str | None = None) -> str:
    """
    메뉴 정보를 조회합니다.

    Args:
        category: 카테고리명 ("메인", "사이드", "음료"). None이면 전체 메뉴 반환.
    """
    try:
        if category and category in MENU:
            items = MENU[category]
            lines = [f"[{category}]"]
            for item in items:
                tags = []
                if item["vegan"]:
                    tags.append("비건")
                elif item["vegetarian"]:
                    tags.append("채식")
                tag_str = f" ({', '.join(tags)})" if tags else ""
                lines.append(f"  - {item['name']}{tag_str}: {item['price']:,}원 - {item['desc']}")
            return "\n".join(lines)

        # 전체 메뉴
        lines = []
        for cat, items in MENU.items():
            lines.append(f"\n[{cat}]")
            for item in items:
                tags = []
                if item["vegan"]:
                    tags.append("비건")
                elif item["vegetarian"]:
                    tags.append("채식")
                tag_str = f" ({', '.join(tags)})" if tags else ""
                lines.append(f"  - {item['name']}{tag_str}: {item['price']:,}원 - {item['desc']}")
        return "\n".join(lines).strip()

    except Exception as e:
        return f"메뉴 조회 중 오류가 발생했습니다: {e}"


@function_tool
def check_allergens(item_name: str) -> str:
    """
    특정 메뉴의 알레르기 성분, 재료, 채식/비건 여부를 확인합니다.

    Args:
        item_name: 메뉴명 (예: "비빔밥", "파전")
    """
    try:
        item = find_menu_item(item_name)
        if not item:
            return f"'{item_name}' 메뉴를 찾을 수 없습니다. 다른 메뉴명으로 시도해주세요."

        allergens = ", ".join(item["allergens"]) if item["allergens"] else "없음"
        ingredients = ", ".join(item["ingredients"])
        diet = "비건" if item["vegan"] else ("채식 가능" if item["vegetarian"] else "육류/해산물 포함")

        return (
            f"[{item['name']}] 상세정보\n"
            f"  - 재료: {ingredients}\n"
            f"  - 알레르기 성분: {allergens}\n"
            f"  - 식단 구분: {diet}"
        )

    except Exception as e:
        return f"알레르기 정보 조회 중 오류가 발생했습니다: {e}"


@function_tool
def create_order(items: list[str], table_no: int | None = None) -> str:
    """
    주문을 생성합니다.

    Args:
        items: 주문할 메뉴명 리스트 (예: ["비빔밥", "막걸리"])
        table_no: 테이블 번호 (선택)
    """
    try:
        if not items:
            return "주문 항목이 없습니다. 최소 한 가지 메뉴를 선택해주세요."

        # 메뉴 검증 및 총액 계산
        validated = []
        total = 0
        not_found = []
        for name in items:
            item = find_menu_item(name)
            if item:
                validated.append(item)
                total += item["price"]
            else:
                not_found.append(name)

        if not_found:
            return f"다음 메뉴를 찾을 수 없습니다: {', '.join(not_found)}. 정확한 메뉴명을 확인해주세요."

        # 주문 저장
        order_id = f"ORD-{len(ORDERS) + 1:04d}"
        order = {
            "order_id": order_id,
            "items": [i["name"] for i in validated],
            "total": total,
            "table_no": table_no,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        ORDERS.append(order)

        table_str = f"테이블 {table_no}번, " if table_no else ""
        return (
            f"주문이 접수되었습니다.\n"
            f"  - 주문번호: {order_id}\n"
            f"  - {table_str}메뉴: {', '.join(order['items'])}\n"
            f"  - 합계: {total:,}원"
        )

    except Exception as e:
        return f"주문 처리 중 오류가 발생했습니다: {e}"


@function_tool
def create_reservation(name: str, party_size: int, date: str, time: str) -> str:
    """
    테이블 예약을 생성합니다.

    Args:
        name: 예약자명
        party_size: 인원수
        date: 예약일 (YYYY-MM-DD)
        time: 예약시간 (HH:MM)
    """
    try:
        # 입력 검증
        if party_size < 1 or party_size > 20:
            return "인원수는 1명 이상 20명 이하로 예약 가능합니다."

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return f"날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요 (입력값: {date})"

        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return f"시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력해주세요 (입력값: {time})"

        # 예약 저장
        reservation_id = f"RSV-{len(RESERVATIONS) + 1:04d}"
        reservation = {
            "reservation_id": reservation_id,
            "name": name,
            "party_size": party_size,
            "date": date,
            "time": time,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        RESERVATIONS.append(reservation)

        return (
            f"예약이 확정되었습니다.\n"
            f"  - 예약번호: {reservation_id}\n"
            f"  - 예약자: {name}님\n"
            f"  - 일시: {date} {time}\n"
            f"  - 인원: {party_size}명"
        )

    except Exception as e:
        return f"예약 처리 중 오류가 발생했습니다: {e}"
