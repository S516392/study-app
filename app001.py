import tkinter as tk
from tkinter import font as tkfont


def on_button_click():
    """ボタンがクリックされたときの処理"""
    current = label_message.cget("text")
    if current == "Hello, World!":
        label_message.config(
            text="Pythonの学習を始めよう！",
            fg="#e74c3c"
        )
    else:
        label_message.config(
            text="Hello, World!",
            fg="#2c3e50"
        )


def on_hover_enter(event):
    """マウスオーバー時にボタンの色を変える"""
    btn_greet.config(bg="#2980b9")


def on_hover_leave(event):
    """マウスが離れたときにボタンの色を元に戻す"""
    btn_greet.config(bg="#3498db")


# ============================================================
# ウィンドウの作成
# ============================================================
root = tk.Tk()
root.title("Hello World - Python GUI入門")
root.geometry("420x280")
root.resizable(False, False)        # サイズ変更を禁止
root.configure(bg="#ecf0f1")        # 背景色

# ============================================================
# フォント定義
# ============================================================
font_title = tkfont.Font(family="Noto Sans JP", size=20, weight="bold")
font_btn   = tkfont.Font(family="Noto Sans JP", size=11, weight="bold")

# ============================================================
# ウィジェットの配置
# ============================================================
# タイトルラベル
label_title = tk.Label(
    root,
    text="🐍 Python GUI 入門",
    font=font_title,
    bg="#3498db",
    fg="white",
    pady=12
)
label_title.pack(fill=tk.X)

# メッセージラベル
label_message = tk.Label(
    root,
    text="Hello, World!",
    font=("Noto Sans JP", 24, "bold"),
    bg="#ecf0f1",
    fg="#2c3e50",
    pady=30
)
label_message.pack()

# ボタン
btn_greet = tk.Button(
    root,
    text="クリックしてね！",
    font=font_btn,
    bg="#3498db",
    fg="white",
    activebackground="#2980b9",
    activeforeground="white",
    relief=tk.FLAT,
    padx=20,
    pady=8,
    cursor="hand2",         # カーソルを手の形に
    command=on_button_click
)
btn_greet.pack()

# ホバーイベントをバインド
btn_greet.bind("<Enter>", on_hover_enter)
btn_greet.bind("<Leave>", on_hover_leave)

# 説明ラベル
label_hint = tk.Label(
    root,
    text="ボタンをクリックするとメッセージが変わります",
    font=("Noto Sans JP", 9),
    bg="#ecf0f1",
    fg="#7f8c8d"
)
label_hint.pack(pady=(8, 0))

# ============================================================
# イベントループ開始（これを忘れるとウィンドウが表示されない）
# ============================================================
root.mainloop()
