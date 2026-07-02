import re
import html
import urllib.request
import pandas as pd


def clean_html(raw_html):
    text = re.sub(r"<script.*?</script>", " ", raw_html, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_url_text(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_html = response.read().decode("utf-8", errors="ignore")
        return clean_html(raw_html)
    except Exception:
        return ""


def extract_release_date(text):
    date_match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", text)

    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return f"2026-{month:02d}-{day:02d}"

    return "-"


def extract_category(product_name):
    drink_keywords = [
        "라떼", "모카", "아메리카노", "프라푸치노", "블렌디드",
        "에이드", "티", "쉐이크", "스무디", "커피", "음료",
        "콜드브루", "티라떼"
    ]

    dessert_keywords = [
        "케이크", "쿠키", "베이글", "샌드위치", "브레드",
        "디저트", "빙수", "마카롱", "도넛", "빵", "롤케이크"
    ]

    if any(keyword in product_name for keyword in drink_keywords):
        return "음료"
    elif any(keyword in product_name for keyword in dessert_keywords):
        return "푸드/디저트"
    return "-"


def get_info_status(product_name, price, release_date, size):
    missing = []

    if product_name == "-":
        missing.append("제품명")
    if price == "-":
        missing.append("가격")
    if release_date == "-":
        missing.append("출시일")
    if size == "-":
        missing.append("사이즈")

    if not missing:
        return "정보 보완 완료"
    elif product_name != "-":
        return f"{', '.join(missing)} 검색 필요"
    return "이미지/텍스트 추출 필요"


def extract_products(text, brand, source):
    prices = re.findall(r"\d{1,2},\d{3}원", text)
    sizes = re.findall(
        r"Tall|Grande|Venti|Short|Regular|Large|Small|Medium",
        text,
        re.IGNORECASE
    )

    release_date = extract_release_date(text)

    product_keywords = [
        "라떼", "모카", "아메리카노", "프라푸치노", "블렌디드",
        "에이드", "티", "쉐이크", "스무디", "케이크", "샌드위치",
        "베이글", "쿠키", "빙수", "브레드", "도넛", "콜드브루",
        "티라떼", "롤케이크"
    ]

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    product_names = []

    for line in lines:
        if any(keyword in line for keyword in product_keywords):
            cleaned = re.sub(
                r"Tall|Grande|Venti|T|G|V|Short|Regular|Large|R|L|EX",
                "",
                line,
                flags=re.IGNORECASE
            )
            cleaned = re.sub(r"\d{1,2},\d{3}원", "", cleaned)
            cleaned = cleaned.replace("출시", "")
            cleaned = cleaned.strip(" -:|")

            if len(cleaned) >= 3 and cleaned not in product_names:
                product_names.append(cleaned)

    if not product_names:
        pattern = r"([가-힣A-Za-z0-9\s]+(?:라떼|모카|아메리카노|프라푸치노|블렌디드|에이드|티|쉐이크|스무디|케이크|샌드위치|베이글|쿠키|빙수|브레드|도넛|콜드브루|티라떼|롤케이크))"
        matches = re.findall(pattern, text)

        for match in matches:
            cleaned = match.strip()
            if len(cleaned) >= 3 and cleaned not in product_names:
                product_names.append(cleaned)

    rows = []

    if not product_names:
        price_value = " / ".join(prices) if prices else "-"
        size_value = " / ".join(dict.fromkeys(sizes)) if sizes else "-"

        rows.append({
            "브랜드": brand,
            "제품명": "-",
            "카테고리": "-",
            "출시일": release_date,
            "가격": price_value,
            "사이즈": size_value,
            "정보상태": get_info_status("-", price_value, release_date, size_value),
            "출처": source
        })
    else:
        for idx, product_name in enumerate(product_names):
            price_value = prices[idx] if idx < len(prices) else "-"
            size_value = sizes[idx] if idx < len(sizes) else "-"

            if len(product_names) == 1:
                price_value = " / ".join(prices) if prices else "-"
                size_value = " / ".join(dict.fromkeys(sizes)) if sizes else "-"

            rows.append({
                "브랜드": brand,
                "제품명": product_name,
                "카테고리": extract_category(product_name),
                "출시일": release_date,
                "가격": price_value,
                "사이즈": size_value,
                "정보상태": get_info_status(product_name, price_value, release_date, size_value),
                "출처": source
            })

    return pd.DataFrame(rows)


def create_image_placeholder_rows(uploaded_images, brand):
    rows = []

    for image in uploaded_images:
        rows.append({
            "브랜드": brand,
            "제품명": "이미지 분석 연결 예정",
            "카테고리": "-",
            "출시일": "-",
            "가격": "-",
            "사이즈": "-",
            "정보상태": "이미지 추출 완료 / 가격·출시일 검색 필요",
            "출처": image.name
        })

    return pd.DataFrame(rows)