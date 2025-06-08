import tkinter as tk
from tkinter import ttk, messagebox
import pulp


class PosrednikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zadanie Pośrednika – Aplikacja Transportowa")
        self.root.geometry("1200x700")
        self.root.configure(padx=20, pady=20)

        style = ttk.Style()
        style.configure("TLabel", font=('Arial', 10))
        style.configure("TButton", font=('Arial', 10, 'bold'))
        style.configure("TEntry", padding=5)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        # Główna ramka pozioma
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=1, column=0, sticky='nsew')

        form_frame = ttk.Frame(root)
        form_frame.grid(row=0, column=0, sticky='w', pady=(0, 10))

        ttk.Label(form_frame, text="Liczba dostawców:").grid(row=0, column=0, padx=5, pady=5)
        self.d_entry = ttk.Entry(form_frame, width=5)
        self.d_entry.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Liczba odbiorców:").grid(row=0, column=2, padx=5, pady=5)
        self.o_entry = ttk.Entry(form_frame, width=5)
        self.o_entry.grid(row=0, column=3, padx=5)

        ttk.Button(form_frame, text="Generuj pola", command=self.generate_fields).grid(row=0, column=4, padx=10)

        # Lewe i prawe panele
        self.fields_frame = ttk.LabelFrame(self.main_frame, text="Dane Wejściowe", padding=10)
        self.fields_frame.grid(row=0, column=0, sticky='nw', padx=(0, 20))

        self.result_frame = ttk.LabelFrame(self.main_frame, text="Wyniki", padding=10)
        self.result_frame.grid(row=0, column=1, sticky='ne')

    def generate_fields(self):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        try:
            self.num_d = int(self.d_entry.get())
            self.num_o = int(self.o_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawne liczby całkowite.")
            return

        self.entries = {}
        row = 0

        ttk.Label(self.fields_frame, text="DOSTAWCY", font=('Arial', 10, 'bold')).grid(row=row, column=0, pady=5)
        row += 1
        for i in range(self.num_d):
            d = f"D{i+1}"
            ttk.Label(self.fields_frame, text=f"{d} - Podaż:").grid(row=row, column=0, sticky='w')
            self.entries[f"{d}_supply"] = ttk.Entry(self.fields_frame, width=6)
            self.entries[f"{d}_supply"].grid(row=row, column=1)

            ttk.Label(self.fields_frame, text=f"{d} - Koszt zakupu:").grid(row=row, column=2, sticky='w')
            self.entries[f"{d}_cost"] = ttk.Entry(self.fields_frame, width=6)
            self.entries[f"{d}_cost"].grid(row=row, column=3)
            row += 1

        ttk.Label(self.fields_frame, text="ODBIORCY", font=('Arial', 10, 'bold')).grid(row=row, column=0, pady=5)
        row += 1
        for j in range(self.num_o):
            o = f"O{j+1}"
            ttk.Label(self.fields_frame, text=f"{o} - Popyt:").grid(row=row, column=0, sticky='w')
            self.entries[f"{o}_demand"] = ttk.Entry(self.fields_frame, width=6)
            self.entries[f"{o}_demand"].grid(row=row, column=1)

            ttk.Label(self.fields_frame, text=f"{o} - Cena sprzedaży:").grid(row=row, column=2, sticky='w')
            self.entries[f"{o}_price"] = ttk.Entry(self.fields_frame, width=6)
            self.entries[f"{o}_price"].grid(row=row, column=3)
            row += 1

        ttk.Label(self.fields_frame, text="KOSZTY TRANSPORTU", font=('Arial', 10, 'bold')).grid(row=row, column=0, pady=5)
        row += 1
        for i in range(self.num_d):
            d = f"D{i+1}"
            for j in range(self.num_o):
                o = f"O{j+1}"
                key = f"{d}_{o}"
                ttk.Label(self.fields_frame, text=f"{d} → {o}:").grid(row=row, column=0, sticky='w')
                self.entries[key] = ttk.Entry(self.fields_frame, width=6)
                self.entries[key].grid(row=row, column=1)
                row += 1

        ttk.Button(self.fields_frame, text="Oblicz zysk", command=self.solve).grid(row=row, column=0, columnspan=4, pady=10)

    def solve(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        try:
            dostawcy = [f"D{i+1}" for i in range(self.num_d)]
            odbiorcy = [f"O{j+1}" for j in range(self.num_o)]

            podaz = {d: int(self.entries[f"{d}_supply"].get()) for d in dostawcy}
            koszt_zakupu = {d: int(self.entries[f"{d}_cost"].get()) for d in dostawcy}
            popyt = {o: int(self.entries[f"{o}_demand"].get()) for o in odbiorcy}
            cena = {o: int(self.entries[f"{o}_price"].get()) for o in odbiorcy}
            koszt_transportu = {(d, o): int(self.entries[f"{d}_{o}"].get()) for d in dostawcy for o in odbiorcy}

            zysk = {(d, o): cena[o] - koszt_zakupu[d] - koszt_transportu[(d, o)] for d in dostawcy for o in odbiorcy}

            prob = pulp.LpProblem("Zysk_Posrednika", pulp.LpMaximize)
            x = pulp.LpVariable.dicts("x", [(d, o) for d in dostawcy for o in odbiorcy], lowBound=0, cat='Integer')

            prob += pulp.lpSum([zysk[(d, o)] * x[(d, o)] for d in dostawcy for o in odbiorcy])
            for d in dostawcy:
                prob += pulp.lpSum([x[(d, o)] for o in odbiorcy]) <= podaz[d]
            for o in odbiorcy:
                prob += pulp.lpSum([x[(d, o)] for d in dostawcy]) <= popyt[o]

            prob.solve(pulp.PULP_CBC_CMD(msg=False))

            # Tabela zysków jednostkowych
            ttk.Label(self.result_frame, text="Macierz zysków jednostkowych", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5, 5))
            zysk_tree = ttk.Treeview(self.result_frame, columns=odbiorcy, show='headings', height=len(dostawcy))
            for o in odbiorcy:
                zysk_tree.heading(o, text=o)
                zysk_tree.column(o, width=80, anchor='center')
            for d in dostawcy:
                row = [f"{zysk[(d, o)]:.2f}" for o in odbiorcy]
                zysk_tree.insert('', 'end', values=row)
            zysk_tree.pack(anchor='w', pady=(0, 15))

            # Optymalny transport
            ttk.Label(self.result_frame, text="Optymalny transport", font=('Arial', 11, 'bold')).pack(anchor='w')
            trans_tree = ttk.Treeview(self.result_frame, columns=odbiorcy, show='headings', height=len(dostawcy))
            for o in odbiorcy:
                trans_tree.heading(o, text=o)
                trans_tree.column(o, width=80, anchor='center')
            for d in dostawcy:
                row = [f"{x[(d, o)].varValue:.0f}" if x[(d, o)].varValue else "0" for o in odbiorcy]
                trans_tree.insert('', 'end', values=row)
            trans_tree.pack(anchor='w', pady=(0, 15))

            # Wyniki finansowe
            koszt_t = sum(koszt_transportu[(d, o)] * x[(d, o)].varValue for d in dostawcy for o in odbiorcy)
            koszt_z = sum(koszt_zakupu[d] * sum(x[(d, o)].varValue for o in odbiorcy) for d in dostawcy)
            przychod = sum(cena[o] * sum(x[(d, o)].varValue for d in dostawcy) for o in odbiorcy)
            zysk_calkowity = przychod - koszt_z - koszt_t

            podsumowanie = [
                f"Koszt transportu: {koszt_t:.2f}",
                f"Koszt zakupu: {koszt_z:.2f}",
                f"Koszt całkowity: {koszt_t + koszt_z:.2f}",
                f"Przychód całkowity: {przychod:.2f}",
                f"Zysk pośrednika: {zysk_calkowity:.2f}"
            ]
            for linia in podsumowanie:
                ttk.Label(self.result_frame, text=linia).pack(anchor='w', pady=1)

        except Exception as e:
            messagebox.showerror("Błąd", f"Coś poszło nie tak:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PosrednikApp(root)
    root.mainloop()
