"""
Life Coach Agent - Streamlit 채팅 앱
"""

import asyncio
import streamlit as st
from dotenv import load_dotenv

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

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    # UI 표시용 메시지 리스트: [{"role": "user"|"assistant", "content": "..."}]
    st.session_state.messages = []

if "agent_history" not in st.session_state:
    # Agent SDK용 대화 이력 (to_input_list() 형식)
    st.session_state.agent_history = None

# --- 기존 대화 이력 표시 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("무엇이든 물어보세요! (예: 아침에 일찍 일어나는 방법)"):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 에이전트 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("코치가 생각 중..."):
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
