"""
도구 모듈 (Tools Module)
- 용도: Life Coach Agent의 도구 정의 (웹 검색 + 일기 기록)
- 사용법: agent.py에서 tools=[web_search, save_journal_entry]로 등록
- 웹 검색: DuckDuckGo (API 키 불필요)
- 파일 검색: OpenAI FileSearchTool (Vector Store 기반, agent.py에서 직접 등록)
- 일기 기록: Vector Store에 일기 항목을 파일로 추가
"""

import os
import tempfile
from datetime import datetime

from agents import function_tool
from duckduckgo_search import DDGS
from openai import OpenAI


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

        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "제목 없음")
            body = r.get("body", "내용 없음")
            href = r.get("href", "")
            formatted.append(f"[{i}] {title}\n{body}\n출처: {href}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"검색 중 오류 발생: {e}. 일반적인 지식으로 답변하겠습니다."


@function_tool
def save_journal_entry(entry: str, mood: str = "보통") -> str:
    """사용자의 일기/진행 기록을 Vector Store에 저장합니다.
    사용자가 오늘의 활동, 감정, 진행 상황을 공유하면 이 도구로 기록하세요.

    Args:
        entry: 일기 내용 (사용자가 공유한 활동, 감정, 진행 상황 등)
        mood: 기분 상태 (좋음/보통/나쁨)
    """
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    if not vector_store_id:
        return "Vector Store가 설정되지 않았습니다. setup_vector_store.py를 먼저 실행하세요."

    try:
        client = OpenAI()
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")

        # 일기 내용 포맷팅
        content = f"""# 일기 - {date_str} {time_str}

**기분**: {mood}

## 내용
{entry}

---
*기록 시각: {date_str} {time_str}*
"""
        # 임시 파일로 생성하여 Vector Store에 업로드
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", prefix="journal_", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            with open(temp_path, "rb") as f:
                # 1단계: Files API에 업로드
                file_obj = client.files.create(file=f, purpose="assistants")

            # 2단계: Vector Store에 연결
            vs_file = client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_obj.id,
            )

            # 3단계: 폴링 (최대 60초)
            import time
            elapsed = 0
            while vs_file.status in ("in_progress", "queued") and elapsed < 60:
                time.sleep(2)
                elapsed += 2
                vs_file = client.vector_stores.files.retrieve(
                    vector_store_id=vector_store_id,
                    file_id=file_obj.id,
                )

            return f"일기가 저장되었습니다. (날짜: {date_str}, 기분: {mood}, file_id: {file_obj.id}, status: {vs_file.status})"
        finally:
            os.unlink(temp_path)

    except Exception as e:
        return f"일기 저장 중 오류 발생: {e}"
