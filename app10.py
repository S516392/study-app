import tkinter as tk
from tkinter import ttk
import random


class App10:
    """じゃんけんゲーム"""

    CHOICES = ["グー ✊", "チョキ ✌️", "パー 🖐️"]
    WINS = {0: 1, 1: 2, 2: 0}  # グー→チョキ、チョキ→パー、パー→グー

    def __init__(self, root):
        self.root = root
        self.root.title("じゃんけんゲーム")
        self.root.geometry("520x440")
        self.root.minsize(520, 440)
        self.root.configure(bg="#f8f9fc")
        self.wins = self.draws = self.losses = 0
        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg="#3776ab", pady=12)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="じゃんけんゲーム",
                 font=("Noto Sans JP", 16, "bold"),
                 bg="#3776ab", fg="white").pack()

        main_frame = tk.Frame(self.root, bg="#f8f9fc", padx=24, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="手を選んでください", bg="#f8f9fc",
                 font=("Noto Sans JP", 12)).pack(pady=(0, 10))

        # じゃんけんボタン
        btn_frame = tk.Frame(main_frame, bg="#f8f9fc")
        btn_frame.pack()
        for i, label in enumerate(self.CHOICES):
            tk.Button(btn_frame, text=label, font=("Noto Sans JP", 13, "bold"),
                      width=9, height=2, bg="#ffffff", activebackground="#dceeff",
                      relief=tk.RAISED, bd=2,
                      command=lambda x=i: self.play(x)).grid(row=0, column=i, padx=6)

        # 対戦表示
        vs_frame = tk.Frame(main_frame, bg="#f8f9fc")
        vs_frame.pack(pady=14)
        self.player_label = tk.Label(vs_frame, text="あなた\n　？　",
                                     font=("Noto Sans JP", 14, "bold"),
                                     bg="#f8f9fc", fg="#3776ab", width=10, justify="center")
        self.player_label.grid(row=0, column=0)
        tk.Label(vs_frame, text="VS", font=("Noto Sans JP", 16, "bold"),
                 bg="#f8f9fc", fg="#888").grid(row=0, column=1, padx=16)
        self.cpu_label = tk.Label(vs_frame, text="CPU\n　？　",
                                  font=("Noto Sans JP", 14, "bold"),
                                  bg="#f8f9fc", fg="#e74c3c", width=10, justify="center")
        self.cpu_label.grid(row=0, column=2)

        # 結果
        self.result_label = tk.Label(main_frame, text="", bg="#f8f9fc",
                                     font=("Noto Sans JP", 20, "bold"))
        self.result_label.pack(pady=6)

        # スコア
        self.score_label = tk.Label(main_frame, text="勝: 0  引: 0  負: 0",
                                    bg="#f8f9fc", font=("Noto Sans JP", 11), fg="#555")
        self.score_label.pack()

        ttk.Button(main_frame, text="リセット", command=self.reset).pack(pady=(10, 0))

    def play(self, player_idx):
        cpu_idx = random.randint(0, 2)
        player_name = self.CHOICES[player_idx].split()[0]
        cpu_name = self.CHOICES[cpu_idx].split()[0]

        self.player_label.config(text=f"あなた\n{self.CHOICES[player_idx]}")
        self.cpu_label.config(text=f"CPU\n{self.CHOICES[cpu_idx]}")

        if player_idx == cpu_idx:
            result, color = "引き分け 🤝", "#888"
            self.draws += 1
        elif self.WINS[player_idx] == cpu_idx:
            result, color = "あなたの勝ち！ 🎉", "#27ae60"
            self.wins += 1
        else:
            result, color = "あなたの負け 😢", "#e74c3c"
            self.losses += 1

        self.result_label.config(text=result, fg=color)
        self.score_label.config(
            text=f"勝: {self.wins}  引: {self.draws}  負: {self.losses}")

    def reset(self):
        self.wins = self.draws = self.losses = 0
        self.player_label.config(text="あなた\n　？　")
        self.cpu_label.config(text="CPU\n　？　")
        self.result_label.config(text="")
        self.score_label.config(text="勝: 0  引: 0  負: 0")


if __name__ == "__main__":
    root = tk.Tk()
    app = App10(root)
    root.mainloop()
