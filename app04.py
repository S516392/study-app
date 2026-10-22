import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from datetime import datetime, timedelta, timezone


class App04:
    """天気予報アプリ"""

    # OpenWeatherMap API（無料枠）
    API_KEY = "YOUR_API_KEY_HERE"
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    WEATHER_ICONS = {
        "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
        "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
        "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("天気予報アプリ")
        self.root.geometry("600x540")
        self.root.minsize(600, 540)
        self.root.configure(bg="#e8f4fd")
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg="#1976d2", pady=10)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="🌤️ 天気予報アプリ",
                 font=("Noto Sans JP", 15, "bold"),
                 bg="#1976d2", fg="white").pack(side=tk.LEFT, padx=12)

        # 検索バー
        search_frame = tk.Frame(self.root, bg="#e8f4fd", pady=10)
        search_frame.pack(fill=tk.X, padx=16)
        tk.Label(search_frame, text="都市名 (英語):",
                 bg="#e8f4fd", font=("Noto Sans JP", 11)).pack(side=tk.LEFT)
        self.city_var = tk.StringVar(value="Tokyo")
        city_entry = ttk.Entry(search_frame, textvariable=self.city_var,
                               font=("Arial", 12), width=20)
        city_entry.pack(side=tk.LEFT, padx=8)
        city_entry.bind("<Return>", lambda e: self._search())
        ttk.Button(search_frame, text="🔍 検索",
                   command=self._search).pack(side=tk.LEFT)

        # プリセット都市ボタン
        preset_frame = tk.Frame(self.root, bg="#e8f4fd")
        preset_frame.pack(fill=tk.X, padx=16)
        for city in ["Tokyo", "Osaka", "Sapporo", "Fukuoka", "London", "New York"]:
            tk.Button(preset_frame, text=city, bg="#90caf9",
                      relief=tk.FLAT, font=("Arial", 9), padx=6,
                      command=lambda c=city: (self.city_var.set(c), self._search())
                      ).pack(side=tk.LEFT, padx=2, pady=4)

        # 現在の天気パネル
        panel_bg = "#ffffff"
        self.current_frame = tk.LabelFrame(self.root, text="現在の天気",
                                           bg=panel_bg, padx=12, pady=12,
                                           font=("Noto Sans JP", 10))
        self.current_frame.pack(fill=tk.X, padx=16, pady=6)
        self.weather_icon_label = tk.Label(self.current_frame, text="",
                                           font=("Segoe UI Emoji", 40),
                                           bg=panel_bg)
        self.weather_icon_label.grid(row=0, column=0, rowspan=3, padx=12)
        self.city_label = tk.Label(self.current_frame, text="---",
                                   font=("Noto Sans JP", 18, "bold"),
                                   bg=panel_bg)
        self.city_label.grid(row=0, column=1, sticky="w")
        self.temp_label = tk.Label(self.current_frame, text="--°C",
                                   font=("Arial", 28, "bold"), fg="#1976d2",
                                   bg=panel_bg)
        self.temp_label.grid(row=1, column=1, sticky="w")
        self.desc_label = tk.Label(self.current_frame, text="",
                                   font=("Noto Sans JP", 11),
                                   bg=panel_bg)
        self.desc_label.grid(row=2, column=1, sticky="w")

        # 詳細情報
        detail_frame = tk.Frame(self.current_frame, bg=panel_bg)
        detail_frame.grid(row=0, column=2, rowspan=3, padx=20, sticky="n")
        self.detail_labels = {}
        for i, key in enumerate(["湿度", "風速", "体感温度", "気圧"]):
            tk.Label(detail_frame, text=f"{key}:", font=("Arial", 10),
                     bg=panel_bg).grid(row=i, column=0, sticky="w", pady=2)
            lbl = tk.Label(detail_frame, text="--", font=("Arial", 10, "bold"),
                           bg=panel_bg, fg="#1976d2")
            lbl.grid(row=i, column=1, sticky="w", padx=8)
            self.detail_labels[key] = lbl

        # 5日間予報
        forecast_frame = tk.LabelFrame(self.root, text="5日間予報",
                                       bg="#e8f4fd", padx=8, pady=8,
                                       font=("Noto Sans JP", 10))
        forecast_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))
        self.forecast_canvas = tk.Canvas(forecast_frame, bg="#f5f9ff",
                                         highlightthickness=0, height=160)
        self.forecast_canvas.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="都市名を入力して検索してください")
        tk.Label(self.root, textvariable=self.status_var,
                 bg="#dde", font=("Arial", 9), anchor="w", padx=8
                 ).pack(fill=tk.X, side=tk.BOTTOM)

    def _search(self):
        city = self.city_var.get().strip()
        if not city:
            return
        self.status_var.set(f"取得中: {city} ...")
        threading.Thread(target=self._fetch_weather, args=(city,),
                         daemon=True).start()

    def _fetch_weather(self, city):
        # requests はクエリ文字列を params= の辞書から組み立てる
        # （都市名の空白や記号のURLエンコードも自動で処理される）
        params = {"q": city, "appid": self.API_KEY,
                  "units": "metric", "lang": "ja"}
        try:
            # 現在天気
            resp = requests.get(f"{self.BASE_URL}/weather",
                                params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()          # JSON を dict に変換
            self.root.after(0, self._update_current, data)

            # 5日間予報（3時間ごと最大40件）
            resp = requests.get(f"{self.BASE_URL}/forecast",
                                params={**params, "cnt": 40}, timeout=10)
            resp.raise_for_status()
            forecast = resp.json()
            self.root.after(0, self._update_forecast, forecast)
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            if code == 401:
                msg = "APIキーが無効です。YOUR_API_KEY_HEREを実際のキーに置き換えてください"
            elif code == 404:
                msg = f"都市が見つかりません: {city}"
            else:
                msg = f"HTTPエラー: {code}"
            self.root.after(0, self._show_demo, city, msg)
        except requests.exceptions.Timeout:
            self.root.after(0, self._show_demo, city, "通信がタイムアウトしました")
        except requests.exceptions.RequestException as e:
            # 例外メッセージにはAPIキー付きURLが含まれるので型名だけ表示する
            self.root.after(0, self._show_demo, city,
                            f"通信エラー: {type(e).__name__}")
        except Exception as e:
            self.root.after(0, self._show_demo, city, str(e))

    def _update_current(self, data):
        name = data["name"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        hum = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        pres = data["main"]["pressure"]
        desc = data["weather"][0]["description"]
        main = data["weather"][0]["main"]
        icon = self.WEATHER_ICONS.get(main, "🌡️")

        self.weather_icon_label.config(text=icon)
        self.city_label.config(text=name)
        self.temp_label.config(text=f"{temp:.1f}°C")
        self.desc_label.config(text=desc)
        self.detail_labels["湿度"].config(text=f"{hum}%")
        self.detail_labels["風速"].config(text=f"{wind} m/s")
        self.detail_labels["体感温度"].config(text=f"{feels:.1f}°C")
        self.detail_labels["気圧"].config(text=f"{pres} hPa")
        self.status_var.set(f"取得完了: {name}  ({datetime.now().strftime('%H:%M')})")

    def _update_forecast(self, data):
        self.forecast_canvas.delete("all")
        # dt・dt_txt はどちらも UTC なので、city.timezone（UTC からのずれ・秒）で現地時刻に直す
        tz = timezone(timedelta(seconds=data["city"]["timezone"]))
        # 1日1エントリに集約（現地時刻の正午にいちばん近いデータを優先）
        days = {}
        for item in data["list"]:
            local = datetime.fromtimestamp(item["dt"], tz)  # dt は UNIX 時刻（UTC）
            gap = abs(local.hour + local.minute / 60 - 12)
            if local.date() not in days or gap < days[local.date()][0]:
                days[local.date()] = (gap, item)
        entries = [(day, item) for day, (gap, item) in days.items()][:5]
        w = self.forecast_canvas.winfo_width() or 560
        col_w = w // max(len(entries), 1)
        for i, (day, item) in enumerate(entries):
            x = i * col_w + col_w // 2
            weekday = ["月", "火", "水", "木", "金", "土", "日"][day.weekday()]
            temp = item["main"]["temp"]
            main = item["weather"][0]["main"]
            icon = self.WEATHER_ICONS.get(main, "🌡️")
            desc = item["weather"][0]["description"]

            self.forecast_canvas.create_text(x, 20, text=f"{day:%m-%d} ({weekday})",
                                             font=("Arial", 9))
            self.forecast_canvas.create_text(x, 50, text=icon,
                                             font=("Segoe UI Emoji", 22))
            self.forecast_canvas.create_text(x, 90, text=f"{temp:.0f}°C",
                                             font=("Arial", 13, "bold"), fill="#1976d2")
            self.forecast_canvas.create_text(x, 115, text=desc,
                                             font=("Arial", 8), fill="#555")
            if i < len(entries) - 1:
                self.forecast_canvas.create_line(
                    (i+1)*col_w, 10, (i+1)*col_w, 140, fill="#ccc")

    def _show_demo(self, city, error_msg):
        """APIキー未設定時はデモデータを表示"""
        self.weather_icon_label.config(text="☀️")
        self.city_label.config(text=f"{city} (デモ)")
        self.temp_label.config(text="22.5°C")
        self.desc_label.config(text="晴れ (デモデータ)")
        self.detail_labels["湿度"].config(text="55%")
        self.detail_labels["風速"].config(text="3.2 m/s")
        self.detail_labels["体感温度"].config(text="21.8°C")
        self.detail_labels["気圧"].config(text="1013 hPa")
        self.status_var.set(f"⚠ {error_msg}  ※デモ表示中")

        # デモ予報
        self.forecast_canvas.delete("all")
        demo = [("☀️", "22°C", "晴れ"), ("⛅", "19°C", "曇り"),
                ("🌧️", "16°C", "雨"), ("☁️", "18°C", "曇り"),
                ("☀️", "24°C", "晴れ")]
        w = self.forecast_canvas.winfo_width() or 560
        col_w = w // 5
        from datetime import timedelta, date
        for i, (icon, temp, desc) in enumerate(demo):
            d = date.today() + timedelta(days=i)
            weekday = ["月", "火", "水", "木", "金", "土", "日"][d.weekday()]
            x = i * col_w + col_w // 2
            self.forecast_canvas.create_text(
                x, 20, text=f"{d.strftime('%m/%d')} ({weekday})", font=("Arial", 9))
            self.forecast_canvas.create_text(x, 50, text=icon,
                                             font=("Segoe UI Emoji", 22))
            self.forecast_canvas.create_text(x, 90, text=temp,
                                             font=("Arial", 13, "bold"), fill="#1976d2")
            self.forecast_canvas.create_text(x, 115, text=desc,
                                             font=("Arial", 8), fill="#555")


if __name__ == "__main__":
    root = tk.Tk()
    app = App04(root)
    root.mainloop()
