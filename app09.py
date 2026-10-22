import tkinter as tk
from tkinter import ttk, messagebox
import random


class App09:
    """数当てゲーム"""

    def __init__(self, root):
        self.root = root
        self.root.title("数当てゲーム")
        self.root.geometry("420x400")
        self.root.minsize(420, 400)
        self.root.configure(bg="#f8f9fc")
        self.answer = 0
        self.tries = 0
        self.max_tries = 7
        self._build_ui()
        self.new_game()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg="#3776ab", pady=12)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="数当てゲーム",
                 font=("Noto Sans JP", 16, "bold"),
                 bg="#3776ab", fg="white").pack()

        main_frame = tk.Frame(self.root, bg="#f8f9fc", padx=24, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.info_label = tk.Label(main_frame, text="", bg="#f8f9fc",
                                   font=("Noto Sans JP", 11), wraplength=360, justify="center")
        self.info_label.pack(pady=(0, 10))

        # 入力
        input_frame = tk.Frame(main_frame, bg="#f8f9fc")
        input_frame.pack()
        tk.Label(input_frame, text="予想 (1〜100):", bg="#f8f9fc",
                 font=("Noto Sans JP", 11)).pack(side=tk.LEFT)
        self.entry = ttk.Entry(input_frame, width=8, font=("Arial", 14), justify="center")
        self.entry.pack(side=tk.LEFT, padx=8)
        self.entry.bind("<Return>", lambda e: self.guess())
        ttk.Button(input_frame, text="判定", command=self.guess).pack(side=tk.LEFT)

        # ヒント表示
        self.hint_label = tk.Label(main_frame, text="", bg="#f8f9fc",
                                   font=("Noto Sans JP", 22, "bold"), fg="#3776ab")
        self.hint_label.pack(pady=10)

        # 試行回数バー
        bar_frame = tk.Frame(main_frame, bg="#f8f9fc")
        bar_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(bar_frame, text="残り試行回数:", bg="#f8f9fc",
                 font=("Noto Sans JP", 10)).pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(bar_frame, maximum=self.max_tries,
                                        length=180, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=8)
        self.tries_label = tk.Label(bar_frame, text="", bg="#f8f9fc",
                                    font=("Noto Sans JP", 10))
        self.tries_label.pack(side=tk.LEFT)

        # 履歴
        history_frame = ttk.LabelFrame(main_frame, text="予想履歴", padding=6)
        history_frame.pack(fill=tk.BOTH, expand=True)
        self.history_text = tk.Text(history_frame, font=("Courier", 10),
                                    bg="white", relief=tk.FLAT, state=tk.DISABLED, height=4)
        self.history_text.pack(fill=tk.BOTH, expand=True)

        ttk.Button(main_frame, text="新しいゲーム", command=self.new_game).pack(pady=(8, 0))

    def new_game(self):
        self.answer = random.randint(1, 100)
        self.tries = 0
        self.history = []
        self.entry.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.hint_label.config(text="")
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        self.history_text.config(state=tk.DISABLED)
        self.info_label.config(text=f"1〜100の数字を当ててください！（最大{self.max_tries}回）")
        self._update_bar()

    def guess(self):
        text = self.entry.get().strip()
        if not text:
            return
        try:
            num = int(text)
        except ValueError:
            messagebox.showwarning("エラー", "整数を入力してください")
            return
        if not 1 <= num <= 100:
            messagebox.showwarning("エラー", "1〜100の数字を入力してください")
            return

        self.tries += 1
        self.entry.delete(0, tk.END)

        if num == self.answer:
            self.hint_label.config(text="🎉 正解！", fg="#27ae60")
            self.info_label.config(text=f"{self.tries}回で正解しました！")
            self.entry.config(state=tk.DISABLED)
        elif self.tries >= self.max_tries:
            self.hint_label.config(text=f"😢 ゲームオーバー", fg="#e74c3c")
            self.info_label.config(text=f"正解は {self.answer} でした。")
            self.entry.config(state=tk.DISABLED)
        elif num < self.answer:
            self.hint_label.config(text="▲ もっと大きい", fg="#e67e22")
        else:
            self.hint_label.config(text="▼ もっと小さい", fg="#e67e22")

        self.history.append(f"第{self.tries:02d}回: {num:3d}")
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        self.history_text.insert("1.0", "  ".join(self.history[-6:]))
        self.history_text.config(state=tk.DISABLED)
        self._update_bar()

    def _update_bar(self):
        remaining = self.max_tries - self.tries
        self.progress["value"] = remaining
        self.tries_label.config(text=f"{remaining}/{self.max_tries}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App09(root)
    root.mainloop()
