import streamlit as st
import pandas as pd

from utils.extractor import (
    fetch_url_text,
    extract_products,
    create_image_placeholder_rows
)


st.set_page_config(
    page_title="Competitor Insight AI",
    page_icon="☕",
    layout="wide"
)


st.title("☕ Competitor Insight AI")
st.subheader("AI-powered F&B Product Market Intelligence Platform")
st.divider()

st.markdown("### Brand")

brand = st.selectbox(
    "브랜드를 선택하세요",
    [
        "STARBUCKS",
        "A TWOSOME PLACE",
        "EDIYA COFFEE",
        "HOLLYS",
        "MEGA MGC COFFEE",
        "PAIK'S COFFEE",
        "COMPOSE COFFEE",
    ]
)

st.markdown("### Input Type")

input_type = st.radio(
    "분석할 입력 방식을 선택하세요",
    ["Image Upload", "URL", "Text"],
    horizontal=True
)

input_text = ""
source = "-"
uploaded_images = []
url = ""

if input_type == "Image Upload":
    uploaded_images = st.file_uploader(
        "제품 이미지 또는 캡처를 업로드하세요",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_images:
        st.caption("업로드된 이미지는 다음 단계에서 GPT Vision으로 제품명/가격/출시일을 자동 추출할 예정입니다.")

        with st.expander(f"📷 Uploaded Images ({len(uploaded_images)})", expanded=False):
            cols = st.columns(4)

            for i, image in enumerate(uploaded_images):
                with cols[i % 4]:
                    st.image(image, caption=image.name, width=180)

    source = "Image Upload"

elif input_type == "URL":
    url = st.text_input(
        "공식 홈페이지/뉴스룸/보도자료 링크를 입력하세요",
        placeholder="예: https://www.starbucks.co.kr/..."
    )
    source = url if url else "-"

elif input_type == "Text":
    input_text = st.text_area(
        "게시글 또는 보도자료 내용을 붙여넣으세요",
        height=250,
        placeholder="""
예시)

스타벅스 코리아

아이스 두바이 초콜릿 모카 출시
Tall 7,300원
Grande 8,100원
Venti 8,900원

두바이 초콜릿 프라푸치노 출시
Grande 8,100원

2월 11일 출시
"""
    )
    source = f"{brand} Text Input"


product_df = pd.DataFrame(
    columns=["브랜드", "제품명", "카테고리", "출시일", "가격", "사이즈", "정보상태", "출처"]
)

if st.button(
    "🔍 Analyze Products",
    use_container_width=True
):
    if input_type == "Image Upload":
        if not uploaded_images:
            st.warning("이미지를 먼저 업로드해주세요.")
        else:
            product_df = create_image_placeholder_rows(uploaded_images, brand)
            st.info("현재 단계에서는 이미지 업로드를 제품 정보 추출 전 단계로 처리합니다. 다음 단계에서 GPT Vision을 연결해 제품명/가격/출시일을 자동 추출합니다.")

    elif input_type == "URL":
        if not url:
            st.warning("URL을 먼저 입력해주세요.")
        elif "instagram.com" in url:
            st.warning("인스타그램 링크는 자동 크롤링이 제한될 수 있어요. 캡처 이미지 업로드 또는 캡션 복사를 권장합니다.")
        else:
            input_text = fetch_url_text(url)

            if input_text:
                product_df = extract_products(input_text, brand, source)

                if product_df["제품명"].eq("-").all():
                    st.warning("해당 URL은 이미지 중심 페이지일 가능성이 높습니다. 페이지 내 이미지 또는 캡처를 업로드하면 다음 단계에서 GPT Vision으로 분석할 수 있습니다.")
            else:
                st.error("URL 내용을 읽지 못했습니다. 공식 홈페이지/뉴스룸/보도자료 링크인지 확인해주세요.")

    elif input_type == "Text":
        if not input_text:
            st.warning("분석할 텍스트를 먼저 입력해주세요.")
        else:
            product_df = extract_products(input_text, brand, source)


st.divider()

with st.container(border=True):
    st.subheader("📦 Product Information")

    if product_df.empty:
        st.info("분석 결과가 아직 없습니다.")
    else:
        st.dataframe(
            product_df,
            use_container_width=True,
            hide_index=True
        )

        csv = product_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name="competitor_product_info.csv",
            mime="text/csv",
            use_container_width=True
        )

st.divider()

with st.container(border=True):
    st.subheader("🤖 AI Insight")

    if product_df.empty:
        st.write("제품 정보 분석 후 AI Insight가 생성될 예정입니다.")
    else:
        st.markdown("##### 🧠 AI Summary")
        st.write(f"{brand}의 신제품 정보를 기반으로 시장 트렌드와 상품기획 시사점을 분석할 수 있습니다.")

        st.markdown("##### 📈 Market Strategy")
        st.write("제품명과 카테고리 정보를 1차 구조화한 뒤, 가격·출시일·사이즈 정보가 부족한 항목은 추가 검색 대상으로 분류합니다.")

        st.markdown("##### 🎯 Target Consumer")
        st.write("다음 단계에서 GPT 분석을 연결해 제품별 예상 타깃 고객을 자동 생성할 예정입니다.")

        st.markdown("##### 💡 Product Planning Insight")
        st.write("이미지 기반 비정형 정보를 구조화하고, 부족한 정보를 검색 대상으로 분리하여 상품기획 업무에 활용 가능한 형태로 전환합니다.")

        st.markdown("##### 🏷️ Positioning")
        st.write("Image-based | Product Intelligence | F&B Market | Search Needed")