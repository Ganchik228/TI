import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

# -----------------------
# Арифметическое кодирование
# -----------------------
def arithmetic_encode(text, probs):
    low = 0.0
    high = 1.0
    steps = []
    symbols = sorted(probs.keys())
    
    # Префикс суммы вероятностей
    cum_probs = {symbols[0]: 0.0}
    for i in range(1, len(symbols)):
        cum_probs[symbols[i]] = cum_probs[symbols[i-1]] + probs[symbols[i-1]]
    
    for ch in text:
        range_width = high - low
        ch_low = low + range_width * cum_probs[ch]
        ch_high = ch_low + range_width * probs[ch]
        steps.append((ch, low, high, ch_low, ch_high))
        low, high = ch_low, ch_high
    
    code = (low + high) / 2  # Любая точка интервала
    return code, steps

# -----------------------
# Арифметическое декодирование
# -----------------------
def arithmetic_decode(code, length, probs):
    symbols = sorted(probs.keys())
    cum_probs = {symbols[0]: 0.0}
    for i in range(1, len(symbols)):
        cum_probs[symbols[i]] = cum_probs[symbols[i-1]] + probs[symbols[i-1]]
    
    low = 0.0
    high = 1.0
    result = ''
    steps = []
    
    for _ in range(length):
        range_width = high - low
        # Найти символ, чей интервал содержит код
        for ch in symbols:
            ch_low = low + range_width * cum_probs[ch]
            ch_high = ch_low + range_width * probs[ch]
            if ch_low <= code < ch_high:
                result += ch
                steps.append((ch, low, high, ch_low, ch_high))
                low, high = ch_low, ch_high
                break
    return result, steps

# -----------------------
# GUI
# -----------------------
class ArithmeticApp:
    def __init__(self, root):
        root.title("Арифметическое кодирование")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.encode_frame = ttk.Frame(self.notebook, padding=10)
        self.decode_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.encode_frame, text='Кодирование')
        self.notebook.add(self.decode_frame, text='Декодирование')

        # ------------------- Кодирование -------------------
        ttk.Label(self.encode_frame, text="Текст для кодирования:").grid(column=0, row=0, sticky='w')
        self.input_text = tk.Text(self.encode_frame, width=50, height=5)
        self.input_text.grid(column=0, row=1, columnspan=3, pady=5)

        ttk.Label(self.encode_frame, text="Вероятности символов (например: a:0.2,b:0.3,c:0.5):").grid(column=0, row=2, sticky='w')
        self.prob_entry = ttk.Entry(self.encode_frame, width=50)
        self.prob_entry.grid(column=0, row=3, columnspan=3, pady=5)

        ttk.Button(self.encode_frame, text="Кодировать", command=self.encode).grid(column=0, row=4, pady=5)
        ttk.Button(self.encode_frame, text="Очистить", command=self.clear_encode).grid(column=1, row=4, pady=5)

        self.encode_tree = ttk.Treeview(self.encode_frame)
        self.encode_tree.grid(column=0, row=5, columnspan=3, sticky='nsew', pady=5)
        self.encode_tree['columns'] = ('low','high','new_low','new_high')
        self.encode_tree.heading('#0', text='Символ')
        self.encode_tree.heading('low', text='low')
        self.encode_tree.heading('high', text='high')
        self.encode_tree.heading('new_low', text='new_low')
        self.encode_tree.heading('new_high', text='new_high')

        self.code_label = ttk.Label(self.encode_frame, text="Код: ")
        self.code_label.grid(column=0, row=6, columnspan=3, sticky='w')

        # ------------------- Декодирование -------------------
        ttk.Label(self.decode_frame, text="Код (дробь):").grid(column=0, row=0, sticky='w')
        self.code_entry = ttk.Entry(self.decode_frame, width=30)
        self.code_entry.grid(column=1, row=0, pady=5)

        ttk.Label(self.decode_frame, text="Длина исходного текста:").grid(column=0, row=1, sticky='w')
        self.length_entry = ttk.Entry(self.decode_frame, width=10)
        self.length_entry.grid(column=1, row=1, pady=5)

        ttk.Label(self.decode_frame, text="Вероятности символов (a:0.2,b:0.3,...):").grid(column=0, row=2, sticky='w')
        self.decode_prob_entry = ttk.Entry(self.decode_frame, width=50)
        self.decode_prob_entry.grid(column=0, row=3, columnspan=3, pady=5)

        ttk.Button(self.decode_frame, text="Декодировать", command=self.decode).grid(column=0, row=4, pady=5)
        ttk.Button(self.decode_frame, text="Очистить", command=self.clear_decode).grid(column=1, row=4, pady=5)

        self.decode_tree = ttk.Treeview(self.decode_frame)
        self.decode_tree.grid(column=0, row=5, columnspan=3, sticky='nsew', pady=5)
        self.decode_tree['columns'] = ('low','high','new_low','new_high')
        self.decode_tree.heading('#0', text='Символ')
        self.decode_tree.heading('low', text='low')
        self.decode_tree.heading('high', text='high')
        self.decode_tree.heading('new_low', text='new_low')
        self.decode_tree.heading('new_high', text='new_high')

        self.decoded_label = ttk.Label(self.decode_frame, text="Восстановленный текст: ")
        self.decoded_label.grid(column=0, row=6, columnspan=3, sticky='w')

    # ------------------- Методы -------------------
    def parse_probs(self, text):
        try:
            parts = text.split(',')
            probs = {}
            for p in parts:
                k,v = p.split(':')
                probs[k.strip()] = float(v.strip())
            if abs(sum(probs.values()) - 1.0) > 1e-6:
                messagebox.showwarning("Предупреждение","Сумма вероятностей ≠ 1, будет нормализована")
                total = sum(probs.values())
                for k in probs:
                    probs[k] /= total
            return probs
        except:
            messagebox.showerror("Ошибка","Неверный формат вероятностей")
            return None

    def encode(self):
        self.encode_tree.delete(*self.encode_tree.get_children())
        text = self.input_text.get("1.0", "end").strip()
        probs = self.parse_probs(self.prob_entry.get())
        if not text or not probs:
            return
        code, steps = arithmetic_encode(text, probs)
        for s in steps:
            self.encode_tree.insert('', 'end', text=s[0], values=tuple(f"{v:.6f}" for v in s[1:]))
        self.code_label.config(text=f"Код: {code:.10f}")

    def decode(self):
        self.decode_tree.delete(*self.decode_tree.get_children())
        try:
            code = float(self.code_entry.get())
            length = int(self.length_entry.get())
        except:
            messagebox.showerror("Ошибка","Некорректный код или длина текста")
            return
        probs = self.parse_probs(self.decode_prob_entry.get())
        if not probs:
            return
        result, steps = arithmetic_decode(code, length, probs)
        for s in steps:
            self.decode_tree.insert('', 'end', text=s[0], values=tuple(f"{v:.6f}" for v in s[1:]))
        self.decoded_label.config(text=f"Восстановленный текст: {result}")

    def clear_encode(self):
        self.input_text.delete("1.0","end")
        self.prob_entry.delete(0,'end')
        self.encode_tree.delete(*self.encode_tree.get_children())
        self.code_label.config(text="Код: ")

    def clear_decode(self):
        self.code_entry.delete(0,'end')
        self.length_entry.delete(0,'end')
        self.decode_prob_entry.delete(0,'end')
        self.decode_tree.delete(*self.decode_tree.get_children())
        self.decoded_label.config(text="Восстановленный текст: ")

# -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ArithmeticApp(root)
    root.mainloop()
