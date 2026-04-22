"""
용도: 에이전트가 사용할 function tools 정의
사용법: from tools import get_menu, check_allergens, create_order, create_reservation
"""

from datetime import datetime
from agents import function_tool
from data import (
    MENU,
    ORDERS,
    RESERVATIONS,
    DISCOUNTS,
    CALLBACKS,
    REFUNDS,
    ESCALATIONS,
    find_menu_item,
)


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


# ─── 불만 처리 도구 ────────────────────────────────────────────────────
@function_tool
def offer_discount(percent: int, reason: str) -> str:
    """
    다음 방문 시 사용 가능한 할인 쿠폰을 발급합니다.

    Args:
        percent: 할인율 (5~50 사이 정수, %)
        reason: 발급 사유 (예: "서비스 불만", "음식 품질 문제")
    """
    try:
        if percent < 5 or percent > 50:
            return "할인율은 5%~50% 범위 내에서만 발급 가능합니다."

        coupon_id = f"CPN-{len(DISCOUNTS) + 1:04d}"
        coupon = {
            "coupon_id": coupon_id,
            "percent": percent,
            "reason": reason,
            "issued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        DISCOUNTS.append(coupon)

        return (
            f"할인 쿠폰이 발급되었습니다.\n"
            f"  - 쿠폰번호: {coupon_id}\n"
            f"  - 할인율: 다음 방문 시 {percent}% 할인\n"
            f"  - 유효기간: 발급일로부터 3개월"
        )

    except Exception as e:
        return f"쿠폰 발급 중 오류가 발생했습니다: {e}"


@function_tool
def request_manager_callback(name: str, phone: str, issue: str) -> str:
    """
    매니저 콜백을 요청합니다.

    Args:
        name: 고객명
        phone: 연락처 (예: "010-1234-5678")
        issue: 불만 내용 요약
    """
    try:
        if not phone or len(phone) < 9:
            return "유효한 연락처를 입력해주세요."

        callback_id = f"CBK-{len(CALLBACKS) + 1:04d}"
        callback = {
            "callback_id": callback_id,
            "name": name,
            "phone": phone,
            "issue": issue,
            "status": "대기",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        CALLBACKS.append(callback)

        return (
            f"매니저 콜백이 접수되었습니다.\n"
            f"  - 접수번호: {callback_id}\n"
            f"  - {name}님 ({phone})\n"
            f"  - 영업시간 내 24시간 이내에 연락드리겠습니다."
        )

    except Exception as e:
        return f"콜백 요청 처리 중 오류가 발생했습니다: {e}"


@function_tool
def process_refund(order_id: str, amount: int, reason: str) -> str:
    """
    기존 주문에 대한 환불을 처리합니다.

    Args:
        order_id: 주문번호 (예: "ORD-0001")
        amount: 환불 금액 (원)
        reason: 환불 사유
    """
    try:
        # 주문 조회
        target_order = None
        for order in ORDERS:
            if order["order_id"] == order_id:
                target_order = order
                break

        if not target_order:
            return f"주문번호 '{order_id}'를 찾을 수 없습니다. 주문번호를 다시 확인해주세요."

        if amount < 1:
            return "환불 금액은 1원 이상이어야 합니다."

        if amount > target_order["total"]:
            return (
                f"환불 금액이 주문 총액을 초과합니다. "
                f"(주문 총액: {target_order['total']:,}원, 요청 환불: {amount:,}원)"
            )

        refund_id = f"RFD-{len(REFUNDS) + 1:04d}"
        refund = {
            "refund_id": refund_id,
            "order_id": order_id,
            "amount": amount,
            "reason": reason,
            "status": "처리중",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        REFUNDS.append(refund)

        return (
            f"환불 요청이 접수되었습니다.\n"
            f"  - 환불번호: {refund_id}\n"
            f"  - 원주문: {order_id}\n"
            f"  - 환불액: {amount:,}원\n"
            f"  - 처리기간: 영업일 기준 3~5일"
        )

    except Exception as e:
        return f"환불 처리 중 오류가 발생했습니다: {e}"


@function_tool
def escalate_issue(severity: str, description: str) -> str:
    """
    심각한 문제를 상위 관리자에게 에스컬레이션합니다.

    Args:
        severity: 심각도 ("low", "medium", "high", "critical")
        description: 문제 상세 설명
    """
    try:
        valid_severities = {"low", "medium", "high", "critical"}
        if severity.lower() not in valid_severities:
            return f"severity는 {', '.join(valid_severities)} 중 하나여야 합니다."

        escalation_id = f"ESC-{len(ESCALATIONS) + 1:04d}"
        escalation = {
            "escalation_id": escalation_id,
            "severity": severity.lower(),
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        ESCALATIONS.append(escalation)

        # 심각도별 후속 조치 메시지
        response_time = {
            "low": "영업일 기준 3일 이내",
            "medium": "영업일 기준 1일 이내",
            "high": "당일 내",
            "critical": "즉시",
        }[severity.lower()]

        return (
            f"해당 사안이 관리자에게 에스컬레이션되었습니다.\n"
            f"  - 접수번호: {escalation_id}\n"
            f"  - 심각도: {severity.upper()}\n"
            f"  - 대응시한: {response_time}"
        )

    except Exception as e:
        return f"에스컬레이션 처리 중 오류가 발생했습니다: {e}"
