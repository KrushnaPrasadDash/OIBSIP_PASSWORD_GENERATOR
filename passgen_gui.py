import tkinter as tk
from tkinter import ttk, messagebox

from passgen_core import generate_password, score_password


STRENGTH_COLORS = {
    "weak": "#e74c3c",
    "fair": "#e67e22",
    "good": "#f1c40f",
    "strong": "#2ecc71",
    "empty": "#888888",
}


class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")
        self.geometry("520x580")
        self.minsize(480, 520)
        self.configure(bg="#1a1a2e")

        self._build_ui()
        self._generate()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#eaeaea", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#ffffff")
        style.configure("TCheckbutton", background="#1a1a2e", foreground="#eaeaea", font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[("active", "#1a1a2e")])
        style.configure("TScale", background="#1a1a2e")
        style.configure("Gen.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        style.configure("Copy.TButton", font=("Segoe UI", 10), padding=6)

        outer = ttk.Frame(self, padding=24)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Password Generator", style="Header.TLabel").pack(anchor="w")
        ttk.Label(outer, text="tweak the options and hit generate").pack(anchor="w", pady=(0, 18))

        display_frame = tk.Frame(outer, bg="#16213e", highlightbackground="#0f3460", highlightthickness=1)
        display_frame.pack(fill="x", pady=(0, 16))

        self.password_var = tk.StringVar(value="")
        self.entry = tk.Entry(
            display_frame,
            textvariable=self.password_var,
            font=("Consolas", 14),
            bg="#16213e",
            fg="#e94560",
            insertbackground="#e94560",
            relief="flat",
            justify="center",
        )
        self.entry.pack(fill="x", ipady=14, padx=12, pady=12)

        strength_row = ttk.Frame(outer)
        strength_row.pack(fill="x", pady=(0, 20))

        ttk.Label(strength_row, text="strength").pack(side="left")
        self.strength_label = ttk.Label(strength_row, text="—", font=("Segoe UI", 10, "bold"))
        self.strength_label.pack(side="right")

        self.strength_bar = tk.Canvas(outer, height=6, bg="#16213e", highlightthickness=0)
        self.strength_bar.pack(fill="x", pady=(0, 22))
        self._bar_fill = self.strength_bar.create_rectangle(0, 0, 0, 6, fill="#888888", outline="")

        opts = ttk.LabelFrame(outer, text="  length  ", padding=14)
        opts.pack(fill="x", pady=(0, 14))

        len_row = ttk.Frame(opts)
        len_row.pack(fill="x")

        self.length_var = tk.IntVar(value=16)
        self.length_display = ttk.Label(len_row, text="16", font=("Consolas", 12, "bold"))
        self.length_display.pack(side="right")

        scale = ttk.Scale(
            len_row,
            from_=8,
            to=64,
            orient="horizontal",
            variable=self.length_var,
            command=self._on_length_change,
        )
        scale.pack(side="left", fill="x", expand=True, padx=(0, 12))

        types = ttk.LabelFrame(outer, text="  character types  ", padding=14)
        types.pack(fill="x", pady=(0, 14))

        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=True)
        self.var_digits = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=False)

        grid = ttk.Frame(types)
        grid.pack(fill="x")
        ttk.Checkbutton(grid, text="lowercase (a-z)", variable=self.var_lower).grid(row=0, column=0, sticky="w", padx=(0, 20))
        ttk.Checkbutton(grid, text="uppercase (A-Z)", variable=self.var_upper).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(grid, text="numbers (0-9)", variable=self.var_digits).grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Checkbutton(grid, text="symbols (!@#...)", variable=self.var_symbols).grid(row=1, column=1, sticky="w", pady=(8, 0))

        rules = ttk.LabelFrame(outer, text="  security rules  ", padding=14)
        rules.pack(fill="x", pady=(0, 20))

        self.var_ambiguous = tk.BooleanVar(value=True)
        self.var_require = tk.BooleanVar(value=True)
        self.var_no_repeat = tk.BooleanVar(value=False)

        ttk.Checkbutton(rules, text="exclude ambiguous characters (0, O, l, 1...)", variable=self.var_ambiguous).pack(anchor="w")
        ttk.Checkbutton(rules, text="require at least one from each enabled type", variable=self.var_require).pack(anchor="w", pady=(6, 0))
        ttk.Checkbutton(rules, text="no adjacent duplicate characters", variable=self.var_no_repeat).pack(anchor="w", pady=(6, 0))

        btn_row = ttk.Frame(outer)
        btn_row.pack(fill="x")

        gen_btn = ttk.Button(btn_row, text="Generate", style="Gen.TButton", command=self._generate)
        gen_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        copy_btn = ttk.Button(btn_row, text="Copy", style="Copy.TButton", command=self._copy)
        copy_btn.pack(side="left", fill="x", expand=True)

        self.bind("<Control-g>", lambda e: self._generate())
        self.bind("<Control-c>", lambda e: self._copy())

    def _on_length_change(self, _val):
        self.length_display.config(text=str(int(float(self.length_var.get()))))

    def _get_options(self):
        return {
            "use_lower": self.var_lower.get(),
            "use_upper": self.var_upper.get(),
            "use_digits": self.var_digits.get(),
            "use_symbols": self.var_symbols.get(),
            "exclude_ambiguous": self.var_ambiguous.get(),
            "require_each_type": self.var_require.get(),
            "no_adjacent_repeat": self.var_no_repeat.get(),
        }

    def _update_strength(self, password, opts):
        score, label = score_password(
            password,
            opts["use_lower"],
            opts["use_upper"],
            opts["use_digits"],
            opts["use_symbols"],
        )
        color = STRENGTH_COLORS.get(label, "#888888")
        self.strength_label.config(text=label.capitalize(), foreground=color)

        width = self.strength_bar.winfo_width()
        if width < 2:
            width = 400
        fill_w = int((score / 100) * width)
        self.strength_bar.coords(self._bar_fill, 0, 0, fill_w, 6)
        self.strength_bar.itemconfig(self._bar_fill, fill=color)

    def _generate(self):
        opts = self._get_options()
        if not any([opts["use_lower"], opts["use_upper"], opts["use_digits"], opts["use_symbols"]]):
            messagebox.showwarning("hold on", "enable at least one character type")
            return

        length = int(self.length_var.get())
        try:
            pwd = generate_password(length, **opts)
        except ValueError as e:
            messagebox.showerror("can't generate", str(e))
            return

        self.password_var.set(pwd)
        self._update_strength(pwd, opts)

    def _copy(self):
        pwd = self.password_var.get()
        if not pwd:
            return
        self.clipboard_clear()
        self.clipboard_append(pwd)
        self.update()
        old = self.title()
        self.title("copied!")
        self.after(1200, lambda: self.title(old))


def main():
    app = PasswordApp()
    app.mainloop()


if __name__ == "__main__":
    main()
