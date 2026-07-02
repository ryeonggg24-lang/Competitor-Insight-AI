import streamlit as st
import pandas as pd

from utils.extractor import (
    fetch_url_text,
    extract_products,
    create_image_placeholder_rows
)

from utils.ocr_reader import read_images_text
from utils.monitoring import monitor_new_products
from utils.storage import mark_new_results, save_monitoring_results


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

st.markdown("### Mode")

input_type = st.radio(
    "분석 방식을 선택하세요",
    ["Monitoring", "Image Upload", "URL", "Text"],
    horizontal=True
)

input_text = ""
source = "-"
uploaded_images = []
url = ""

product_df = pd.DataFrame(
    columns=["브랜드", "제품명", "카테고리", "출시일", "가격", "사이즈", "정보상태", "출처"]
)

monitoring_df = pd.DataFrame(
    columns=["검색어", "제목", "출처", "게시일", "링크", "정보상태"]
)


if input_type == "Monitoring":
    st.markdown("### 🔎 New Product Monitoring")
    st.write("브랜드명 기반으로 신메뉴/신제품 관련 뉴스·웹 후보를 자동 수집합니다.")

    max_results = st.slider(
        "검색어별 수집 개수",
        min_value=3,
        max_value=20,
        value=5
    )

elif input_type == "Image Upload":
    uploaded_images = st.file_uploader(
        "제품 이미지 또는 캡처를 업로드하세요",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_images:
        st.caption("업로드된 이미지는 OCR로 텍스트를 추출한 뒤 제품 정보 테이블로 변환합니다.")

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

2월 11일 출시
"""
    )
    source = f"{brand} Text Input"


if st.button(
    "🔍 Run Analysis",
    use_container_width=True
):
    if input_type == "Monitoring":
        with st.spinner("신제품 관련 후보를 모니터링하는 중입니다..."):
            monitoring_df = monitor_new_products(
                brand,
                max_results_per_query=max_results
            )
            monitoring_df = mark_new_results(monitoring_df)

        if monitoring_df.empty:
            st.warning("검색 결과가 없습니다.")
        else:
            st.success("신제품 모니터링이 완료되었습니다.")

    elif input_type == "Image Upload":
        if not uploaded_images:
            st.warning("이미지를 먼저 업로드해주세요.")
        else:
            with st.spinner("이미지에서 텍스트를 읽는 중입니다..."):
                ocr_text = read_images_text(uploaded_images)

            with st.expander("🔎 OCR 추출 텍스트 확인", expanded=False):
                st.text(ocr_text)

            if ocr_text.strip():
                product_df = extract_products(
                    ocr_text,
                    brand,
                    "Image OCR"
                )
                st.success("이미지 OCR 분석이 완료되었습니다.")
            else:
                product_df = create_image_placeholder_rows(uploaded_images, brand)
                st.warning("이미지에서 텍스트를 충분히 읽지 못했습니다. 더 선명한 캡처를 업로드해주세요.")

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
                    st.warning("해당 URL은 이미지 중심 페이지일 가능성이 높습니다. 페이지 내 이미지 또는 캡처를 업로드하면 OCR로 분석할 수 있습니다.")
            else:
                st.error("URL 내용을 읽지 못했습니다. 공식 홈페이지/뉴스룸/보도자료 링크인지 확인해주세요.")

    elif input_type == "Text":
        if not input_text:
            st.warning("분석할 텍스트를 먼저 입력해주세요.")
        else:
            product_df = extract_products(input_text, brand, source)


st.divider()

if input_type == "Monitoring":
    with st.container(border=True):
        st.subheader("🛰️ Monitoring Results")

        if monitoring_df.empty:
            st.info("모니터링 결과가 아직 없습니다.")

        else:
            st.dataframe(
                monitoring_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "링크": st.column_config.LinkColumn("링크")
                }
            )

            csv = monitoring_df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label="📥 모니터링 결과 CSV 다운로드",
                data=csv,
                file_name="new_product_monitoring_results.csv",
                mime="text/csv",
                use_container_width=True
            )

            if st.button(
                "💾 모니터링 결과 DB 저장",
                use_container_width=True
            ):
                saved_count = save_monitoring_results(monitoring_df)

                st.success(
                    f"DB 저장 완료! 현재 {saved_count}개의 링크가 저장되어 있습니다."
                )

else:
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

    if input_type == "Monitoring":
        if monitoring_df.empty:
            st.write("모니터링 결과 생성 후 AI Insight가 생성될 예정입니다.")
        else:
            st.markdown("##### 🧠 Monitoring Summary")
            st.write(f"{brand} 관련 신제품 후보 뉴스/웹문서를 수집했습니다.")

            st.markdown("##### 📈 Market Strategy")
            st.write("수집된 제목과 출처를 기반으로 브랜드별 신제품 출시 흐름을 추적할 수 있습니다.")

            st.markdown("##### 💡 Next Step")
            st.write("다음 단계에서는 수집된 링크 본문을 읽어 제품명/가격/출시일을 자동 추출하고, 기존 DB와 비교해 신규 여부를 판별합니다.")

            st.markdown("##### 🏷️ Positioning")
            st.write("Monitoring-based | New Product Tracking | Search-first Architecture")

    else:
        if product_df.empty:
            st.write("제품 정보 분석 후 AI Insight가 생성될 예정입니다.")
        else:
            st.markdown("##### 🧠 AI Summary")
            st.write(f"{brand}의 신제품 정보를 기반으로 시장 트렌드와 상품기획 시사점을 분석할 수 있습니다.")

            st.markdown("##### 📈 Market Strategy")
            st.write("제품명과 카테고리 정보를 1차 구조화한 뒤, 가격·출시일·사이즈 정보가 부족한 항목은 추가 검색 대상으로 분류합니다.")

            st.markdown("##### 🎯 Target Consumer")
            st.write("다음 단계에서 제품별 예상 타깃 고객을 자동 생성할 예정입니다.")

            st.markdown("##### 💡 Product Planning Insight")
            st.write("이미지 기반 비정형 정보를 OCR로 구조화하고, 부족한 정보를 검색 대상으로 분리하여 상품기획 업무에 활용 가능한 형태로 전환합니다.")

            st.markdown("##### 🏷️ Positioning")
            st.write("OCR-based | Product Intelligence | F&B Market | Search Needed")