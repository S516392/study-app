import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium

# 画面全体のレイアウト設定
st.set_page_config(page_title="リアルタイム雨情報ダッシュボード", layout="wide")

st.title("🌧️ 当日 雨の降り方＆雨雲レーダー比較ダッシュボード")
st.write("各気象機関のリアルタイムデータと雨雲レーダーを統合表示しています。")

# ---------------------------------------------------------
# データ取得関数
# ---------------------------------------------------------

@st.cache_data(ttl=300) # 5分間キャッシュ
def get_open_meteo_hourly(lat=35.6785, lon=139.6823):
    """Open-Meteoから1時間ごとの降水量・降水確率・天気を取得"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=precipitation,precipitation_probability,weather_code"
        f"&timezone=Asia%2FTokyo&forecast_days=1"
    )
    try:
        res = requests.get(url, timeout=10)
        data = res.json()["hourly"]
        
        df = pd.DataFrame({
            "時間": [t.split("T")[1] for t in data["time"]],
            "降水量 (mm/h)": data["precipitation"],
            "降水確率 (%)": data["precipitation_probability"]
        })
        return df
    except Exception as e:
        st.error(f"Open-Meteoデータの取得に失敗しました: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_jma_pops():
    """気象庁JSON APIから当日の降水確率を取得"""
    url = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        pops_series = data[0]["timeSeries"][1]
        
        times = [datetime.fromisoformat(t).strftime("%H:00") for t in pops_series["timeDefines"]]
        pops = pops_series["areas"][0]["pops"]
        
        return pd.DataFrame({"時間帯": times, "気象庁 降水確率 (%)": pops})
    except Exception as e:
        st.error(f"気象庁データの取得に失敗しました: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# メイン画面レイアウト
# ---------------------------------------------------------

# サイドバー設定
st.sidebar.header("📍 地域設定")
location = st.sidebar.selectbox("地域を選択", ["東京 (Tokyo)", "大阪 (Osaka)", "名古屋 (Nagoya)"])

coords = {
    "東京 (Tokyo)": (35.6785, 139.6823),
    "大阪 (Osaka)": (34.6937, 135.5023),
    "名古屋 (Nagoya)": (35.1815, 136.9066)
}
lat, lon = coords[location]

# タブの作成
tab1, tab2, tab3 = st.tabs(["📊 時間別の雨予報（詳細）", "🗺️ リアルタイム雨雲レーダー", "🏢 気象機関ごとの比較一覧"])

# ---------------------------------------------------------
# タブ1: 時間別雨予報グラフィック
# ---------------------------------------------------------
with tab1:
    st.subheader(f"⏱️ {location} の本日の時間別降水予報 (Open-Meteo API)")
    
    df_hourly = get_open_meteo_hourly(lat, lon)
    
    if not df_hourly.empty:
        # 今日の雨のピーク・合算値などの概要表示
        max_precip = df_hourly["降水量 (mm/h)"].max()
        max_prob = df_hourly["降水確率 (%)"].max()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("本日の最大1時間雨量", f"{max_precip} mm/h")
        col2.metric("本日の最大降水確率", f"{max_prob} %")
        col3.metric("雨の注意度", "☔ 傘が必要" if max_precip > 0.5 or max_prob > 50 else "☀️ 傘不要")

        # 降水量グラフの描画
        st.write("▼ 1時間ごとの予想降水量 (mm/h)")
        st.bar_chart(df_hourly.set_index("時間")["降水量 (mm/h)"])
        
        # テーブルデータの表示
        with st.expander("詳細な数値データを表示"):
            st.dataframe(df_hourly, use_container_width=True)

# ---------------------------------------------------------
# タブ2: 埋め込み雨雲レーダー
# ---------------------------------------------------------
with tab2:
    st.subheader("🗺️ 雨雲レーダー（動的マップ）")
    st.write("雨雲のリアルタイム推移をインタラクティブに確認できます。")
    
    # RainViewerの雨雲レーダータイルをFoliumマップにレイヤー追加
    m = folium.Map(location=[lat, lon], zoom_start=9)
    
    # 雨雲レーダータイルの重ね合わせ (RainViewer API)
    radar_url = "https://tilecache.rainviewer.com/v2/radar/nowcast_60/256/{z}/{x}/{y}/2/1_1.png"
    folium.TileLayer(
        tiles=radar_url,
        attr="RainViewer",
        name="雨雲レーダー",
        overlay=True,
        control=True,
        opacity=0.7
    ).add_to(m)
    
    # マップを画面上に埋め込み表示
    st_folium(m, width=900, height=500)

# ---------------------------------------------------------
# タブ3: 各機関の比較一覧
# ---------------------------------------------------------
with tab3:
    st.subheader("🏢 各気象サービスデータの統合比較")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### 1. 気象庁 (JMA) の予報")
        df_jma = get_jma_pops()
        if not df_jma.empty:
            st.dataframe(df_jma, use_container_width=True)
            
    with col_b:
        st.write("### 2. Open-Meteo (数値予測)")
        if not df_hourly.empty:
            # 降水確率がある時間帯のみピックアップ
            st.dataframe(df_hourly[df_hourly["降水確率 (%)"] > 0], use_container_width=True)