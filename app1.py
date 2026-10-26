import json
import os
import time
import streamlit as st

DATA_FILE = "study_roadmap.json"

st.set_page_config(
    page_title="試験勉強・講義回別＆周回管理", page_icon="🎓", layout="wide"
)

# --- スマホ縦画面向けのレイアウト・ボタンデザイン用CSS ---
st.markdown(
    """
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    div.stButton > button {
        width: 100% !important;
        padding: 6px 2px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }
    .timer-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# データ構造の読み込み（互換性保持）
raw_data = load_data()
if isinstance(raw_data, list):
    full_data = {"subjects": raw_data, "total_study_minutes": 0}
else:
    full_data = raw_data
    if "subjects" not in full_data:
        full_data["subjects"] = []
    if "total_study_minutes" not in full_data:
        full_data["total_study_minutes"] = 0

if "subjects" not in st.session_state:
    st.session_state.subjects = full_data["subjects"]
if "total_study_minutes" not in st.session_state:
    st.session_state.total_study_minutes = full_data["total_study_minutes"]


def update_and_save():
    save_data(
        {
            "subjects": st.session_state.subjects,
            "total_study_minutes": st.session_state.total_study_minutes,
        }
    )


st.title("🎓 進捗状況")

# --- ⏱️ 勉強タイマー & 時間記録エリア ---
st.markdown("### ⏱️ 勉強タイマー & 総学習時間")

# 合計時間の計算表示
hours = st.session_state.total_study_minutes // 60
mins = st.session_state.total_study_minutes % 60
st.metric(
    label="🔥 累計勉強時間",
    value=f"{hours} 時間 {mins} 分",
    delta=f"合計 {st.session_state.total_study_minutes} 分",
)

col_timer, col_manual = st.columns([2, 1])

with col_timer:
    st.write("**タイマー設定**")
    t_mode = st.radio(
        "モード選択", ["📖 勉強", "☕ 休憩"], horizontal=True
    )
    default_min = 25 if "勉強" in t_mode else 5
    timer_minutes = st.number_input(
        "時間（分）", min_value=1, max_value=180, value=default_min, step=1
    )

    if st.button("▶️ タイマー開始", type="primary"):
        total_seconds = int(timer_minutes * 60)
        progress_bar = st.progress(0.0)
        timer_text = st.empty()

        for remaining in range(total_seconds, -1, -1):
            m, s = divmod(remaining, 60)
            timer_text.markdown(f"### ⏳ 残り時間: **{m:02d}:{s:02d}**")
            progress_bar.progress((total_seconds - remaining) / total_seconds)
            time.sleep(1)

        st.balloons()
        if "勉強" in t_mode:
            st.session_state.total_study_minutes += int(timer_minutes)
            update_and_save()
            st.success(f"🎉 お疲れ様でした！{timer_minutes}分の勉強を記録しました！")
        else:
            st.success("☕ 休憩終了！次の勉強に移りましょう！")
        st.rerun()

with col_manual:
    st.write("**手動で追加**")
    manual_min = st.number_input("追加する分（分）", min_value=1, value=30, step=5)
    if st.button("➕ 記録を追加"):
        st.session_state.total_study_minutes += int(manual_min)
        update_and_save()
        st.success(f"{manual_min}分 追加しました！")
        st.rerun()

    if st.button("🔄 時間リセット", help="時間を0分に戻します"):
        st.session_state.total_study_minutes = 0
        update_and_save()
        st.rerun()

st.markdown("---")

# --- サイドバー (設定・操作) ---
st.sidebar.header("🔄 記録設定")
round_mode = st.sidebar.radio(
    "記録する周回数を選択", ["1周目 (🟩緑)", "2周目 (🟦青)", "3周目 (🟪紫)"]
)
current_round = (
    1 if "1周目" in round_mode else (2 if "2周目" in round_mode else 3)
)

st.sidebar.markdown("---")
st.sidebar.header("📖 教材・レジュメの追加")
sub_input = st.sidebar.text_input("科目名")
title_input = st.sidebar.text_input("レジュメ / テキスト名")
has_pages = st.sidebar.checkbox("ページ番号で管理する", value=True)

if has_pages:
    sp_input = st.sidebar.number_input("開始P", value=1, step=1)
    ep_input = st.sidebar.number_input("終了P", value=40, step=1)
lec_input = st.sidebar.number_input("講義数", value=4, step=1)

if st.sidebar.button("ロードマップに追加", type="primary"):
    if sub_input and title_input:
        new_item = {
            "id": int(st.session_state.subjects.__len__() + 1),
            "subject": sub_input,
            "title": title_input,
            "hasPages": has_pages,
            "lecturesCount": lec_input,
            "pageRounds": {},
            "lectureRounds": {},
            "memo": "",
        }
        if has_pages:
            new_item["startPage"] = int(sp_input)
            new_item["endPage"] = int(ep_input)

        st.session_state.subjects.append(new_item)
        update_and_save()
        st.sidebar.success("追加しました！")
        st.rerun()
    else:
        st.sidebar.error("科目名とタイトルを入力してください。")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ 全データを削除"):
    st.session_state.subjects = []
    st.session_state.total_study_minutes = 0
    update_and_save()
    st.rerun()

# --- メイン表示エリア ---
if not st.session_state.subjects:
    st.info("登録された教材がありません。左上の「＞」メニューから追加してください。")

for item in st.session_state.subjects:
    with st.expander(f"📌 {item['subject']} - {item['title']}", expanded=True):
        col_title, col_del = st.columns([4, 1])
        with col_del:
            if st.button("🗑️ 削除", key=f"del_{item['id']}"):
                st.session_state.subjects = [
                    s
                    for s in st.session_state.subjects
                    if s["id"] != item["id"]
                ]
                update_and_save()
                st.rerun()

        # 進捗メモ
        memo = st.text_input(
            "📝 メモ",
            value=item.get("memo", ""),
            key=f"memo_{item['id']}",
        )
        if memo != item.get("memo", ""):
            item["memo"] = memo
            update_and_save()

        # 1. ページ管理の場合
        if item.get("hasPages", True):
            st.write(
                f"**範囲:** p.{item['startPage']} 〜 p.{item['endPage']} （全{item['lecturesCount']}回講義）"
            )

            cols_per_row = 5
            pages = list(range(item["startPage"], item["endPage"] + 1))

            for row_idx in range(0, len(pages), cols_per_row):
                row_pages = pages[row_idx : row_idx + cols_per_row]
                cols = st.columns(cols_per_row)
                for i, p in enumerate(row_pages):
                    p_str = str(p)
                    r_level = item.get("pageRounds", {}).get(p_str, 0)

                    if r_level == 0:
                        label = f"p.{p}"
                        b_type = "secondary"
                    elif r_level == 1:
                        label = f"🟩 p.{p}"
                        b_type = "primary"
                    elif r_level == 2:
                        label = f"🟦 p.{p}\n(2周)"
                        b_type = "secondary"
                    else:
                        label = f"🟪 p.{p}\n(3周)"
                        b_type = "secondary"

                    if cols[i].button(label, key=f"p_{item['id']}_{p}", type=b_type):
                        item["pageRounds"][p_str] = (
                            0 if r_level >= current_round else current_round
                        )
                        update_and_save()
                        st.rerun()

        # 2. 回数管理（ページなし）の場合
        else:
            st.write(f"**全{item['lecturesCount']}回講義**（ページ指定なし）")

            cols_per_row = 3
            lecs = list(range(1, item["lecturesCount"] + 1))

            for row_idx in range(0, len(lecs), cols_per_row):
                row_lecs = lecs[row_idx : row_idx + cols_per_row]
                cols = st.columns(cols_per_row)
                for i, l_num in enumerate(row_lecs):
                    l_str = str(l_num)
                    r_level = item.get("lectureRounds", {}).get(l_str, 0)

                    if r_level == 0:
                        label = f"第{l_num}回"
                        b_type = "secondary"
                    elif r_level == 1:
                        label = f"🟩 第{l_num}回"
                        b_type = "primary"
                    elif r_level == 2:
                        label = f"🟦 第{l_num}回\n(2周)"
                        b_type = "secondary"
                    else:
                        label = f"🟪 第{l_num}回\n(3周)"
                        b_type = "secondary"

                    if cols[i].button(label, key=f"l_{item['id']}_{l_num}", type=b_type):
                        item["lectureRounds"][l_str] = (
                            0 if r_level >= current_round else current_round
                        )
                        update_and_save()
                        st.rerun()