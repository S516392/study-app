import math
import tkinter as tk
import unicodedata
from tkinter import ttk, messagebox

# 肥満度分類（日本肥満学会）。(BMIの下限, 判定名) を大きいほうから並べる
BMI_CATEGORIES = [
    (40.0, "肥満（4度）"),
    (35.0, "肥満（3度）"),
    (30.0, "肥満（2度）"),
    (25.0, "肥満（1度）"),
    (18.5, "普通体重"),
    (0.0, "低体重（やせ）"),
]


def parse_number(text, label):
    """入力欄の文字列を数値にする。全角を半角に寄せ、nan・inf・0以下を弾く"""
    normalized = unicodedata.normalize("NFKC", text).replace("−", "-").strip()
    value = float(normalized)          # 数値として読めなければ ValueError
    if not math.isfinite(value):       # float() は "nan" と "inf" を通してしまう
        raise ValueError(f"{label}には有限の数値を入力してください")
    if value <= 0:
        raise ValueError(f"{label}は0より大きい値を入力してください")
    return value


def judge_bmi(bmi):
    """BMI から肥満度分類の判定名を返す"""
    for lower, name in BMI_CATEGORIES:
        if bmi >= lower:
            return name
    raise ValueError(f"判定できないBMIです: {bmi}")


class App04:
    """BMI計算アプリ"""

    def __init__(self, root):
        self.root = root
        self.root.title("BMI計算アプリ")
        self.root.geometry("500x500")   # 結果は10行。400だと5行しか見えない
        self.root.minsize(500, 500)
        self.root.configure(bg="#f8f9fc")
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg="#3776ab", pady=12)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="BMI計算アプリ",
                 font=("Noto Sans JP", 16, "bold"),
                 bg="#3776ab", fg="white").pack()

        main_frame = tk.Frame(self.root, bg="#f8f9fc", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="入力", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(input_frame, text="身長 (cm):").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_height = ttk.Entry(input_frame, width=20, font=("Arial", 12))
        self.entry_height.grid(row=0, column=1, padx=8, sticky="ew")
        self.entry_height.bind("<Return>", lambda e: self.process())

        tk.Label(input_frame, text="体重 (kg):").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_weight = ttk.Entry(input_frame, width=20, font=("Arial", 12))
        self.entry_weight.grid(row=1, column=1, padx=8, sticky="ew")
        self.entry_weight.bind("<Return>", lambda e: self.process())
        input_frame.columnconfigure(1, weight=1)

        ttk.Button(main_frame, text="計算する", command=self.process).pack(pady=8)

        result_frame = ttk.LabelFrame(main_frame, text="結果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, font=("Noto Sans JP", 11),
                                   bg="white", relief=tk.FLAT, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.entry_height.focus_set()

    def process(self):
        height_str = self.entry_height.get().strip()
        weight_str = self.entry_weight.get().strip()
        if not height_str or not weight_str:
            messagebox.showwarning("警告", "身長と体重を入力してください")
            return
        try:
            result = self._calculate(height_str, weight_str)
        except ValueError as e:
            messagebox.showerror("エラー", f"入力値が不正です: {e}")
            return
        self._show_result(result)

    def _calculate(self, height_str, weight_str):
        height_cm = parse_number(height_str, "身長")
        weight = parse_number(weight_str, "体重")

        # cm と m を取り違えると BMI が 10000 倍ずれるので、計算する前に止める
        if height_cm < 30:
            raise ValueError(
                f"身長は cm で入力してください（{height_cm:g} は m での入力に見えます）"
            )
        if height_cm > 300:
            raise ValueError("身長は 30〜300 cm の範囲で入力してください")
        if not 5 <= weight <= 500:
            raise ValueError("体重は 5〜500 kg の範囲で入力してください")

        height_m = height_cm / 100
        # 画面に出す桁で丸めてから判定する。丸めないと 24.999999999999996 が
        # 「25.00」と表示されているのに「普通体重」と判定されてしまう
        bmi = round(weight / height_m ** 2, 2)
        ideal_weight = 22.0 * height_m ** 2

        return (
            f"【BMI計算結果】\n\n"
            f"身長:     {height_cm:.1f} cm\n"
            f"体重:     {weight:.1f} kg\n"
            f"BMI:      {bmi:.2f}\n"
            f"判定:     {judge_bmi(bmi)}\n\n"
            f"標準体重: {ideal_weight:.1f} kg（BMI=22）\n\n"
            f"※学習用のサンプルです。医学的な診断ではありません。"
        )

    def _show_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = App04(root)
    root.mainloop()