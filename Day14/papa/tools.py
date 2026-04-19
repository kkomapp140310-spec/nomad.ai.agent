"""
도구 모듈 (Tools Module)
- 용도: Life Coach Agent의 도구 정의 (웹 검색 + 일기 기록 + 이미지 생성)
- 사용법: agent.py에서 tools=[web_search, save_journal_entry, generate_image]로 등록
- 웹 검색: DuckDuckGo (API 키 불필요)
- 파일 검색: OpenAI FileSearchTool (Vector Store 기반, agent.py에서 직접 등록)
- 일기 기록: Vector Store에 일기 항목을 파일로 추가
- 이미지 생성: OpenAI DALL-E 3 API로 비전 보드/동기부여 포스터 생성
"""

import os
import tempfile
import time
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


@function_tool
def generate_image(prompt: str, style: str = "비전보드") -> str:
    """DALL-E 3를 사용하여 동기부여 이미지, 비전 보드, 축하 포스터를 생성합니다.
    사용자의 목표 달성 축하, 비전 보드 제작, 동기부여 포스터 요청 시 사용하세요.

    Args:
        prompt: 생성할 이미지에 대한 상세 설명 (영어로 작성. 구체적인 목표, 활동, 감정을 포함)
        style: 이미지 스타일. 다음 중 택1:
            - "비전보드": 여러 목표를 콜라주 형태로 시각화 (가로형)
            - "동기부여포스터": 핵심 메시지가 담긴 깔끔한 포스터 (세로형)
            - "축하카드": 목표 달성 축하 이미지 (세로형)
            - "진행상황": 성장/변화를 보여주는 인포그래픽 스타일 (가로형)
            - "마일스톤": 특정 단계 달성을 기념하는 배지/메달 스타일 (세로형)
    """
    try:
        client = OpenAI()

        # 스타일별 프롬프트 보강 및 이미지 사이즈 설정
        style_configs = {
            "비전보드": {
                "prefix": (
                    "Create a stunning, high-quality vision board in a modern collage layout. "
                    "Use a harmonious color palette with warm, inspiring tones. "
                    "Include symbolic imagery, icons, and visual metaphors representing these goals and dreams: "
                ),
                "suffix": (
                    ". Style: magazine-quality collage with overlapping photos, motivational words, "
                    "soft gradients, gold accents, and a cohesive aesthetic. "
                    "No text blocks, focus on visual storytelling."
                ),
                "size": "1792x1024",
            },
            "동기부여포스터": {
                "prefix": (
                    "Create a clean, modern motivational poster design. "
                    "Feature bold, readable typography as the centerpiece with a powerful message. "
                    "Include a striking background image related to: "
                ),
                "suffix": (
                    ". Style: minimalist design, strong contrast, "
                    "cinematic lighting, single focal point, "
                    "professional typography, dark or gradient background."
                ),
                "size": "1024x1792",
            },
            "축하카드": {
                "prefix": (
                    "Create a beautiful, warm celebration card with festive elements. "
                    "Include confetti, ribbons, or fireworks. "
                    "The theme is congratulating someone for achieving: "
                ),
                "suffix": (
                    ". Style: joyful and uplifting, golden and bright colors, "
                    "elegant design with celebratory elements, "
                    "party atmosphere, achievement feeling."
                ),
                "size": "1024x1024",
            },
            "진행상황": {
                "prefix": (
                    "Create a visually compelling illustration showing a journey of growth and progress. "
                    "Use a path, staircase, mountain climb, or timeline metaphor to depict: "
                ),
                "suffix": (
                    ". Style: clean infographic illustration, "
                    "before-and-after visual narrative, upward trajectory, "
                    "milestones marked along the way, hopeful and energetic mood."
                ),
                "size": "1792x1024",
            },
            "마일스톤": {
                "prefix": (
                    "Create a premium achievement badge or medal design celebrating a specific milestone. "
                    "Include laurel wreaths, stars, or shield elements for: "
                ),
                "suffix": (
                    ". Style: metallic gold and silver tones, embossed effect, "
                    "premium badge/seal design, ceremonial feeling, "
                    "centered composition with radiating light."
                ),
                "size": "1024x1024",
            },
        }

        config = style_configs.get(style, style_configs["비전보드"])
        full_prompt = f"{config['prefix']}{prompt}{config['suffix']}"

        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size=config["size"],
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt or ""

        # 마크다운 이미지 형식으로 반환 (Streamlit에서 렌더링됨)
        return (
            f"![{style} 이미지]({image_url})\n\n"
            f"**이미지 스타일**: {style}\n"
            f"**생성 프롬프트 요약**: {revised_prompt[:300]}"
        )

    except Exception as e:
        return f"이미지 생성 중 오류 발생: {e}"
