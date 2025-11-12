import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from collections import Counter

getcontext().prec = 30
getcontext().rounding = ROUND_HALF_EVEN


class ArithmeticCodingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Арифметическое кодирование (Python версия)")
        self.root.geometry("950x600")

        # === Верхняя панель ===
        frame_top = tk.Frame(root)
        frame_top.pack(fill="x", pady=4)

        tk.Button(frame_top, text="Открыть файл", command=self.open_file, width=14).pack(side="left", padx=6)
        tk.Button(frame_top, text="Кодировать", command=self.encode, width=14, bg="#4CAF50", fg="white").pack(side="left", padx=6)
        tk.Button(frame_top, text="Декодировать", command=self.decode, width=14, bg="#2196F3", fg="white").pack(side="left", padx=6)

        # === Поле ввода ===
        tk.Label(root, text="Исходный текст:", anchor="w").pack(fill="x", padx=8)
        self.text_input = tk.Text(root, height=4, wrap="word")
        self.text_input.pack(fill="x", padx=8, pady=2)

        # === Код ===
        frame_code = tk.Frame(root)
        frame_code.pack(fill="x", padx=8, pady=4)
        tk.Label(frame_code, text="Код:").pack(side="left")
        self.entry_code = tk.Entry(frame_code, width=40)
        self.entry_code.pack(side="left", padx=6)
        tk.Label(frame_code, text="Декодированный текст:").pack(side="left", padx=(20, 0))
        self.entry_decoded = tk.Entry(frame_code, width=40)
        self.entry_decoded.pack(side="left", padx=6)

        # === Таблицы ===
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=8, pady=4)

        # таблица шагов
        self.tree_steps = ttk.Treeview(nb, columns=("step", "chain", "interval"), show="headings")
        self.tree_steps.heading("step", text="Шаг")
        self.tree_steps.heading("chain", text="Цепочка")
        self.tree_steps.heading("interval", text="Интервал [L;H)")
        nb.add(self.tree_steps, text="Шаги кодирования")

        # таблица вероятностей
        self.tree_freq = ttk.Treeview(nb, columns=("char", "prob", "low", "high"), show="headings")
        self.tree_freq.heading("char", text="Символ")
        self.tree_freq.heading("prob", text="Вероятность")
        self.tree_freq.heading("low", text="Нижняя граница")
        self.tree_freq.heading("high", text="Верхняя граница")
        nb.add(self.tree_freq, text="Таблица вероятностей")

        self.freq = None
        self.low = None
        self.high = None
        self.symbols = None
        self.code = None

    # === Открыть файл ===
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(tk.END, f.read())

    # === Подсчет вероятностей и интервалов ===
    def compute_freq(self, text):
        freq = Counter(text)
        total = Decimal(len(text))
        probs = {c: Decimal(freq[c]) / total for c in freq}
        # сортировка как в C# — по вероятности (убывание), затем по символу (возрастание)
        symbols = sorted(probs.keys(), key=lambda c: (-probs[c], c))
        low, high = {}, {}
        cumulative = Decimal(0)
        for c in symbols:
            low[c] = cumulative
            cumulative += probs[c]
            high[c] = cumulative
        return probs, low, high, symbols

    # === Кодирование ===
    def encode(self):
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Ошибка", "Введите или выберите текст для кодирования!")
            return

        self.freq, self.low, self.high, self.symbols = self.compute_freq(text)

        L, H = Decimal(0), Decimal(1)
        self.tree_steps.delete(*self.tree_steps.get_children())

        for i, symbol in enumerate(text):
            range_ = H - L
            H = L + range_ * self.high[symbol]
            L = L + range_ * self.low[symbol]
            chain = text[:i + 1]
            self.tree_steps.insert("", "end", values=(i + 1, chain, f"[{L:.28f}; {H:.28f})"))

        code = (L + H) / 2
        self.code = code
        self.entry_code.delete(0, tk.END)
        self.entry_code.insert(0, str(code))

        # таблица вероятностей
        self.tree_freq.delete(*self.tree_freq.get_children())
        for c in self.symbols:
            self.tree_freq.insert(
                "", "end",
                values=(c,
                        f"{self.freq[c]:.4f}",
                        f"{self.low[c]:.4f}",
                        f"{self.high[c]:.4f}")
            )

    # === Декодирование ===
    def decode(self):
        code_str = self.entry_code.get().replace(",", ".")
        try:
            code = Decimal(code_str)
        except Exception:
            messagebox.showerror("Ошибка", "Введите корректное число для декодирования!")
            return

        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Ошибка", "Для декодирования нужен исходный текст (для частот)!")
            return

        if not self.freq:
            self.freq, self.low, self.high, self.symbols = self.compute_freq(text)

        decoded = ""
        for _ in range(len(text)):
            for s in self.symbols:
                if self.low[s] <= code < self.high[s]:
                    decoded += s
                    code = (code - self.low[s]) / (self.high[s] - self.low[s])
                    break

        self.entry_decoded.delete(0, tk.END)
        self.entry_decoded.insert(0, decoded)


if __name__ == "__main__":
    root = tk.Tk()
    app = ArithmeticCodingApp(root)
    root.mainloop()
