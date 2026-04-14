"""
웹 검색 도구 (Web Search Tool)
- 용도: Life Coach Agent가 동기부여, 자기개발, 습관 형성 관련 정보를 검색
- 사용법: agent.py에서 tools=[web_search]로 등록
- 검색 엔진: DuckDuckGo (API 키 불필요)
"""

from agents import function_tool
from duckduckgo_search import DDGS


@function_tool
def web_search(query: str) -> str:
    """웹에서 동기부여, 자기개발, 습관 형성 등 라이프 코칭 관련 정보를 검색합니다.
    사용자의 질문에 근거 있는 조언을 제공하기 위해 활용하세요.

    Args:
        query: 검색할 키워드 또는 문장
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "검색 결과를 찾지 못했습니다. 일반적인 지식으로 답변하겠습니다."

        # 검색 결과를 텍스트로 포맷팅
        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "제목 없음")
            body = r.get("body", "내용 없음")
            href = r.get("href", "")
            formatted.append(f"[{i}] {title}\n{body}\n출처: {href}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"검색 중 오류 발생: {e}. 일반적인 지식으로 답변하겠습니다."
