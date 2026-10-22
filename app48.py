import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import colorsys
import json


class App48:
    """カラーテーマジェネレーター"""

    HARMONY_MODES = ["補色", "類似色", "三角配色", "四角配色", "分裂補色"]

    def __init__(self, root):
        self.root = root
        self.root.title("カラーテーマジェネレーター")
        self.root.geometry("1100x720")
        self.root.configure(bg="#1e1e1e")

        self._base_hex = "#4fc3f7"
        self._palette = []
        self._swatch_refs = []

        self._build_ui()
        self._generate()

    def _build_ui(self):
        # ヘッダー
        header = tk.Frame(self.root, bg="#252526", pady=6)
        header.pack(fill=tk.X)
        tk.Label(header, text="🎨 カラーテーマジェネレーター",
                 font=("Noto Sans JP", 12, "bold"),
                 bg="#252526", fg="#4fc3f7").pack(side=tk.LEFT, padx=12)

        tk.Label(header, text="ベースカラー:", bg="#252526", fg="#ccc",
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=(16, 4))
        self.color_entry = ttk.Entry(header, width=9)
        self.color_entry.insert(0, self._base_hex)
        self.color_entry.pack(side=tk.LEFT, padx=2)

        self.color_preview_btn = tk.Button(
            header, text="  ", width=3,
            bg=self._base_hex, relief=tk.FLAT, bd=1,
            command=self._pick_color)
        self.color_preview_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(header, text="適用",
                   command=self._apply_entry).pack(side=tk.LEFT, padx=4)

        tk.Label(header, text="配色:", bg="#252526", fg="#ccc",
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=(12, 4))
        self.harmony_var = tk.StringVar(value="補色")
        ttk.Combobox(header, textvariable=self.harmony_var,
                     values=self.HARMONY_MODES, state="readonly",
                     width=10).pack(side=tk.LEFT)
        ttk.Button(header, text="生成",
                   command=self._generate).pack(side=tk.LEFT, padx=4)

        ttk.Button(header, text="CSS コピー",
                   command=self._copy_css).pack(side=tk.RIGHT, padx=4)
        ttk.Button(header, text="JSON コピー",
                   command=self._copy_json).pack(side=tk.RIGHT, padx=2)

        # メインエリア
        main = tk.Frame(self.root, bg="#1e1e1e")
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左パネル
        left = tk.Frame(main, bg="#1e1e1e", width=340)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        # ベースカラー情報
        info_f = tk.LabelFrame(left, text="ベースカラー情報", bg="#252526",
                                fg="#ccc", font=("Arial", 9), padx=6, pady=4)
        info_f.pack(fill=tk.X, pady=(0, 6))
        self.base_canvas = tk.Canvas(info_f, width=60, height=60,
                                      highlightthickness=0)
        self.base_canvas.pack(side=tk.LEFT, padx=4)
        vals_f = tk.Frame(info_f, bg="#252526")
        vals_f.pack(side=tk.LEFT, padx=4)
        self.hex_lbl = tk.Label(vals_f, text="HEX: #------",
                                 bg="#252526", fg="#fff", font=("Courier New", 9))
        self.hex_lbl.pack(anchor="w")
        self.rgb_lbl = tk.Label(vals_f, text="RGB: (0, 0, 0)",
                                 bg="#252526", fg="#ccc", font=("Arial", 9))
        self.rgb_lbl.pack(anchor="w")
        self.hsl_lbl = tk.Label(vals_f, text="HSL: (0°, 0%, 0%)",
                                 bg="#252526", fg="#ccc", font=("Arial", 9))
        self.hsl_lbl.pack(anchor="w")
        self.cmyk_lbl = tk.Label(vals_f, text="CMYK: (0, 0, 0, 0)",
                                  bg="#252526", fg="#ccc", font=("Arial", 9))
        self.cmyk_lbl.pack(anchor="w")

        # ハーモニーカラー
        harm_f = tk.LabelFrame(left, text="ハーモニーカラー", bg="#252526",
                                fg="#ccc", font=("Arial", 9), padx=6, pady=4)
        harm_f.pack(fill=tk.X, pady=(0, 6))
        self.harm_frame = tk.Frame(harm_f, bg="#252526")
        self.harm_frame.pack(fill=tk.X)

        # シェード & ティント
        shade_f = tk.LabelFrame(left, text="シェード & ティント", bg="#252526",
                                  fg="#ccc", font=("Arial", 9), padx=6, pady=4)
        shade_f.pack(fill=tk.X, pady=(0, 6))
        self.shade_frame = tk.Frame(shade_f, bg="#252526")
        self.shade_frame.pack(fill=tk.X)

        # セマンティックカラー
        sem_f = tk.LabelFrame(left, text="UI セマンティックカラー", bg="#252526",
                               fg="#ccc", font=("Arial", 9), padx=6, pady=4)
        sem_f.pack(fill=tk.X, pady=(0, 6))
        self.sem_frame = tk.Frame(sem_f, bg="#252526")
        self.sem_frame.pack(fill=tk.X)

        # 右: UIプレビュー
        right = tk.Frame(main, bg="#1e1e1e")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        tk.Label(right, text="UI プレビュー", bg="#1e1e1e",
                 fg="#888", font=("Arial", 9)).pack(anchor="w")
        self.preview_frame = tk.Frame(right, bg="#ffffff",
                                       relief=tk.SOLID, bd=1)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        self._build_preview(self.preview_frame)

        # CSS出力
        out_f = tk.LabelFrame(self.root, text="CSS / JSON 出力",
                               bg="#1e1e1e", fg="#888", font=("Arial", 9),
                               padx=4, pady=4)
        out_f.pack(fill=tk.X, padx=8, pady=(0, 4))
        self.output_text = tk.Text(out_f, height=5, bg="#0d1117", fg="#8b949e",
                                    font=("Courier New", 8), relief=tk.FLAT,
                                    wrap=tk.NONE)
        xsb = ttk.Scrollbar(out_f, orient=tk.HORIZONTAL,
                             command=self.output_text.xview)
        self.output_text.configure(xscrollcommand=xsb.set)
        self.output_text.pack(fill=tk.X)
        xsb.pack(fill=tk.X)

    def _build_preview(self, parent):
        # ナビゲーションバー
        self.prev_navbar = tk.Frame(parent, pady=8)
        self.prev_navbar.pack(fill=tk.X)
        self.prev_title = tk.Label(self.prev_navbar, text="My Application",
                                    font=("Arial", 12, "bold"))
        self.prev_title.pack(side=tk.LEFT, padx=12)
        self.prev_nav_btn1 = tk.Button(self.prev_navbar, text="Home",
                                        relief=tk.FLAT, padx=10)
        self.prev_nav_btn1.pack(side=tk.LEFT, padx=2)
        self.prev_nav_btn2 = tk.Button(self.prev_navbar, text="About",
                                        relief=tk.FLAT, padx=10)
        self.prev_nav_btn2.pack(side=tk.LEFT, padx=2)

        # コンテンツ
        content = tk.Frame(parent)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self._prev_content = content

        # ヒーロー
        self.prev_hero = tk.Frame(content, pady=16)
        self.prev_hero.pack(fill=tk.X, pady=(0, 8))
        self.prev_hero_title = tk.Label(self.prev_hero,
                                         text="Welcome to the App",
                                         font=("Arial", 16, "bold"))
        self.prev_hero_title.pack()
        self.prev_hero_sub = tk.Label(self.prev_hero,
                                       text="Build beautiful UIs with generated color themes.",
                                       font=("Arial", 10))
        self.prev_hero_sub.pack()
        btn_row = tk.Frame(self.prev_hero)
        btn_row.pack(pady=6)
        self._prev_hero_btn_row = btn_row
        self.prev_btn_primary = tk.Button(btn_row, text="Get Started",
                                           font=("Arial", 10, "bold"),
                                           relief=tk.FLAT, padx=14, pady=5)
        self.prev_btn_primary.pack(side=tk.LEFT, padx=4)
        self.prev_btn_secondary = tk.Button(btn_row, text="Learn More",
                                             font=("Arial", 10),
                                             relief=tk.FLAT, padx=14, pady=5)
        self.prev_btn_secondary.pack(side=tk.LEFT, padx=4)

        # カード
        cards = tk.Frame(content)
        cards.pack(fill=tk.X, pady=4)
        self._prev_cards_row = cards
        self.prev_cards = []
        titles = ["Feature One", "Feature Two", "Feature Three"]
        descs = ["Vivid palettes with one click.",
                 "Harmony-based color science.",
                 "Export CSS in seconds."]
        for i, (t, d) in enumerate(zip(titles, descs)):
            card = tk.Frame(cards, relief=tk.SOLID, bd=1, padx=10, pady=8)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            cards.columnconfigure(i, weight=1)
            tl = tk.Label(card, text=t, font=("Arial", 10, "bold"))
            tl.pack(anchor="w")
            dl = tk.Label(card, text=d, font=("Arial", 9), wraplength=150)
            dl.pack(anchor="w")
            self.prev_cards.append((card, tl, dl))

        # アラート
        alert_row = tk.Frame(content)
        alert_row.pack(fill=tk.X, pady=4)
        self._prev_alert_row = alert_row
        self.prev_alert_success = tk.Label(
            alert_row, text="✔ Success message here",
            font=("Arial", 9), padx=8, pady=3, anchor="w")
        self.prev_alert_success.pack(fill=tk.X, pady=1)
        self.prev_alert_warn = tk.Label(
            alert_row, text="⚠ Warning message here",
            font=("Arial", 9), padx=8, pady=3, anchor="w")
        self.prev_alert_warn.pack(fill=tk.X, pady=1)
        self.prev_alert_error = tk.Label(
            alert_row, text="✖ Error message here",
            font=("Arial", 9), padx=8, pady=3, anchor="w")
        self.prev_alert_error.pack(fill=tk.X, pady=1)

        # フッター
        self.prev_footer = tk.Frame(parent, pady=5)
        self.prev_footer.pack(fill=tk.X)
        self.prev_footer_lbl = tk.Label(self.prev_footer,
                                         text="© 2025 My App  |  Privacy  |  Terms",
                                         font=("Arial", 8))
        self.prev_footer_lbl.pack()

    # ── カラーユーティリティ ──────────────────────────────────────

    @staticmethod
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _rgb_to_hex(r, g, b):
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    @staticmethod
    def _rgb_to_hsl(r, g, b):
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        return h * 360, s * 100, l * 100

    @staticmethod
    def _hsl_to_rgb(h, s, l):
        r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
        return int(r*255), int(g*255), int(b*255)

    @staticmethod
    def _rgb_to_cmyk(r, g, b):
        if r == g == b == 0:
            return 0, 0, 0, 100
        r_, g_, b_ = r/255, g/255, b/255
        k = 1 - max(r_, g_, b_)
        if 1 - k == 0:
            return 0, 0, 0, round(k*100)
        c = (1 - r_ - k) / (1 - k)
        m = (1 - g_ - k) / (1 - k)
        y = (1 - b_ - k) / (1 - k)
        return round(c*100), round(m*100), round(y*100), round(k*100)

    def _contrast_color(self, hex_color):
        try:
            r, g, b = self._hex_to_rgb(hex_color)
        except Exception:
            return "#000000"
        luminance = (0.299*r + 0.587*g + 0.114*b) / 255
        return "#000000" if luminance > 0.5 else "#ffffff"

    def _rotate_hue(self, hex_color, degrees):
        r, g, b = self._hex_to_rgb(hex_color)
        h, s, l = self._rgb_to_hsl(r, g, b)
        h2 = (h + degrees) % 360
        return self._rgb_to_hex(*self._hsl_to_rgb(h2, s, l))

    def _adjust_lightness(self, hex_color, delta_l):
        r, g, b = self._hex_to_rgb(hex_color)
        h, s, l = self._rgb_to_hsl(r, g, b)
        l2 = max(0, min(100, l + delta_l))
        return self._rgb_to_hex(*self._hsl_to_rgb(h, s, l2))

    def _harmony_colors(self, base_hex, mode):
        if mode == "補色":
            return [base_hex, self._rotate_hue(base_hex, 180)]
        elif mode == "類似色":
            return [self._rotate_hue(base_hex, -30), base_hex,
                    self._rotate_hue(base_hex, 30)]
        elif mode == "三角配色":
            return [base_hex, self._rotate_hue(base_hex, 120),
                    self._rotate_hue(base_hex, 240)]
        elif mode == "四角配色":
            return [base_hex, self._rotate_hue(base_hex, 90),
                    self._rotate_hue(base_hex, 180),
                    self._rotate_hue(base_hex, 270)]
        elif mode == "分裂補色":
            return [base_hex, self._rotate_hue(base_hex, 150),
                    self._rotate_hue(base_hex, 210)]
        return [base_hex]

    def _semantic_colors(self, base_hex):
        r, g, b = self._hex_to_rgb(base_hex)
        h, s, l = self._rgb_to_hsl(r, g, b)
        return {
            "Primary":       base_hex,
            "Primary Dark":  self._adjust_lightness(base_hex, -15),
            "Primary Light": self._adjust_lightness(base_hex, 20),
            "Success":       self._rgb_to_hex(*self._hsl_to_rgb(120, max(40, s), 40)),
            "Warning":       self._rgb_to_hex(*self._hsl_to_rgb(38, max(60, s), 50)),
            "Error":         self._rgb_to_hex(*self._hsl_to_rgb(0, max(60, s), 45)),
            "Info":          self._rgb_to_hex(*self._hsl_to_rgb(210, max(40, s), 50)),
            "Background":    self._rgb_to_hex(*self._hsl_to_rgb(h, min(s, 15), 97)),
            "Surface":       "#ffffff",
            "Text":          self._rgb_to_hex(*self._hsl_to_rgb(h, min(s, 15), 15)),
            "Muted":         self._rgb_to_hex(*self._hsl_to_rgb(h, min(s, 10), 55)),
        }

    # ── 生成・更新 ────────────────────────────────────────────────

    def _generate(self):
        base = self._base_hex
        mode = self.harmony_var.get()

        r, g, b = self._hex_to_rgb(base)
        h, s, l = self._rgb_to_hsl(r, g, b)
        c, m, y, k = self._rgb_to_cmyk(r, g, b)

        self.base_canvas.config(bg=base)
        self.base_canvas.delete("all")
        self.hex_lbl.config(text=f"HEX: {base.upper()}", fg=base)
        self.rgb_lbl.config(text=f"RGB: ({r}, {g}, {b})")
        self.hsl_lbl.config(text=f"HSL: ({h:.0f}°, {s:.0f}%, {l:.0f}%)")
        self.cmyk_lbl.config(text=f"CMYK: ({c}, {m}, {y}, {k})")

        # ハーモニーカラー
        harmony = self._harmony_colors(base, mode)
        for w in self.harm_frame.winfo_children():
            w.destroy()
        for i, hc in enumerate(harmony):
            self._make_swatch(self.harm_frame, hc)

        # シェード & ティント
        for w in self.shade_frame.winfo_children():
            w.destroy()
        shades = ([self._adjust_lightness(base, -(s_))
                   for s_ in [30, 20, 10]]
                  + [base]
                  + [self._adjust_lightness(base, t_)
                     for t_ in [10, 20, 30]])
        for sc in shades:
            self._make_swatch(self.shade_frame, sc, size=28)

        # セマンティックカラー
        for w in self.sem_frame.winfo_children():
            w.destroy()
        sem = self._semantic_colors(base)
        row = col = 0
        for name, color in sem.items():
            f = tk.Frame(self.sem_frame, bg="#252526")
            f.grid(row=row, column=col, padx=2, pady=1, sticky="w")
            cv = tk.Canvas(f, width=16, height=16, bg=color,
                            highlightthickness=1,
                            highlightbackground="#555")
            cv.pack(side=tk.LEFT)
            tk.Label(f, text=name, bg="#252526", fg="#ccc",
                     font=("Arial", 7)).pack(side=tk.LEFT, padx=2)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        self._palette = list(harmony) + shades
        self._update_preview(base, sem)
        self._update_output(sem, harmony)

    def _make_swatch(self, parent, color, size=40):
        cv = tk.Canvas(parent, width=size, height=size, bg=color,
                        highlightthickness=1,
                        highlightbackground="#555",
                        cursor="hand2")
        cv.pack(side=tk.LEFT, padx=2, pady=2)
        fg = self._contrast_color(color)
        if size >= 36:
            cv.create_text(size//2, size//2,
                            text=color.upper()[1:],
                            fill=fg, font=("Arial", 6))
        cv.bind("<Button-1>", lambda e, c=color: self._on_swatch_click(c))

    def _on_swatch_click(self, color):
        self._base_hex = color
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, color)
        self.color_preview_btn.config(bg=color)
        self._generate()

    def _update_preview(self, base, sem):
        bg        = sem["Background"]
        surface   = sem["Surface"]
        text_c    = sem["Text"]
        muted     = sem["Muted"]
        primary   = sem["Primary"]
        p_dark    = sem["Primary Dark"]
        p_light   = sem["Primary Light"]
        success   = sem["Success"]
        warning   = sem["Warning"]
        error     = sem["Error"]

        p_fg      = self._contrast_color(primary)
        pd_fg     = self._contrast_color(p_dark)
        pl_fg     = self._contrast_color(p_light)
        footer_bg = self._adjust_lightness(base, -30)

        self.preview_frame.config(bg=bg)

        self.prev_navbar.config(bg=primary)
        self.prev_title.config(bg=primary, fg=p_fg)
        self.prev_nav_btn1.config(bg=p_dark, fg=pd_fg,
                                   activebackground=p_dark, activeforeground=pd_fg)
        self.prev_nav_btn2.config(bg=p_dark, fg=pd_fg,
                                   activebackground=p_dark, activeforeground=pd_fg)

        self.prev_hero.config(bg=p_light)
        self.prev_hero_title.config(bg=p_light, fg=pl_fg)
        self.prev_hero_sub.config(bg=p_light, fg=pl_fg)
        self._prev_hero_btn_row.config(bg=p_light)

        self.prev_btn_primary.config(bg=primary, fg=p_fg,
                                      activebackground=p_dark,
                                      activeforeground=pd_fg)
        self.prev_btn_secondary.config(bg=surface, fg=primary,
                                        activebackground=surface,
                                        activeforeground=p_dark)

        self._prev_cards_row.config(bg=bg)
        for card, tl, dl in self.prev_cards:
            card.config(bg=surface)
            tl.config(bg=surface, fg=text_c)
            dl.config(bg=surface, fg=muted)

        self._prev_content.config(bg=bg)
        self._prev_alert_row.config(bg=bg)
        self.prev_alert_success.config(
            bg=self._adjust_lightness(success, 35),
            fg=self._adjust_lightness(success, -20))
        self.prev_alert_warn.config(
            bg=self._adjust_lightness(warning, 35),
            fg=self._adjust_lightness(warning, -20))
        self.prev_alert_error.config(
            bg=self._adjust_lightness(error, 35),
            fg=self._adjust_lightness(error, -20))

        self.prev_footer.config(bg=footer_bg)
        self.prev_footer_lbl.config(bg=footer_bg,
                                     fg=self._contrast_color(footer_bg))

    def _update_output(self, sem, harmony):
        css = ":root {\n"
        for name, color in sem.items():
            var_name = "--color-" + name.lower().replace(" ", "-")
            css += f"  {var_name}: {color};\n"
        for i, hc in enumerate(harmony):
            css += f"  --harmony-{i+1}: {hc};\n"
        css += "}"
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, css)

    def _pick_color(self):
        result = colorchooser.askcolor(color=self._base_hex,
                                        title="ベースカラーを選択")
        if result and result[1]:
            self._base_hex = result[1]
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, self._base_hex)
            self.color_preview_btn.config(bg=self._base_hex)
            self._generate()

    def _apply_entry(self):
        val = self.color_entry.get().strip()
        if not val.startswith("#"):
            val = "#" + val
        if len(val) not in (4, 7):
            messagebox.showerror("エラー", "正しいHEXカラーを入力してください (#RRGGBB)")
            return
        try:
            self._hex_to_rgb(val)
        except Exception:
            messagebox.showerror("エラー", "HEXカラーの形式が正しくありません")
            return
        self._base_hex = val.lower()
        self.color_preview_btn.config(bg=self._base_hex)
        self._generate()

    def _copy_css(self):
        css = self.output_text.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(css)
        messagebox.showinfo("コピー完了", "CSS をクリップボードにコピーしました")

    def _copy_json(self):
        sem = self._semantic_colors(self._base_hex)
        harmony = self._harmony_colors(self._base_hex, self.harmony_var.get())
        data = {
            "base": self._base_hex,
            "harmony_mode": self.harmony_var.get(),
            "semantic": sem,
            "harmony": harmony,
        }
        self.root.clipboard_clear()
        self.root.clipboard_append(
            json.dumps(data, ensure_ascii=False, indent=2))
        messagebox.showinfo("コピー完了", "JSON をクリップボードにコピーしました")


if __name__ == "__main__":
    root = tk.Tk()
    app = App48(root)
    root.mainloop()
