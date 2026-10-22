import requests
import pandas as pd

# 取得したい都市の緯度・経度リスト
CITIES = {
    "東京": {"lat": 35.6785, "lon": 139.6823},
    "大阪": {"lat": 34.6937, "lon": 135.5022},
    "札幌": {"lat": 43.0642, "lon": 141.3469},
}

def get_open_meteo_weather(lat, lon):
    """Open-Meteo API から天気データを取得する関数"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia%2FTokyo"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 本日のデータ（先頭の要素）を抽出
        daily = data["daily"]
        return {
            "最高気温(℃)": daily["temperature_2m_max"][0],
            "最低気温(℃)": daily["temperature_2m_min"][0],
            "降水量(mm)": daily["precipitation_sum"][0],
        }
    except Exception as e:
        print(f"データ取得エラー: {e}")
        return None

def main():
    weather_results = []

    print("各地域の天気予報データを集約中...\n")
    
    for city_name, coords in CITIES.items():
        data = get_open_meteo_weather(coords["lat"], coords["lon"])
        if data:
            data["都市"] = city_name
            weather_results.append(data)

    # データを集約して見やすい表（DataFrame）に変換
    df = pd.DataFrame(weather_results)
    
    # 列の順序を整える
    df = df[["都市", "最高気温(℃)", "最低気温(℃)", "降水量(mm)"]]
    
    print("=== 集約結果 ===")
    print(df.to_string(index=False))

    # 必要に応じてCSVファイルに保存
    df.to_csv("weather_summary.csv", index=False, encoding="utf-8-sig")
    print("\n'weather_summary.csv' に結果を保存しました。")

if __name__ == "__main__":
    main()