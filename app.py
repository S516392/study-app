import json
import os
import time
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "study_roadmap.json"

ROUND_COLORS = {
    0: ("#E2E8F0", "#475569"),  # 未完了: グレー
    1: ("#10B981", "white"),  # 1周目: 緑
    2: ("#3B82F6", "white"),  # 2周目: 青
    3: ("#8B5CF6", "white"),  # 3周目: 紫
}


class LectureRangeDialog(tk.Toplevel):

    def __init__(self, parent, lec_count, start_p, end_p):
        super().__init__(parent)
        self.title("各講義のページ範囲を設定")
        self.geometry("380x420")
        self.configure(bg="#F8FAFC")
        self.transient(parent)
        self.grab_set()

        self.lec_count = lec_count
        self.start_p = start_p
        self.end_p = end_p
        self.result = None

        tk.Label(
            self,
            text=f"全{lec_count}回講義の範囲を設定してください\n(全体: p.{start_p} 〜 p.{end_p})",
            font=("Helvetica", 10, "bold"),
            bg="#F8FAFC",
            pady=10,
        ).pack()

        frame_container = tk.Frame(self, bg="#F8FAFC")
        frame_container.pack(fill="both", expand=True, padx=15, pady=5)

        canvas = tk.Canvas(frame_container, bg="#F8FAFC", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            frame_container, orient="vertical", command=canvas.yview
        )
        self.inputs_frame = tk.Frame(canvas, bg="#F8FAFC")

        self.inputs_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.inputs_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.entries = []
        pages_per_lec = (end_p - start_p + 1) // lec_count

        for i in range(lec_count):
            row = tk.Frame(self.inputs_frame, bg="#F8FAFC", pady=4)
            row.pack(fill="x")

            tk.Label(
                row,
                text=f"第{i+1}回:",
                font=("Helvetica", 9, "bold"),
                width=6,
                anchor="w",
                bg="#F8FAFC",
            ).pack(side="left")

            default_s = start_p + (i * pages_per_lec)
            default_e = (
                start_p + ((i + 1) * pages_per_lec) - 1
                if i < lec_count - 1
                else end_p
            )

            ent_s = tk.Entry(row, width=6)
            ent_s.insert(0, str(default_s))
            ent_s.pack(side="left", padx=2)

            tk.Label(row, text="〜", bg="#F8FAFC").pack(side="left")

            ent_e = tk.Entry(row, width=6)
            ent_e.insert(0, str(default_e))
            ent_e.pack(side="left", padx=2)

            tk.Label(
                row, text="P", font=("Helvetica", 8), bg="#F8FAFC"
            ).pack(side="left")
            self.entries.append((ent_s, ent_e))

        btn_frame = tk.Frame(self, bg="#F8FAFC", pady=10)
        btn_frame.pack(fill="x")
        save_btn = tk.Button(
            btn_frame,
            text="設定を決定して登録",
            command=self.on_save,
            bg="#4F46E5",
            fg="white",
            font=("Helvetica", 9, "bold"),
            padx=10,
            pady=4,
        )
        save_btn.pack()

    def on_save(self):
        ranges = []
        try:
            for i, (s_ent, e_ent) in enumerate(self.entries):
                s = int(s_ent.get())
                e = int(e_ent.get())
                if s > e:
                    messagebox.showerror(
                        "エラー",
                        f"第{i+1}回の開始ページが終了ページより大きくなっています。",
                    )
                    return
                ranges.append((i + 1, s, e))
            self.result = ranges
            self.destroy()
        except ValueError:
            messagebox.showerror(
                "エラー", "すべての範囲に適切な数値を入力してください。"
            )


class StudyApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("試験勉強・講義回別＆周回管理")
        self.geometry("1000x750")
        self.configure(bg="#F8FAFC")

        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.timer_job = None
        self.current_round = 1

        self.subjects = self.load_data()
        self.memo_entries = {}  # 各カードのメモ入力欄参照を保持
        self.setup_ui()
        self.render_subjects()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.subjects, f, ensure_ascii=False, indent=2)

    def setup_ui(self):
        header = tk.Frame(self, bg="#4F46E5", height=60)
        header.pack(fill="x", side="top")
        title_label = tk.Label(
            header,
            text="🎓 レジュメ・講義回別＆周回管理",
            font=("Helvetica", 16, "bold"),
            fg="white",
            bg="#4F46E5",
        )
        title_label.pack(side="left", padx=20, pady=15)

        self.overall_label = tk.Label(
            header,
            text="全体進捗: 0%",
            font=("Helvetica", 11, "bold"),
            fg="#FDE047",
            bg="#3730A3",
            padx=10,
            pady=5,
        )
        self.overall_label.pack(side="right", padx=20)

        main_frame = tk.Frame(self, bg="#F8FAFC")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        left_col = tk.Frame(main_frame, bg="#F8FAFC", width=320)
        left_col.pack(side="left", fill="y", padx=(0, 10))

        # 周回モード選択
        round_box = tk.LabelFrame(
            left_col,
            text="🔄 記録する周回数を選択",
            font=("Helvetica", 10, "bold"),
            bg="white",
            padx=10,
            pady=8,
        )
        round_box.pack(fill="x", pady=(0, 8))

        self.round_var = tk.IntVar(value=1)
        r_frame = tk.Frame(round_box, bg="white")
        r_frame.pack(fill="x")

        tk.Radiobutton(
            r_frame,
            text="1周目(緑)",
            variable=self.round_var,
            value=1,
            bg="white",
            fg="#10B981",
            font=("Helvetica", 9, "bold"),
            command=self.set_current_round,
        ).pack(side="left", expand=True)
        tk.Radiobutton(
            r_frame,
            text="2周目(青)",
            variable=self.round_var,
            value=2,
            bg="white",
            fg="#3B82F6",
            font=("Helvetica", 9, "bold"),
            command=self.set_current_round,
        ).pack(side="left", expand=True)
        tk.Radiobutton(
            r_frame,
            text="3周目(紫)",
            variable=self.round_var,
            value=3,
            bg="white",
            fg="#8B5CF6",
            font=("Helvetica", 9, "bold"),
            command=self.set_current_round,
        ).pack(side="left", expand=True)

        # ポモドーロタイマー
        timer_box = tk.LabelFrame(
            left_col,
            text="⏱️ 集中ポモドーロタイマー",
            font=("Helvetica", 10, "bold"),
            bg="white",
            padx=10,
            pady=8,
        )
        timer_box.pack(fill="x", pady=(0, 8))

        self.timer_label = tk.Label(
            timer_box,
            text="25:00",
            font=("Helvetica", 28, "bold"),
            fg="#4F46E5",
            bg="white",
        )
        self.timer_label.pack(pady=2)

        timer_btn_frame = tk.Frame(timer_box, bg="white")
        timer_btn_frame.pack(pady=2)

        self.start_btn = tk.Button(
            timer_btn_frame,
            text="スタート",
            command=self.toggle_timer,
            bg="#4F46E5",
            fg="white",
            font=("Helvetica", 8, "bold"),
            padx=8,
        )
        self.start_btn.pack(side="left", padx=4)

        reset_btn = tk.Button(
            timer_btn_frame,
            text="リセット",
            command=self.reset_timer,
            bg="#E2E8F0",
            fg="#334155",
            font=("Helvetica", 8),
        )
        reset_btn.pack(side="left", padx=4)

        # 範囲一括反映
        quick_box = tk.LabelFrame(
            left_col,
            text="⚡ 範囲を一括記録 (ページ指定のみ)",
            font=("Helvetica", 9, "bold"),
            bg="white",
            padx=10,
            pady=8,
        )
        quick_box.pack(fill="x", pady=(0, 8))

        tk.Label(
            quick_box, text="対象テキスト/レジュメ:", bg="white", font=("Helvetica", 8)
        ).pack(anchor="w")
        self.quick_select = ttk.Combobox(quick_box, state="readonly")
        self.quick_select.pack(fill="x", pady=(0, 4))

        range_frame = tk.Frame(quick_box, bg="white")
        range_frame.pack(fill="x", pady=2)
        self.quick_start_ent = tk.Entry(range_frame, width=5)
        self.quick_start_ent.pack(side="left")
        tk.Label(range_frame, text="〜", bg="white").pack(side="left", padx=2)
        self.quick_end_ent = tk.Entry(range_frame, width=5)
        self.quick_end_ent.pack(side="left")
        tk.Label(
            range_frame, text="ページ", bg="white", font=("Helvetica", 8)
        ).pack(side="left", padx=2)

        apply_btn = tk.Button(
            quick_box,
            text="選択中の周回数で色塗り",
            command=self.apply_quick_progress,
            bg="#10B981",
            fg="white",
            font=("Helvetica", 8, "bold"),
        )
        apply_btn.pack(fill="x", pady=(4, 0))

        # テキスト/レジュメ追加フォーム
        add_box = tk.LabelFrame(
            left_col,
            text="📖 科目・レジュメの追加",
            font=("Helvetica", 10, "bold"),
            bg="white",
            padx=10,
            pady=8,
        )
        add_box.pack(fill="x", pady=(0, 8))

        tk.Label(
            add_box, text="科目名:", bg="white", font=("Helvetica", 8)
        ).pack(anchor="w")
        self.sub_ent = tk.Entry(add_box)
        self.sub_ent.pack(fill="x", pady=(0, 4))

        tk.Label(
            add_box,
            text="レジュメ名 / テキスト名:",
            bg="white",
            font=("Helvetica", 8),
        ).pack(anchor="w")
        self.title_ent = tk.Entry(add_box)
        self.title_ent.pack(fill="x", pady=(0, 4))

        p_frame = tk.Frame(add_box, bg="white")
        p_frame.pack(fill="x", pady=2)

        tk.Label(
            p_frame,
            text="開始P:",
            bg="white",
            font=("Helvetica", 8),
        ).grid(row=0, column=0)
        self.start_p_ent = tk.Entry(p_frame, width=4)
        self.start_p_ent.grid(row=0, column=1, padx=(0, 2))

        tk.Label(
            p_frame,
            text="終了P:",
            bg="white",
            font=("Helvetica", 8),
        ).grid(row=0, column=2)
        self.end_p_ent = tk.Entry(p_frame, width=4)
        self.end_p_ent.grid(row=0, column=3, padx=(0, 2))

        tk.Label(
            p_frame, text="講義数:", bg="white", font=("Helvetica", 8)
        ).grid(row=0, column=4)
        self.lec_ent = tk.Entry(p_frame, width=4)
        self.lec_ent.insert(0, "4")
        self.lec_ent.grid(row=0, column=5)

        tk.Label(
            add_box,
            text="※ページ無し（回数のみ）の場合は開始/終了Pを空欄にしてください",
            font=("Helvetica", 7),
            fg="#64748B",
            bg="white",
        ).pack(anchor="w", pady=(2, 4))

        add_btn = tk.Button(
            add_box,
            text="ロードマップに追加",
            command=self.add_subject,
            bg="#1E293B",
            fg="white",
            font=("Helvetica", 9, "bold"),
        )
        add_btn.pack(fill="x", pady=(2, 0))

        # 全データ削除
        clear_all_btn = tk.Button(
            left_col,
            text="🗑️ すべての登録データを削除",
            command=self.clear_all_data,
            bg="#FEF2F2",
            fg="#EF4444",
            font=("Helvetica", 8, "bold"),
            bd=1,
            relief="groove",
        )
        clear_all_btn.pack(fill="x")

        # 右カラム
        right_col = tk.Frame(main_frame, bg="#F8FAFC")
        right_col.pack(side="right", fill="both", expand=True)

        canvas = tk.Canvas(right_col, bg="#F8FAFC", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            right_col, orient="vertical", command=canvas.yview
        )
        self.scrollable_frame = tk.Frame(canvas, bg="#F8FAFC")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def set_current_round(self):
        self.current_round = self.round_var.get()

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.timer_job:
                self.after_cancel(self.timer_job)
            self.start_btn.config(text="再開", bg="#4F46E5")
        else:
            self.timer_running = True
            self.start_btn.config(text="一時停止", bg="#F59E0B")
            self.count_down()

    def count_down(self):
        if self.timer_seconds > 0:
            m, s = divmod(self.timer_seconds, 60)
            self.timer_label.config(text=f"{m:02d}:{s:02d}")
            self.timer_seconds -= 1
            self.timer_job = self.after(1000, self.count_down)
        else:
            self.timer_running = False
            self.start_btn.config(text="スタート", bg="#4F46E5")
            messagebox.showinfo(
                "タイマー終了",
                "⏰ 25分の集中タイムが終了しました！お疲れ様でした。",
            )
            self.reset_timer()

    def reset_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_running = False
        self.timer_seconds = 25 * 60
        self.timer_label.config(text="25:00")
        self.start_btn.config(text="スタート", bg="#4F46E5")

    def save_memo(self, subject_id):
        """途中の進捗メモを保存"""
        ent = self.memo_entries.get(subject_id)
        if ent:
            memo_text = ent.get().strip()
            for s in self.subjects:
                if s["id"] == subject_id:
                    s["memo"] = memo_text
                    break
            self.save_data()
            messagebox.showinfo(
                "保存完了", "途中の進捗メモを保存しました！"
            )

    def render_subjects(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.memo_entries = {}

        if not self.subjects:
            empty_msg = tk.Label(
                self.scrollable_frame,
                text="登録されたレジュメやテキストがありません。\n左側のフォームから追加してください。",
                font=("Helvetica", 11),
                fg="#94A3B8",
                bg="#F8FAFC",
                pady=50,
            )
            empty_msg.pack(fill="both", expand=True)

        total_units_all = 0
        total_comp_r1_all = 0
        quick_values = []

        for item in self.subjects:
            has_pages = item.get("hasPages", True)
            page_rounds = item.get("pageRounds", {})
            lecture_rounds = item.get("lectureRounds", {})
            lectures = item.get("lectureRanges", [])
            current_memo = item.get("memo", "")

            quick_values.append(
                f"{item['id']}: {item['subject']} - {item['title']}"
            )

            card = tk.LabelFrame(
                self.scrollable_frame,
                text=f" {item['subject']} ",
                font=("Helvetica", 10, "bold"),
                bg="white",
                padx=10,
                pady=10,
            )
            card.pack(fill="x", expand=True, pady=6, padx=5)

            title_frame = tk.Frame(card, bg="white")
            title_frame.pack(fill="x")

            tk.Label(
                title_frame,
                text=item["title"],
                font=("Helvetica", 11, "bold"),
                bg="white",
            ).pack(side="left")

            del_btn = tk.Button(
                title_frame,
                text="🗑️ 削除",
                command=lambda s_id=item["id"], title=item[
                    "title"
                ]: self.delete_subject(s_id, title),
                fg="#EF4444",
                bg="#FEF2F2",
                activebackground="#FEE2E2",
                bd=0,
                padx=6,
                pady=2,
                font=("Helvetica", 8, "bold"),
            )
            del_btn.pack(side="right")

            # --- 1. ページ数指定がある場合 ---
            if has_pages:
                total_p = item["endPage"] - item["startPage"] + 1
                r1_count = sum(1 for r in page_rounds.values() if r >= 1)
                r2_count = sum(1 for r in page_rounds.values() if r >= 2)
                r3_count = sum(1 for r in page_rounds.values() if r >= 3)

                total_units_all += total_p
                total_comp_r1_all += r1_count

                stats_text = f"全{len(lectures)}回講義 (p.{item['startPage']}〜p.{item['endPage']}) | 1周目: {r1_count}/{total_p}P | 2周目: {r2_count}/{total_p}P | 3周目: {r3_count}/{total_p}P"
                tk.Label(
                    card,
                    text=stats_text,
                    font=("Helvetica", 8),
                    fg="#64748B",
                    bg="white",
                ).pack(anchor="w", pady=(0, 6))

                for l_num, l_start, l_end in lectures:
                    l_total = l_end - l_start + 1
                    l_r1 = sum(
                        1
                        for p in range(l_start, l_end + 1)
                        if page_rounds.get(str(p), 0) >= 1
                    )
                    l_pct = int((l_r1 / l_total) * 100) if l_total > 0 else 0

                    lec_frame = tk.Frame(card, bg="#F1F5F9", padx=6, pady=4)
                    lec_frame.pack(fill="x", pady=3)

                    lec_header = tk.Frame(lec_frame, bg="#F1F5F9")
                    lec_header.pack(fill="x", pady=(0, 2))

                    tk.Label(
                        lec_header,
                        text=f"第{l_num}回講義 (p.{l_start}〜p.{l_end})",
                        font=("Helvetica", 8, "bold"),
                        fg="#334155",
                        bg="#F1F5F9",
                    ).pack(side="left")

                    tk.Label(
                        lec_header,
                        text=f"1周目: {l_r1}/{l_total}P ({l_pct}%)",
                        font=("Helvetica", 8),
                        fg="#059669" if l_pct == 100 else "#64748B",
                        bg="#F1F5F9",
                    ).pack(side="right")

                    grid_frame = tk.Frame(lec_frame, bg="#F1F5F9")
                    grid_frame.pack(fill="x")

                    cols = 15
                    for i, p in enumerate(range(l_start, l_end + 1)):
                        r_level = page_rounds.get(str(p), 0)
                        color_key = min(r_level, 3)
                        bg_color, fg_color = ROUND_COLORS.get(
                            color_key, ROUND_COLORS[0]
                        )

                        btn = tk.Button(
                            grid_frame,
                            text=str(p),
                            width=3,
                            height=1,
                            font=(
                                "Helvetica",
                                7,
                                "bold" if r_level > 0 else "normal",
                            ),
                            bg=bg_color,
                            fg=fg_color,
                            relief="flat",
                            command=lambda s_id=item["id"], page=p: self.toggle_page(
                                s_id, page
                            ),
                        )
                        row = i // cols
                        col = i % cols
                        btn.grid(row=row, column=col, padx=1, pady=1)

            # --- 2. ページ指定無し（回数のみ）の場合 ---
            else:
                lec_cnt = item.get("lecturesCount", 1)
                r1_count = sum(1 for r in lecture_rounds.values() if r >= 1)
                r2_count = sum(1 for r in lecture_rounds.values() if r >= 2)
                r3_count = sum(1 for r in lecture_rounds.values() if r >= 3)

                total_units_all += lec_cnt
                total_comp_r1_all += r1_count

                stats_text = f"全{lec_cnt}回講義（ページ指定なし）| 1周目: {r1_count}/{lec_cnt}回 | 2周目: {r2_count}/{lec_cnt}回 | 3周目: {r3_count}/{lec_cnt}回"
                tk.Label(
                    card,
                    text=stats_text,
                    font=("Helvetica", 8),
                    fg="#64748B",
                    bg="white",
                ).pack(anchor="w", pady=(0, 6))

                grid_frame = tk.Frame(card, bg="#F1F5F9", padx=6, pady=6)
                grid_frame.pack(fill="x")

                cols = 5
                for i in range(lec_cnt):
                    l_num = i + 1
                    r_level = lecture_rounds.get(str(l_num), 0)
                    color_key = min(r_level, 3)
                    bg_color, fg_color = ROUND_COLORS.get(
                        color_key, ROUND_COLORS[0]
                    )

                    btn = tk.Button(
                        grid_frame,
                        text=f"第{l_num}回講義",
                        font=(
                            "Helvetica",
                            9,
                            "bold" if r_level > 0 else "normal",
                        ),
                        bg=bg_color,
                        fg=fg_color,
                        relief="flat",
                        padx=8,
                        pady=6,
                        command=lambda s_id=item["id"], l_idx=l_num: self.toggle_lecture(
                            s_id, l_idx
                        ),
                    )
                    row = i // cols
                    col = i % cols
                    btn.grid(row=row, column=col, padx=3, pady=3, sticky="w")

            # --- 3. 途中の進捗メモ入力エリア（新規追加） ---
            memo_frame = tk.Frame(card, bg="#F8FAFC", padx=6, pady=4, bd=1, relief="groove")
            memo_frame.pack(fill="x", pady=(6, 0))

            tk.Label(
                memo_frame,
                text="📝 途中の進捗メモ:",
                font=("Helvetica", 8, "bold"),
                fg="#475569",
                bg="#F8FAFC",
            ).pack(side="left", padx=(0, 4))

            memo_ent = tk.Entry(memo_frame, font=("Helvetica", 8), bg="white")
            memo_ent.insert(0, current_memo)
            memo_ent.pack(side="left", fill="x", expand=True, padx=4)
            self.memo_entries[item["id"]] = memo_ent

            save_memo_btn = tk.Button(
                memo_frame,
                text="メモ保存",
                font=("Helvetica", 8, "bold"),
                bg="#E2E8F0",
                fg="#334155",
                bd=0,
                padx=6,
                command=lambda s_id=item["id"]: self.save_memo(s_id),
            )
            save_memo_btn.pack(side="right")

        overall_pct = (
            int((total_comp_r1_all / total_units_all) * 100)
            if total_units_all > 0
            else 0
        )
        self.overall_label.config(
            text=f"1周目完了度: {overall_pct}% ({total_comp_r1_all}/{total_units_all})"
        )

        self.quick_select["values"] = quick_values
        if quick_values:
            self.quick_select.current(0)
        else:
            self.quick_select.set("")

        self.save_data()

    def toggle_page(self, subject_id, page_num):
        for s in self.subjects:
            if s["id"] == subject_id:
                if "pageRounds" not in s:
                    s["pageRounds"] = {}

                p_str = str(page_num)
                current_val = s["pageRounds"].get(p_str, 0)

                if current_val >= self.current_round:
                    s["pageRounds"][p_str] = 0
                else:
                    s["pageRounds"][p_str] = self.current_round
                break

        self.render_subjects()

    def toggle_lecture(self, subject_id, lec_num):
        for s in self.subjects:
            if s["id"] == subject_id:
                if "lectureRounds" not in s:
                    s["lectureRounds"] = {}

                l_str = str(lec_num)
                current_val = s["lectureRounds"].get(l_str, 0)

                if current_val >= self.current_round:
                    s["lectureRounds"][l_str] = 0
                else:
                    s["lectureRounds"][l_str] = self.current_round
                break

        self.render_subjects()

    def apply_quick_progress(self):
        sel = self.quick_select.get()
        if not sel:
            return
        s_id = int(sel.split(":")[0])
        try:
            start_p = int(self.quick_start_ent.get())
            end_p = int(self.quick_end_ent.get())
        except ValueError:
            messagebox.showerror(
                "エラー", "開始・終了ページには数値を入力してください。"
            )
            return

        for s in self.subjects:
            if s["id"] == s_id:
                if not s.get("hasPages", True):
                    messagebox.showinfo(
                        "お知らせ",
                        "このテキストはページ指定がないため一括入力できません。",
                    )
                    return
                if "pageRounds" not in s:
                    s["pageRounds"] = {}
                for p in range(start_p, end_p + 1):
                    if s["startPage"] <= p <= s["endPage"]:
                        s["pageRounds"][str(p)] = self.current_round
                break

        self.quick_start_ent.delete(0, tk.END)
        self.quick_end_ent.delete(0, tk.END)
        self.render_subjects()

    def add_subject(self):
        sub = self.sub_ent.get().strip()
        title = self.title_ent.get().strip()
        sp_str = self.start_p_ent.get().strip()
        ep_str = self.end_p_ent.get().strip()
        lec_str = self.lec_ent.get().strip()

        try:
            lec = int(lec_str)
        except ValueError:
            messagebox.showerror("エラー", "講義数には数値を入力してください。")
            return

        if not sub or not title or lec < 1:
            messagebox.showerror(
                "入力不備", "科目名・タイトル・講義数を入力してください。"
            )
            return

        if sp_str == "" and ep_str == "":
            new_item = {
                "id": int(time.time() * 1000),
                "subject": sub,
                "title": title,
                "hasPages": False,
                "lecturesCount": lec,
                "lectureRounds": {},
                "memo": "",
            }
        else:
            try:
                sp = int(sp_str)
                ep = int(ep_str)
            except ValueError:
                messagebox.showerror(
                    "エラー",
                    "開始P・終了Pには数値を入力するか、空欄にしてください。",
                )
                return

            if sp >= ep:
                messagebox.showerror(
                    "入力不備",
                    "終了ページは開始ページより大きい数値を指定してください。",
                )
                return

            dialog = LectureRangeDialog(self, lec, sp, ep)
            self.wait_window(dialog)

            if dialog.result is None:
                return

            new_item = {
                "id": int(time.time() * 1000),
                "subject": sub,
                "title": title,
                "hasPages": True,
                "startPage": sp,
                "endPage": ep,
                "lectureRanges": dialog.result,
                "pageRounds": {},
                "memo": "",
            }

        self.subjects.append(new_item)
        self.sub_ent.delete(0, tk.END)
        self.title_ent.delete(0, tk.END)
        self.start_p_ent.delete(0, tk.END)
        self.end_p_ent.delete(0, tk.END)
        self.render_subjects()

    def delete_subject(self, subject_id, subject_title):
        if messagebox.askyesno(
            "削除の確認", f"「{subject_title}」を削除してもよろしいですか？"
        ):
            self.subjects = [s for s in self.subjects if s["id"] != subject_id]
            self.render_subjects()

    def clear_all_data(self):
        if not self.subjects:
            messagebox.showinfo("お知らせ", "削除するデータがありません。")
            return
        if messagebox.askyesno(
            "全データ削除の確認",
            "すべての登録テキスト・レジュメと記録が消去されます。\n本当に削除しますか？",
        ):
            self.subjects = []
            self.render_subjects()


if __name__ == "__main__":
    app = StudyApp()
    app.mainloop()