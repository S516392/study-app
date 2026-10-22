import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 画面全体のレイアウト設定
st.set_page_config(page_title="リアルタイム雨情報ダッシュボード", layout="wide")

st.title("🌧️ 雨の降り方＆雨雲レーダー比較ダッシュボード")

# ---------------------------------------------------------
# スポット情報（名称・住所・座標・気象庁地域コード・Yahoo地域ID）の設定
# ---------------------------------------------------------
LOCATIONS = {
    "杉本（大阪市住吉区）": {
        "address": "大阪府大阪市住吉区杉本３丁目１",
        "lat": 34.5904,
        "lon": 135.5050,
        "jma_code": "270000",
        "yahoo_url": "https://weather.yahoo.co.jp/weather/jp/27/6200/27120.html"
    },
    "長居（大阪市東住吉区）": {
        "address": "大阪府大阪市東住吉区長居公園１−１",
        "lat": 34.6133,
        "lon": 135.5186,
        "jma_code": "270000",
        "yahoo_url": "https://weather.yahoo.co.jp/weather/jp/27/6200/27121.html"
    },
    "大泉緑地（堺市北区）": {
        "address": "大阪府堺市北区中村町",
        "lat": 34.5654,
        "lon": 135.5226,
        "jma_code": "270000",
        "yahoo_url": "https://weather.yahoo.co.jp/weather/jp/27/6200/27146.html"
    },
    "鶴見緑地（大阪市鶴見区）": {
        "address": "大阪府大阪市鶴見区浜１丁目２−６",
        "lat": 34.7108,
        "lon": 135.5772,
        "jma_code": "270000",
        "yahoo_url": "https://weather.yahoo.co.jp/weather/jp/27/6200/27124.html"
    },
    "二色浜（大阪府貝塚市）": {
        "address": "大阪府貝塚市脇浜３４",
        "lat": 34.4430,
        "lon": 135.3450,
        "jma_code": "270000",
        "yahoo_url": "https://weather.yahoo.co.jp/weather/jp/27/6200/27208.html"
    },
    "向島（京都市伏見区）": {
        "address": "京都府京都市伏見区向島二ノ丸町１５１−５０",
        "lat": 34.9172,
        "lon": 135.7701,
        "jma_code": "260000",
        "yahoo_url": "https://weather.yahoo.co.jp/weather/jp/26/6110/26109.html"
    }
}

# ---------------------------------------------------------
# データ取得処理
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def get_open_meteo_hourly(lat, lon):
    """Open-Meteoから指定座標の当日1時間ごとの降水量(mm)と確率(%)を取得"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=precipitation,precipitation_probability"
        f"&timezone=Asia%2FTokyo&forecast_days=1"
    )
    try:
        res = requests.get(url, timeout=10)
        data = res.json()["hourly"]
        
        now_hour = datetime.now().hour
        df = pd.DataFrame({
            "時間": [f"{int(t.split('T')[1].split(':')[0])}:00" for t in data["time"]],
            "hour": [int(t.split('T')[1].split(':')[0]) for t in data["time"]],
            "Open-Meteo 降水量(mm/h)": data["precipitation"],
            "Open-Meteo 降水確率(%)": data["precipitation_probability"]
        })
        df = df[df["hour"] >= now_hour].drop(columns=["hour"])
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_jma_pops(jma_code):
    """気象庁JSON APIから指定府県の直近（24時間以内）の降水確率を取得"""
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{jma_code}.json"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        pops_series = data[0]["timeSeries"][1]
        
        times = [datetime.fromisoformat(t) for t in pops_series["timeDefines"]]
        pops = pops_series["areas"][0]["pops"]
        
        now = datetime.now()
        jma_list = []
        
        for dt, pop in zip(times, pops):
            dt_end = dt + timedelta(hours=6)
            # 終了時刻が現在より未来、かつ今後24時間以内のデータであれば抽出
            if dt_end > now and dt < now + timedelta(hours=24):
                time_label = f"{dt.strftime('%m/%d %H:00')}〜{dt_end.strftime('%H:00')}"
                jma_list.append({
                    "時間帯": time_label,
                    "気象庁 降水確率(%)": f"{pop}%"
                })
                
        return pd.DataFrame(jma_list)
    except Exception as e:
        return pd.DataFrame()

# ---------------------------------------------------------
# サイドバー
# ---------------------------------------------------------
st.sidebar.header("📍 場所を選択")
selected_name = st.sidebar.selectbox("対象のスポットを選んでください", list(LOCATIONS.keys()))

spot_info = LOCATIONS[selected_name]
lat = spot_info["lat"]
lon = spot_info["lon"]
jma_code = spot_info["jma_code"]
yahoo_url = spot_info["yahoo_url"]

st.sidebar.markdown(f"**住所:**  \n{spot_info['address']}")

# 各機関の公式リンク集（サイドバーにも配置）
st.sidebar.markdown("---")
st.sidebar.subheader("🔗 各気象サービスの公式ページ")
wni_url = f"https://weathernews.jp/onebox/radar/lat={lat}/lon={lon}/"
st.sidebar.markdown(f"- ☀️ [ウェザーニュース ({selected_name})]({wni_url})")
st.sidebar.markdown(f"- 🟡 [Yahoo!天気 ({selected_name})]({yahoo_url})")
st.sidebar.markdown(f"- 🔵 [気象庁 雨雲の動き (ナウキャスト)](https://www.jma.go.jp/bosai/nowc/)")

# ---------------------------------------------------------
# メイン画面
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📊 時間別の雨予報（機関比較）", "🗺️ ウェザーニュース 雨雲レーダー"])

# === タブ1: 時間別の雨予報 ===
with tab1:
    st.subheader(f"⏱️ {selected_name} 本日の残り時間帯の雨予報比較")
    
    # 公式Webサイトへのリンクボタンエリア
    st.info(f"""
    🔗 **各気象サービスの公式ピンポイント予報ページ**  
    ・ [ウェザーニュース公式 (5分〜10分単位の雨雲予測)]({wni_url})  
    ・ [Yahoo!天気公式 ({selected_name}のピンポイント天気)]({yahoo_url})  
    ・ [気象庁ナウキャスト (高解像度降水ナウキャスト)](https://www.jma.go.jp/bosai/nowc/)
    """)
    
    df_om = get_open_meteo_hourly(lat, lon)
    df_jma = get_jma_pops(jma_code)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔹 Open-Meteo（1時間ごとのピンポイント予測）")
        if not df_om.empty:
            st.dataframe(df_om, use_container_width=True, hide_index=True)
            st.caption("▼ 1時間ごとの予想降水量 (mm/h)")
            st.bar_chart(df_om.set_index("時間")["Open-Meteo 降水量(mm/h)"])
        else:
            st.warning("Open-Meteoデータの取得に失敗しました。")

    with col2:
        area_label = "京都府" if jma_code == "260000" else "大阪府"
        st.markdown(f"### 🔹 気象庁 JMA（{area_label}全域の確率）")
        if not df_jma.empty:
            st.dataframe(df_jma, use_container_width=True, hide_index=True)
        else:
            st.info("本日の残り時間帯の気象庁発表データはありません。")

# === タブ2: ウェザーニュース 雨雲レーダー ===
with tab2:
    st.subheader(f"🗺️ ウェザーニュース リアルタイム雨雲レーダー ({selected_name})")
    
    st.markdown(f"🔗 **[ウェザーニュース公式で開く（フルスクリーン表示）]({wni_url})**")
    
    components.iframe(wni_url, height=650, scrolling=True)