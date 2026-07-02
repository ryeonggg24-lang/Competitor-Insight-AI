import urllib.parse
import feedparser
import pandas as pd


BRAND_MAP = {
    "STARBUCKS": "스타벅스",
    "A TWOSOME PLACE": "투썸플레이스",
    "EDIYA COFFEE": "이디야",
    "HOLLYS": "할리스",
    "MEGA MGC COFFEE": "메가커피",
    "PAIK'S COFFEE": "빽다방",
    "COMPOSE COFFEE": "컴포즈커피",
}


def create_search_queries(brand):

    brand = BRAND_MAP.get(brand, brand)

    return [
        f"{brand} 신메뉴",
        f"{brand} 신제품",
        f"{brand} 출시",
        f"{brand} 시즌메뉴",
        f"{brand} 신상품",
    ]


def fetch_google_news_rss(query, max_results=10):

    encoded_query = urllib.parse.quote(query)

    url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    )

    feed = feedparser.parse(url)

    rows = []

    for entry in feed.entries[:max_results]:

        source = "-"

        if "source" in entry:
            try:
                source = entry.source.title
            except:
                pass

        rows.append(
            {
                "검색어": query,
                "제목": entry.get("title", "-"),
                "출처": source,
                "게시일": entry.get("published", "-"),
                "링크": entry.get("link", "-"),
                "정보상태": "신제품 후보"
            }
        )

    return rows


def monitor_new_products(
    brand,
    max_results_per_query=5
):

    queries = create_search_queries(brand)

    all_rows = []

    for query in queries:

        rows = fetch_google_news_rss(
            query,
            max_results=max_results_per_query
        )

        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "검색어",
                "제목",
                "출처",
                "게시일",
                "링크",
                "정보상태",
            ]
        )

    df = df.drop_duplicates(subset=["링크"])

    return df