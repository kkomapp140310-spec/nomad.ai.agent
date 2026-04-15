"""
Life Coach Agent - Streamlit 채팅 앱
- 용도: 웹 검색 + 파일 검색 기능을 갖춘 AI 라이프 코치 채팅 인터페이스
- 실행: uv run streamlit run app.py
- 필수 환경변수: OPENAI_API_KEY, VECTOR_STORE_ID (.env 파일 또는 시스템 환경변수)
- 사전 설정: uv run python setup_vector_store.py (Vector Store 생성)
"""

import asyncio
import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent

# 환경변수 로드
load_dotenv()

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Life Coach Agent",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 Life Coach Agent")
st.caption("목표 달성, 습관 형성, 자기개발을 도와주는 AI 라이프 코치")

# --- 사이드바: 파일 업로드 및 상태 표시 ---
with st.sidebar:
    st.header("📂 목표 & 일기 관리")

    vector_store_id = os.getenv("VECTOR_STORE_ID")

    if vector_store_id:
        st.success(f"Vector Store 연결됨")
        st.caption(f"ID: `{vector_store_id[:20]}...`")

        # 파일 업로드 UI
        st.subheader("문서 업로드")
        uploaded_files = st.file_uploader(
            "목표, 일기, 계획 문서를 업로드하세요",
            type=["pdf", "txt", "md", "docx"],
            accept_multiple_files=True,
            key="file_uploader",
        )

        if uploaded_files and st.button("📤 Vector Store에 추가", type="primary"):
            client = OpenAI()
            for uploaded_file in uploaded_files:
                try:
                    # 임시 파일로 저장 후 업로드
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix
                    ) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name

                    with open(tmp_path, "rb") as f:
                        # Files API에 업로드 후 Vector Store에 연결
                        file_obj = client.files.create(file=f, purpose="assistants")
                        vs_file = client.vector_stores.files.create(
                            vector_store_id=vector_store_id,
                            file_id=file_obj.id,
                        )
                        # 폴링 (최대 60초)
                        import time as _time
                        _elapsed = 0
                        while vs_file.status in ("in_progress", "queued") and _elapsed < 60:
                            _time.sleep(2)
                            _elapsed += 2
                            vs_file = client.vector_stores.files.retrieve(
                                vector_store_id=vector_store_id,
                                file_id=file_obj.id,
                            )
                    os.unlink(tmp_path)
                    st.success(f"✅ {uploaded_file.name} 업로드 완료 ({vs_file.status})")
                except Exception as e:
                    st.error(f"❌ {uploaded_file.name} 실패: {e}")

        # 저장된 파일 목록 표시
        st.subheader("저장된 파일")
        if st.button("🔄 파일 목록 새로고침"):
            try:
                client = OpenAI()
                vs_files = client.vector_stores.files.list(
                    vector_store_id=vector_store_id
                )
                file_count = 0
                for vs_file in vs_files:
                    file_count += 1
                    status_icon = "✅" if vs_file.status == "completed" else "⏳"
                    st.caption(f"{status_icon} {vs_file.id} ({vs_file.status})")
                if file_count == 0:
                    st.info("아직 업로드된 파일이 없습니다.")
                else:
                    st.caption(f"총 {file_count}개 파일")
            except Exception as e:
                st.error(f"파일 목록 조회 실패: {e}")
    else:
        st.warning("Vector Store 미설정")
        st.markdown(
            """
            **초기 설정이 필요합니다:**
            ```bash
            uv run python setup_vector_store.py
            ```
            실행 후 `.env` 파일에 `VECTOR_STORE_ID`가
            자동으로 저장됩니다.
            """
        )

    st.divider()
    st.subheader("💡 사용 팁")
    st.markdown(
        """
        - **목표 확인**: "내 운동 목표 어떻게 돼가고 있어?"
        - **일기 기록**: "오늘 러닝 30분 했어, 기분 좋아!"
        - **조언 요청**: "아침에 일찍 일어나는 방법 알려줘"
        - **진행 추적**: "이번 달 내 진행 상황 정리해줘"
        """
    )

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_history" not in st.session_state:
    st.session_state.agent_history = None

# --- 기존 대화 이력 표시 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("무엇이든 물어보세요! (예: 내 운동 목표 달성은 잘 되어가고 있어?)"):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 에이전트 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("코치가 기록을 확인하고 있어요..."):
            try:
                response, updated_history = asyncio.run(
                    run_agent(prompt, st.session_state.agent_history)
                )
                st.session_state.agent_history = updated_history
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                error_text = f"오류가 발생했습니다: {e}"
                st.error(error_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_text}
                )
