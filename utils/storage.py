import os
import pandas as pd


DATA_DIR = "data"
MONITORING_HISTORY_PATH = os.path.join(DATA_DIR, "monitoring_history.csv")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_monitoring_history():
    ensure_data_dir()

    if os.path.exists(MONITORING_HISTORY_PATH):
        return pd.read_csv(MONITORING_HISTORY_PATH)

    return pd.DataFrame(
        columns=["검색어", "제목", "출처", "게시일", "링크", "정보상태", "등록상태"]
    )


def mark_new_results(current_df):
    history_df = load_monitoring_history()

    if current_df.empty:
        return current_df

    existing_links = set(history_df["링크"].dropna()) if not history_df.empty else set()

    result_df = current_df.copy()
    result_df["등록상태"] = result_df["링크"].apply(
        lambda link: "EXISTING" if link in existing_links else "NEW"
    )

    return result_df


def save_monitoring_results(result_df):
    ensure_data_dir()

    if result_df.empty:
        return 0

    history_df = load_monitoring_history()

    combined_df = pd.concat([history_df, result_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["링크"], keep="first")

    combined_df.to_csv(MONITORING_HISTORY_PATH, index=False, encoding="utf-8-sig")

    return len(combined_df)