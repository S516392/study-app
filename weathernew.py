import requests
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# 1. 気象庁（JMA）公式JSON API
# ---------------------------------------------------------
def get_jma_rain_hourly():
    """気象庁の時系列予報JSONから当日の降水確率（3〜6時間ごと）を取得"""
    url = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        pops_series = data[0]["timeSeries"][1]
        time_defines = pops_series["timeDefines"]
        pops = pops_series["areas"][0]["pops"]
        
        now = datetime.now()
        rain_info = []
        
        for t_str, pop in zip(time_defines, pops):
            dt = datetime.fromisoformat(t_str)
            # 本日の日付かつ、現在の時刻以降のデータのみ抽出
            if dt.date() == now.date() and dt >= now:
                time_label = dt.strftime("%H:00")
                rain_info.append(f"{time_label}~: {pop}%")
                
        forecast_text = " / ".join(rain_info) if rain_info else "本日の残り時間帯の予報なし"
        
        return {
            "情報元": "気象庁 (JMA)",
            "取得方式": "公式JSON API",
            "雨データ種別": "降水確率 (%)",
            "時間別・降雨の予報・様子": forecast_text,
            "雨雲レーダー情報": "https://www.jma.go.jp/bosai/nowc/"
        }
    except Exception as e:
        return {
            "情報元": "気象庁 (JMA)",
            "取得方式": "公式JSON API",
            "雨データ種別": "降水確率 (%)",
            "時間別・降雨の予報・様子": f"エラー: {e}",
            "雨雲レーダー情報": "https://www.jma.go.jp/bosai/nowc/"
        }


# ---------------------------------------------------------
# 2. Open-Meteo（リアルタイム1時間ごとの降水量・確率）
# ---------------------------------------------------------
def get_open_meteo_rain_hourly(lat=35.6785, lon=139.6823):
    """Open-Meteo API から本日の現在時刻以降の予測を取得"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=precipitation,precipitation_probability"
        f"&timezone=Asia%2FTokyo&forecast_days=1"
    )
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()["hourly"]
        
        times = data["time"]
        precip = data["precipitation"]
        prob = data["precipitation_probability"]
        
        now = datetime.now()
        rain_hours = []
        
        for t_str, p, pr in zip(times, precip, prob):
            dt = datetime.fromisoformat(t_str)
            # 現在時刻以降のみを表示対象にする
            if dt >= now:
                time_label = dt.strftime("%H:00")
                # 雨が降る予想（降雨量>0 または 確率>0）をわかりやすく記述
                if p > 0 or pr > 0:
                    rain_hours.append(f"{time_label}: {p}mm ({pr}%)")
                else:
                    rain_hours.append(f"{time_label}: 0mm (0%)")
                
        if rain_hours:
            # 表示が見づらくならないよう直近6時間分を基本抽出
            forecast_text = " / ".join(rain_hours[:6])
            if len(rain_hours) > 6:
                forecast_text += " 他"
        else:
            forecast_text = "本日の残り時間帯は降水なし"
            
        return {
            "情報元": "Open-Meteo",
            "取得方式": "無料Web API (キー不要)",
            "雨データ種別": "1時間毎 降水量(mm) & 確率",
            "時間別・降雨の予報・様子": forecast_text,
            "雨雲レーダー情報": "数値モデル予測（レーダー画像なし）"
        }
    except Exception as e:
        return {
            "情報元": "Open-Meteo",
            "取得方式": "無料Web API",
            "雨データ種別": "1時間毎 降水量(mm) & 確率",
            "時間別・降雨の予報・様子": f"エラー: {e}",
            "雨雲レーダー情報": "-"
        }


# ---------------------------------------------------------
# 3. 民間サービス（スクレイピング／公式Webへの案内リンク）
# ---------------------------------------------------------
def get_yahoo_rain_info():
    """Yahoo!天気の雨雲レーダー・ピンポイント天気情報へのリンク"""
    return {
        "情報元": "Yahoo!天気 (JWA)",
        "取得方式": "公式Web参照",
        "雨データ種別": "雨雲レーダー / 1時間天気",
        "時間別・降雨の予報・様子": "リアルタイム雨雲推移はWebから確認可能",
        "雨雲レーダー情報": "https://weather.yahoo.co.jp/weather/zoomradar/"
    }

def get_wni_rain_info():
    """ウェザーニュースの超密着雨雲レーダーへのリンク"""
    return {
        "情報元": "ウェザーニュース (WNI)",
        "取得方式": "公式Web参照",
        "雨データ種別": "5分単位超密着レーダー予報",
        "時間別・降雨の予報・様子": "5分〜10分単位の雨雲接近予測",
        "雨雲レーダー情報": "https://weathernews.jp/onebox/radar/"
    }


# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
def main():
    print("=== 当日の『リアルタイム雨の降り方・降水予報』を集約中... ===\n")
    
    results = [
        get_jma_rain_hourly(),
        get_open_meteo_rain_hourly(),
        get_yahoo_rain_info(),
        get_wni_rain_info()
    ]

    df = pd.DataFrame(results)
    
    cols = ["情報元", "取得方式", "雨データ種別", "時間別・降雨の予報・様子", "雨雲レーダー情報"]
    df = df[cols]
    
    print("【本日のリアルタイム雨予測一覧】")
    print(df.to_string(index=False))
    
    df.to_csv("today_rain_detailed.csv", index=False, encoding="utf-8-sig")
    print("\n'today_rain_detailed.csv' に保存しました。")

if __name__ == "__main__":
    main()