import streamlit as st

st.set_page_config(
    page_title="Competitor Insight AI",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Competitor Insight AI")

st.subheader("AI-powered Competitor Analysis Platform")

st.divider()

st.markdown("### Brand")

brand = st.selectbox(
    "브랜드를 선택하세요",
    [
        "스타벅스",
        "투썸플레이스",
        "이디야",
        "할리스",
        "메가MGC",
        "빽다방",
        "컴포즈커피"
    ]
)
st.markdown("### Instagram Post / News")

post = st.text_area(
    "게시글 또는 기사 내용을 붙여넣으세요.",
    height=250,
    placeholder="스타벅스 인스타그램 게시글 또는 보도자료를 붙여넣으세요."
)
if st.button("🔍 Analyze", use_container_width=True):
    st.success("분석 기능은 다음 단계에서 구현됩니다.")
    st.divider()

st.markdown("## 📊 Analysis Result")

col1, col2 = st.columns(2)

with col1:
    st.metric("브랜드", "스타벅스")
    st.metric("제품명", "아이스 두바이 초콜릿 모카")
    st.metric("카테고리", "음료")

with col2:
    st.metric("출시일", "2026-02-11")
    st.metric("가격", "7,300 / 8,100 / 8,900원")
    st.metric("사이즈", "Tall / Grande / Venti")

    st.markdown("## 🤖 AI Insight")

st.success("""
- 글로벌 인기 메뉴의 국내 도입 전략
- 프리미엄 디저트 트렌드 반영
- 초콜릿 기반 시즌 음료 강화
- 국내 소비자 취향을 고려한 현지화
""")