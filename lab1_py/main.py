import tkinter as tk
from tkinter import ttk, messagebox
import math
from functools import partial

# Helper math functions
EPS = 1e-12

def safe_log2(x):
    return math.log2(x) if x > 0 else 0.0

def entropy_from_probs(probs):
    H = 0.0
    for p in probs:
        if p > 0:
            H -= p * math.log2(p)
    return H

# Core computations for different input cases

def from_joint_to_all(Pab):
    na = len(Pab)
    nb = len(Pab[0]) if na>0 else 0
    joint = [[max(0.0, float(Pab[i][j])) for j in range(nb)] for i in range(na)]
    total = sum(sum(row) for row in joint)
    if abs(total - 1.0) > 1e-6 and total > 0:
        joint = [[x/total for x in row] for row in joint]
    Pa = [sum(joint[i][j] for j in range(nb)) for i in range(na)]
    Pb = [sum(joint[i][j] for i in range(na)) for j in range(nb)]
    P_b_given_a = [[0.0]*nb for _ in range(na)]
    P_a_given_b = [[0.0]*nb for _ in range(na)]
    for i in range(na):
        for j in range(nb):
            if Pa[i] > EPS:
                P_b_given_a[i][j] = joint[i][j] / Pa[i]
            else:
                P_b_given_a[i][j] = 0.0
            if Pb[j] > EPS:
                P_a_given_b[i][j] = joint[i][j] / Pb[j]
            else:
                P_a_given_b[i][j] = 0.0
    H_A = entropy_from_probs(Pa)
    H_B = entropy_from_probs(Pb)
    H_B_given_A = sum(Pa[i] * entropy_from_probs(P_b_given_a[i]) for i in range(na))
    H_A_given_B = sum(Pb[j] * entropy_from_probs([P_a_given_b[i][j] for i in range(na)]) for j in range(nb))
    flat = [joint[i][j] for i in range(na) for j in range(nb)]
    H_AB = entropy_from_probs(flat)
    I = H_A + H_B - H_AB
    return {
        'joint': joint,
        'Pa': Pa,
        'Pb': Pb,
        'P(B|A)': P_b_given_a,
        'P(A|B)': P_a_given_b,
        'H(A)': H_A,
        'H(B)': H_B,
        'H(B|A)': H_B_given_A,
        'H(A|B)': H_A_given_B,
        'H(AB)': H_AB,
        'I(A;B)': I,
    }

def from_Pa_and_PbgivenA(Pa, PbgivenA):
    na = len(Pa)
    nb = len(PbgivenA[0]) if na>0 else 0
    joint = [[max(0.0, Pa[i] * PbgivenA[i][j]) for j in range(nb)] for i in range(na)]
    total = sum(sum(row) for row in joint)
    if total <= 0:
        raise ValueError('Joint probability sums to zero; check inputs')
    if abs(total-1.0) > 1e-6:
        joint = [[x/total for x in row] for row in joint]
    res = from_joint_to_all(joint)
    res['joint'] = joint  # explicitly store joint for display
    return res

def from_Pb_and_PagivenB(Pb, PagivenB):
    na = len(PagivenB)
    nb = len(Pb)
    joint = [[max(0.0, PagivenB[i][j] * Pb[j]) for j in range(nb)] for i in range(na)]
    total = sum(sum(row) for row in joint)
    if total <= 0:
        raise ValueError('Joint probability sums to zero; check inputs')
    if abs(total-1.0) > 1e-6:
        joint = [[x/total for x in row] for row in joint]
    res = from_joint_to_all(joint)
    res['joint'] = joint  # explicitly store joint for display
    return res

class EntropyApp:
    def __init__(self, root):
        self.root = root
        root.title('Энтропия объединения двух источников')
        self.mainframe = ttk.Frame(root, padding=10)
        self.mainframe.grid(sticky='nsew')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.case_var = tk.StringVar(value='joint')
        cases = [
            ('Дана матрица совместных вероятностей P(AB)', 'joint'),
            ('Дана матрица условных P(A|B) и ансамбль B', 'A_given_B'),
            ('Дана матрица условных P(B|A) и ансамбль A', 'B_given_A'),
        ]
        ttk.Label(self.mainframe, text='Случай рассмотрения:').grid(column=0, row=0, sticky='w')
        for i,(txt,val) in enumerate(cases, start=1):
            ttk.Radiobutton(self.mainframe, text=txt, variable=self.case_var, value=val).grid(column=0, row=i, sticky='w')

        sizeframe = ttk.Frame(self.mainframe)
        sizeframe.grid(column=0, row=4, sticky='w', pady=(10,0))
        ttk.Label(sizeframe, text='Размер матрицы:').grid(column=0, row=0)
        ttk.Label(sizeframe, text='Число состояний A (строки):').grid(column=0, row=1, sticky='e')
        self.na_spin = tk.Spinbox(sizeframe, from_=1, to=10, width=5)
        self.na_spin.grid(column=1, row=1, sticky='w')
        ttk.Label(sizeframe, text='Число состояний B (столбцы):').grid(column=2, row=1, sticky='e')
        self.nb_spin = tk.Spinbox(sizeframe, from_=1, to=10, width=5)
        self.nb_spin.grid(column=3, row=1, sticky='w')

        ttk.Button(self.mainframe, text='Сформировать поля ввода', command=self.build_matrix_inputs).grid(column=0, row=5, pady=(10,0), sticky='w')
        self.inputs_frame = ttk.Frame(self.mainframe)
        self.inputs_frame.grid(column=0, row=6, sticky='nsew', pady=(10,0))

        ttk.Button(self.mainframe, text='Рассчитать', command=self.calculate).grid(column=0, row=7, pady=(10,0), sticky='w')
        ttk.Label(self.mainframe, text='Результаты:').grid(column=0, row=8, sticky='w', pady=(10,0))
        self.out_text = tk.Text(self.mainframe, width=90, height=20)
        self.out_text.grid(column=0, row=9, sticky='nsew')

        self.matrix_entries = []
        self.ensemble_entries = []

    def clear_inputs(self):
        for child in self.inputs_frame.winfo_children():
            child.destroy()
        self.matrix_entries = []
        self.ensemble_entries = []

    def build_matrix_inputs(self):
        self.clear_inputs()
        try:
            na = int(self.na_spin.get())
            nb = int(self.nb_spin.get())
        except Exception:
            messagebox.showerror('Ошибка', 'Размеры матрицы должны быть целыми числами')
            return
        case = self.case_var.get()
        ttk.Label(self.inputs_frame, text='Ансамбль A -> строки, Ансамбль B -> столбцы').grid(column=0, row=0, columnspan=nb+2)
        start_row = 1
        for j in range(nb):
            ttk.Label(self.inputs_frame, text=f'B{j+1}').grid(column=1+j, row=start_row)
        self.matrix_entries = [[None]*nb for _ in range(na)]
        for i in range(na):
            ttk.Label(self.inputs_frame, text=f'A{i+1}').grid(column=0, row=start_row+1+i)
            for j in range(nb):
                e = ttk.Entry(self.inputs_frame, width=8)
                e.grid(column=1+j, row=start_row+1+i)
                e.insert(0, '0')
                self.matrix_entries[i][j] = e
        if case == 'joint':
            ttk.Label(self.inputs_frame, text='(Input: joint P(A,B) entries)').grid(column=0, row=start_row+1+na, columnspan=nb+1, sticky='w')
        elif case == 'A_given_B':
            ttk.Label(self.inputs_frame, text='Ансамбль B (P(B_j)) — введите вероятности для каждого столбца:').grid(column=0, row=start_row+1+na, columnspan=nb+1, sticky='w')
            self.ensemble_entries = []
            for j in range(nb):
                e = ttk.Entry(self.inputs_frame, width=8)
                e.grid(column=1+j, row=start_row+2+na)
                e.insert(0, '0')
                self.ensemble_entries.append(e)
            ttk.Label(self.inputs_frame, text='(Вводим P(A|B) матрицу: строки=A, столбцы=B; суммы по строкам=1)').grid(column=0, row=start_row+3+na, columnspan=nb+1, sticky='w')
        elif case == 'B_given_A':
            ttk.Label(self.inputs_frame, text='Ансамбль A (P(A_i)) — введите вероятности для каждой строки:').grid(column=0, row=start_row+1+na, columnspan=nb+1, sticky='w')
            self.ensemble_entries = []
            for i in range(na):
                e = ttk.Entry(self.inputs_frame, width=8)
                e.grid(column=0, row=start_row+2+na+i, sticky='w')
                e.insert(0, '0')
                ttk.Label(self.inputs_frame, text=f'P(A{i+1})').grid(column=1, row=start_row+2+na+i, sticky='w')
                self.ensemble_entries.append(e)
            ttk.Label(self.inputs_frame, text='(Вводим P(B|A) матрицу: строки=A, столбцы=B; суммы по столбцам=1)').grid(column=0, row=start_row+2+na+na, columnspan=nb+1, sticky='w')

    def read_matrix(self):
        na = len(self.matrix_entries)
        nb = len(self.matrix_entries[0]) if na>0 else 0
        M = [[0.0]*nb for _ in range(na)]
        for i in range(na):
            for j in range(nb):
                text = self.matrix_entries[i][j].get()
                try:
                    val = float(text.replace(',','.'))
                except Exception:
                    val = 0.0
                M[i][j] = val
        return M

    def read_ensemble(self):
        arr = []
        for e in self.ensemble_entries:
            try:
                val = float(e.get().replace(',','.'))
            except Exception:
                val = 0.0
            arr.append(val)
        return arr

    def format_matrix(self, M):
        s = ''
        for row in M:
            s += '[' + ', '.join(f'{v:.6f}' for v in row) + ']\n'
        return s

    def calculate(self):
        case = self.case_var.get()
        na = int(self.na_spin.get())
        nb = int(self.nb_spin.get())
        try:
            if case == 'joint':
                M = self.read_matrix()
                res = from_joint_to_all(M)
            elif case == 'A_given_B':
                PagivenB = self.read_matrix()
                Pb = self.read_ensemble()
                if len(Pb) != nb:
                    messagebox.showerror('Ошибка', 'Длина ансамбля B не совпадает с числом столбцов')
                    return
                for j in range(nb):
                    col_sum = sum(PagivenB[i][j] for i in range(na))
                    if abs(col_sum - 1.0) > 1e-6 and col_sum>EPS:
                        for i in range(na):
                            PagivenB[i][j] = PagivenB[i][j] / col_sum
                res = from_Pb_and_PagivenB(Pb, PagivenB)
            elif case == 'B_given_A':
                PbgivenA = self.read_matrix()
                Pa = self.read_ensemble()
                if len(Pa) != na:
                    messagebox.showerror('Ошибка', 'Длина ансамбля A не совпадает с числом строк')
                    return
                for i in range(na):
                    row_sum = sum(PbgivenA[i][j] for j in range(nb))
                    if abs(row_sum - 1.0) > 1e-6 and row_sum>EPS:
                        for j in range(nb):
                            PbgivenA[i][j] = PbgivenA[i][j] / row_sum
                res = from_Pa_and_PbgivenA(Pa, PbgivenA)
            else:
                messagebox.showerror('Ошибка', 'Неизвестный случай')
                return
        except Exception as ex:
            messagebox.showerror('Ошибка вычисления', str(ex))
            return

        self.out_text.delete('1.0', tk.END)
        out = []
        # Вывод совместной вероятности при ансамбле
        if case in ['A_given_B','B_given_A']:
            out.append('Матрица совместных вероятностей P(A,B):\n')
            out.append(self.format_matrix(res['joint']))
            out.append('\n')

        out.append('Ансамбль A (P(A_i)):\n')
        out.append('[' + ', '.join(f'{p:.6f}' for p in res['Pa']) + ']\n\n')
        out.append('Ансамбль B (P(B_j)):\n')
        out.append('[' + ', '.join(f'{p:.6f}' for p in res['Pb']) + ']\n\n')
        out.append(f"H(A) = {res['H(A)']:.6f} бит\n")
        out.append(f"H(B) = {res['H(B)']:.6f} бит\n")
        out.append(f"H(B|A) = {res['H(B|A)']:.6f} бит\n")
        out.append(f"H(A|B) = {res['H(A|B)']:.6f} бит\n")
        out.append(f"H(AB) = {res['H(AB)']:.6f} бит\n")
        out.append(f"I(A;B) = {res['I(A;B)']:.6f} бит\n\n")
        out.append('Матрица условных вероятностей P(B|A) (строки=A, столбцы=B):\n')
        out.append(self.format_matrix(res['P(B|A)']))
        out.append('\nМатрица условных вероятностей P(A|B) (строки=A, столбцы=B):\n')
        out.append(self.format_matrix(res['P(A|B)']))

        self.out_text.insert(tk.END, ''.join(out))

if __name__ == '__main__':
    root = tk.Tk()
    app = EntropyApp(root)
    root.mainloop()
