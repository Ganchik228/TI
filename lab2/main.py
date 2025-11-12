import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import math
from typing import Dict, List, Tuple, Optional
from copy import deepcopy
import heapq
import itertools


class Node:
    def __init__(self, symbol: Optional[str] = None, frequency: float = 0.0):
        self.symbol = symbol
        self.frequency = frequency
        self.left: Optional["Node"] = None
        self.right: Optional["Node"] = None

    def is_leaf(self):
        return self.left is None and self.right is None


class TextCompression:
    def __init__(self):
        self.frequencies: Dict[str, int] = {}
        # nodes for sorted list of dicts: {'symbol', 'probability', 'code'}
        self.nodes: List[Dict] = []
        self.fano_codes_map: Dict[str, str] = {}
        self.huffman_codes_map: Dict[str, str] = {}

    def calculate_frequencies(self, text: str):
        self.frequencies.clear()
        for ch in text:
            self.frequencies[ch] = self.frequencies.get(ch, 0) + 1

        text_length = len(text)
        self.nodes = []
        if text_length == 0:
            return

        for symbol, freq in self.frequencies.items():
            self.nodes.append({
                'symbol': symbol,
                'probability': freq / text_length,
                'frequency': freq,
                'code': ''
            })

        # sort descending by probability (and by symbol for stable order)
        self.nodes.sort(key=lambda x: (-x['probability'], x['symbol']))

    # ---------- Shannon-Fano ----------
    def _split_index(self, probs: List[float]) -> int:
        """
        Return index to split list into two parts with sums as close as possible.
        """
        if not probs:
            return -1
        total = sum(probs)
        acc = 0.0
        best_idx = 0
        best_diff = float('inf')
        for i in range(len(probs)):
            acc += probs[i]
            diff = abs(acc - (total - acc))
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        return best_idx

    def _shannon_fano_recursive(self, items: List[Tuple[str, float]], codes: Dict[str, str]):
        """
        items: list of (symbol, probability) sorted descending by probability
        codes: dict to fill with binary strings
        """
        n = len(items)
        if n == 0:
            return
        if n == 1:
            # single item — if it has no code yet, give '0' (handled externally if needed)
            if codes.get(items[0][0], '') == '':
                codes[items[0][0]] = codes.get(items[0][0], '') or '0'
            return

        probs = [p for (_, p) in items]
        split = self._split_index(probs)
        # left: 0..split, right: split+1..end
        left = items[:split + 1]
        right = items[split + 1:]

        for sym, _ in left:
            codes[sym] = codes.get(sym, '') + '0'
        for sym, _ in right:
            codes[sym] = codes.get(sym, '') + '1'

        # recurse
        self._shannon_fano_recursive(left, codes)
        self._shannon_fano_recursive(right, codes)

    def generate_shannon_fano_codes(self):
        self.fano_codes_map.clear()
        if not self.nodes:
            return
        # build items list sorted by probability desc
        items = [(n['symbol'], n['probability']) for n in self.nodes]
        codes: Dict[str, str] = {symbol: '' for symbol, _ in items}
        self._shannon_fano_recursive(items, codes)

        # Ensure single-symbol case gets at least '0'
        if len(items) == 1:
            codes[items[0][0]] = codes[items[0][0]] or '0'

        # update nodes and map
        for node in self.nodes:
            node['code'] = codes[node['symbol']]
            self.fano_codes_map[node['symbol']] = node['code']

    # ---------- Huffman ----------
    def generate_huffman_codes(self):
        self.huffman_codes_map.clear()
        if not self.frequencies:
            return
        if len(self.frequencies) == 1:
            # single symbol -> code '0'
            only_symbol = next(iter(self.frequencies.keys()))
            self.huffman_codes_map[only_symbol] = '0'
            return

        # build heap of (freq, count, node)
        heap = []
        counter = itertools.count()
        for sym, freq in self.frequencies.items():
            node = Node(symbol=sym, frequency=freq)
            heapq.heappush(heap, (freq, next(counter), node))

        # merge
        while len(heap) > 1:
            f1, _, n1 = heapq.heappop(heap)
            f2, _, n2 = heapq.heappop(heap)
            parent = Node(symbol=None, frequency=f1 + f2)
            parent.left = n1
            parent.right = n2
            heapq.heappush(heap, (parent.frequency, next(counter), parent))

        # root
        _, _, root = heap[0]

        # traverse tree to assign codes
        codes: Dict[str, str] = {}

        def _traverse(node: Node, prefix: str):
            if node is None:
                return
            if node.is_leaf():
                # leaf
                # If prefix is empty (single-symbol case already handled), give '0'
                codes[node.symbol] = prefix or '0'
                return
            _traverse(node.left, prefix + '0')
            _traverse(node.right, prefix + '1')

        _traverse(root, '')

        # store
        self.huffman_codes_map = codes

        # update nodes list codes if present
        for node in self.nodes:
            node['code'] = self.huffman_codes_map.get(node['symbol'], '')

    # ---------- Metrics ----------
    def calculate_entropy(self) -> float:
        if not self.nodes:
            return 0.0
        ent = 0.0
        for node in self.nodes:
            p = node['probability']
            if p > 0:
                ent -= p * math.log2(p)
        return ent

    def calculate_average_length(self, codes_map: Dict[str, str]) -> float:
        if not self.nodes or not codes_map:
            return 0.0
        avg = 0.0
        for node in self.nodes:
            p = node['probability']
            code = codes_map.get(node['symbol'], '')
            avg += p * len(code)
        return avg

    def calculate_redundancy(self, avg_length: float, entropy: float) -> float:
        if avg_length == 0:
            return 0.0
        return (avg_length - entropy) / avg_length

    def encode_text(self, text: str, codes_map: Dict[str, str]) -> str:
        if not codes_map:
            return ''
        out = []
        for ch in text:
            c = codes_map.get(ch, '')
            out.append(c)
        return ''.join(out)


class TextCompressionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы сжатия текста: Шеннон-Фано и Хаффман")
        self.root.geometry("1200x800")

        self.compressor = TextCompression()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = ttk.Label(main_frame, text="Алгоритмы сжатия текста", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        input_frame = ttk.LabelFrame(main_frame, text="Ввод текста", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.text_input = scrolledtext.ScrolledText(input_frame, height=6, font=("Consolas", 10))
        self.text_input.pack(fill=tk.BOTH, expand=True)

        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Загрузить из файла", command=self.load_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Анализировать", command=self.analyze_text).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Очистить", command=self.clear_all).pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        codes_frame = ttk.Frame(self.notebook)
        self.notebook.add(codes_frame, text="Таблицы кодов")

        tables_frame = ttk.Frame(codes_frame)
        tables_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        fano_frame = ttk.LabelFrame(tables_frame, text="Коды Шеннона-Фано", padding=10)
        fano_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.fano_tree = ttk.Treeview(fano_frame, columns=("symbol", "frequency", "probability", "code"), show="headings", height=8)
        self.fano_tree.heading("symbol", text="Символ")
        self.fano_tree.heading("frequency", text="Частота")
        self.fano_tree.heading("probability", text="Вероятность")
        self.fano_tree.heading("code", text="Код")

        self.fano_tree.column("symbol", width=80, anchor=tk.CENTER)
        self.fano_tree.column("frequency", width=80, anchor=tk.CENTER)
        self.fano_tree.column("probability", width=100, anchor=tk.CENTER)
        self.fano_tree.column("code", width=120, anchor=tk.CENTER)

        fano_scrollbar = ttk.Scrollbar(fano_frame, orient=tk.VERTICAL, command=self.fano_tree.yview)
        self.fano_tree.configure(yscrollcommand=fano_scrollbar.set)

        self.fano_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fano_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        huffman_frame = ttk.LabelFrame(tables_frame, text="Коды Хаффмана", padding=10)
        huffman_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.huffman_tree = ttk.Treeview(huffman_frame, columns=("symbol", "frequency", "probability", "code"), show="headings", height=8)
        self.huffman_tree.heading("symbol", text="Символ")
        self.huffman_tree.heading("frequency", text="Частота")
        self.huffman_tree.heading("probability", text="Вероятность")
        self.huffman_tree.heading("code", text="Код")

        self.huffman_tree.column("symbol", width=80, anchor=tk.CENTER)
        self.huffman_tree.column("frequency", width=80, anchor=tk.CENTER)
        self.huffman_tree.column("probability", width=100, anchor=tk.CENTER)
        self.huffman_tree.column("code", width=120, anchor=tk.CENTER)

        huffman_scrollbar = ttk.Scrollbar(huffman_frame, orient=tk.VERTICAL, command=self.huffman_tree.yview)
        self.huffman_tree.configure(yscrollcommand=huffman_scrollbar.set)

        self.huffman_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        huffman_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Результаты анализа")

        stats_frame = ttk.LabelFrame(results_frame, text="Характеристики сжатия", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        ttk.Label(stats_grid, text="Характеристика", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(stats_grid, text="Значение", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(stats_grid, text="Шеннон-Фано", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        ttk.Label(stats_grid, text="Хаффман", font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W)

        self.length_label = ttk.Label(stats_grid, text="Длина исходного текста:")
        self.length_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 20), pady=2)
        self.length_value = ttk.Label(stats_grid, text="0")
        self.length_value.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=2)

        ttk.Label(stats_grid, text="Энтропия:").grid(row=2, column=0, sticky=tk.W, padx=(0, 20), pady=2)
        self.entropy_value = ttk.Label(stats_grid, text="0.000")
        self.entropy_value.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=2)

        ttk.Label(stats_grid, text="Средняя длина кода:").grid(row=3, column=0, sticky=tk.W, padx=(0, 20), pady=2)
        self.fano_avg_length = ttk.Label(stats_grid, text="0.000")
        self.fano_avg_length.grid(row=3, column=2, sticky=tk.W, padx=(0, 20), pady=2)
        self.huffman_avg_length = ttk.Label(stats_grid, text="0.000")
        self.huffman_avg_length.grid(row=3, column=3, sticky=tk.W, pady=2)

        ttk.Label(stats_grid, text="Избыточность:").grid(row=4, column=0, sticky=tk.W, padx=(0, 20), pady=2)
        self.fano_redundancy = ttk.Label(stats_grid, text="0.000")
        self.fano_redundancy.grid(row=4, column=2, sticky=tk.W, padx=(0, 20), pady=2)
        self.huffman_redundancy = ttk.Label(stats_grid, text="0.000")
        self.huffman_redundancy.grid(row=4, column=3, sticky=tk.W, pady=2)

        encoded_frame = ttk.LabelFrame(results_frame, text="Закодированный текст", padding=10)
        encoded_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        encoded_notebook = ttk.Notebook(encoded_frame)
        encoded_notebook.pack(fill=tk.BOTH, expand=True)

        fano_encoded_frame = ttk.Frame(encoded_notebook)
        encoded_notebook.add(fano_encoded_frame, text="Шеннон-Фано")

        self.fano_encoded_text = scrolledtext.ScrolledText(fano_encoded_frame, height=6, font=("Consolas", 9))
        self.fano_encoded_text.pack(fill=tk.BOTH, expand=True)

        huffman_encoded_frame = ttk.Frame(encoded_notebook)
        encoded_notebook.add(huffman_encoded_frame, text="Хаффман")

        self.huffman_encoded_text = scrolledtext.ScrolledText(huffman_encoded_frame, height=6, font=("Consolas", 9))
        self.huffman_encoded_text.pack(fill=tk.BOTH, expand=True)

    def load_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите текстовый файл",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
            )

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_input.delete(1.0, tk.END)
                    self.text_input.insert(1.0, content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def clear_all(self):
        self.text_input.delete(1.0, tk.END)
        self.clear_results()

    def clear_results(self):
        for item in self.fano_tree.get_children():
            self.fano_tree.delete(item)
        for item in self.huffman_tree.get_children():
            self.huffman_tree.delete(item)

        self.length_value.config(text="0")
        self.entropy_value.config(text="0.000")
        self.fano_avg_length.config(text="0.000")
        self.huffman_avg_length.config(text="0.000")
        self.fano_redundancy.config(text="0.000")
        self.huffman_redundancy.config(text="0.000")

        self.fano_encoded_text.delete(1.0, tk.END)
        self.huffman_encoded_text.delete(1.0, tk.END)

    def analyze_text(self):
        text = self.text_input.get(1.0, tk.END).rstrip('\n')
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для анализа!")
            return
        try:
            self.clear_results()
            self.compressor.calculate_frequencies(text)
            self.compressor.generate_shannon_fano_codes()
            self.compressor.generate_huffman_codes()
            self.update_tables()
            self.update_statistics(text)
            self.update_encoded_text(text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе текста: {str(e)}")

    def update_tables(self):
        for node in self.compressor.nodes:
            sym = node['symbol']
            symbol_display = repr(sym) if sym in [' ', '\n', '\t'] else sym
            freq = node.get('frequency', self.compressor.frequencies.get(sym, 0))
            prob = f"{node['probability']:.4f}"
            code_fano = self.compressor.fano_codes_map.get(sym, '')
            self.fano_tree.insert('', 'end', values=(symbol_display, freq, prob, code_fano))

        for node in self.compressor.nodes:
            sym = node['symbol']
            symbol_display = repr(sym) if sym in [' ', '\n', '\t'] else sym
            freq = node.get('frequency', self.compressor.frequencies.get(sym, 0))
            prob = f"{node['probability']:.4f}"
            code_huff = self.compressor.huffman_codes_map.get(sym, '')
            self.huffman_tree.insert('', 'end', values=(symbol_display, freq, prob, code_huff))

    def update_statistics(self, text):
        self.length_value.config(text=str(len(text)))
        entropy = self.compressor.calculate_entropy()
        self.entropy_value.config(text=f"{entropy:.4f}")

        fano_avg_len = self.compressor.calculate_average_length(self.compressor.fano_codes_map)
        huffman_avg_len = self.compressor.calculate_average_length(self.compressor.huffman_codes_map)

        self.fano_avg_length.config(text=f"{fano_avg_len:.4f}")
        self.huffman_avg_length.config(text=f"{huffman_avg_len:.4f}")

        fano_redundancy = self.compressor.calculate_redundancy(fano_avg_len, entropy)
        huffman_redundancy = self.compressor.calculate_redundancy(huffman_avg_len, entropy)

        self.fano_redundancy.config(text=f"{fano_redundancy:.4f}")
        self.huffman_redundancy.config(text=f"{huffman_redundancy:.4f}")

    def update_encoded_text(self, text):
        fano_encoded = self.compressor.encode_text(text, self.compressor.fano_codes_map)
        huffman_encoded = self.compressor.encode_text(text, self.compressor.huffman_codes_map)
        self.fano_encoded_text.insert(1.0, fano_encoded)
        self.huffman_encoded_text.insert(1.0, huffman_encoded)


def main():
    root = tk.Tk()
    app = TextCompressionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
