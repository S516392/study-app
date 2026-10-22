import json
import os
import streamlit as st

DATA_FILE = "study_roadmap.json"

st.set_page_config(
    page_title="試験勉強・講義回別＆周回管理", page_icon="🎓", layout="wide"
)

# --- スマホ縦画面向けのレイアウト・ボタンデザイン用CSS ---
st.markdown(
    """
<style>
    /* 全体コンテナの余白調整（上が切れないよう余白を確保） */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* ボタンを格子状に綺麗に並べるFlexボックス */
    .grid-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    /* ボタン自体のスタイル調整（押しやすさと配置） */
    div.stButton > button {
        width: 100% !important;
        padding: 6px 2px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
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
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if "subjects" not in st.session_state:
    st.session_state.subjects = load_data()

st.title("🎓 進捗状況")

# --- サイドバー (設定・操作) ---
st.sidebar.header("🔄 記録設定")
round_mode = st.sidebar.radio(
    "記録する周回数を選択", ["1周目 (緑)", "2周目 (青)", "3周目 (紫)"]
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
        save_data(st.session_state.subjects)
        st.sidebar.success("追加しました！")
        st.rerun()
    else:
        st.sidebar.error("科目名とタイトルを入力してください。")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ 全データを削除"):
    st.session_state.subjects = []
    save_data([])
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
                save_data(st.session_state.subjects)
                st.rerun()

        # 進捗メモ
        memo = st.text_input(
            "📝 メモ",
            value=item.get("memo", ""),
            key=f"memo_{item['id']}",
        )
        if memo != item.get("memo", ""):
            item["memo"] = memo
            save_data(st.session_state.subjects)

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

                    label = f"p.{p}" if r_level == 0 else f"p.{p}\n({r_level}周)"

                    if cols[i].button(label, key=f"p_{item['id']}_{p}"):
                        item["pageRounds"][p_str] = (
                            0 if r_level >= current_round else current_round
                        )
                        save_data(st.session_state.subjects)
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

                    label = (
                        f"第{l_num}回"
                        if r_level == 0
                        else f"第{l_num}回\n({r_level}周)"
                    )

                    if cols[i].button(label, key=f"l_{item['id']}_{l_num}"):
                        item["lectureRounds"][l_str] = (
                            0 if r_level >= current_round else current_round
                        )
                        save_data(st.session_state.subjects)
                        st.rerun()