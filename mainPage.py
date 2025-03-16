import streamlit as st

# ✅ 세션 상태에서 페이지 이동을 관리
if "page" not in st.session_state:
    st.session_state["page"] = "main"

# ✅ 페이지 이동 함수 (페이지 이동 후 UI 업데이트)
def change_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()  # 🔄 페이지 전환 후 새로고침하여 UI 업데이트

# ✅ 메인 페이지 UI 구성
if st.session_state["page"] == "main":
    st.title("🔹 법률 서비스 포털")

    # ✅ 버튼을 가운데 정렬하는 CSS 추가
    st.markdown(
        """
        <style>
        div.stButton > button {
            width: 100%;
            height: 50px;
            font-size: 16px;
        }
        div.block-container { text-align: center; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ 버튼 3개를 중앙 정렬
    st.write("")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💬 법률 상담 AI 챗봇"):
            change_page("chatbot")

    with col2:
        if st.button("📄 법률 문서 제작"):
            change_page("document")

    with col3:
        if st.button("📂 게시판 DB"):
            change_page("database")

# ✅ 법률 상담 AI 챗봇 페이지
elif st.session_state["page"] == "chatbot":
    import law_chatbot

# ✅ 법률 문서 제작 페이지
elif st.session_state["page"] == "document":
    import law_report

# ✅ 게시판 DB 페이지
elif st.session_state["page"] == "database":
    st.title("📂 게시판 DB")
    st.write("이곳에서 법률 관련 게시판 데이터를 관리할 수 있습니다.")
    if st.button("⬅️ 돌아가기"):
        change_page("main")
