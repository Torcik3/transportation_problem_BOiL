import tkinter as tk
from tkinter import ttk, messagebox
import pulp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PosrednikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zadanie Pośrednika – Aplikacja Transportowa")
        self.root.geometry("1300x750")
        self.root.configure(padx=10, pady=10)

        style = ttk.Style()
        style.configure("TLabel", font=('Arial', 10))
        style.configure("TButton", font=('Arial', 10, 'bold'))
        style.configure("TEntry", padding=5)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

        # Frames
        self.form_frame = ttk.LabelFrame(root, text="Konfiguracja", padding=10)
        self.form_frame.grid(row=0, column=0, sticky='new')

        self.fields_frame = ttk.LabelFrame(root, text="Dane Wejściowe", padding=10)
        self.fields_frame.grid(row=1, column=0, sticky='nsew')

        self.result_frame = ttk.LabelFrame(root, text="Wyniki", padding=10)
        self.result_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=(10, 0))

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)

        # Entry for number of suppliers and consumers
        ttk.Label(self.form_frame, text="Liczba dostawców:").grid(row=0, column=0, padx=5, pady=5)
        self.d_entry = ttk.Entry(self.form_frame, width=5)
        self.d_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.form_frame, text="Liczba odbiorców:").grid(row=0, column=2, padx=5, pady=5)
        self.o_entry = ttk.Entry(self.form_frame, width=5)
        self.o_entry.grid(row=0, column=3, padx=5)

        ttk.Button(self.form_frame, text="Generuj pola", command=self.generate_fields).grid(row=0, column=4, padx=10)

    def validate_integer(self, entry, name):
        val = entry.get()
        try:
            value = int(val)
            if value < 0:
                raise ValueError
            entry.configure(background='white')
            return True
        except:
            messagebox.showerror("Błąd", f"{name} musi być nieujemną liczbą całkowitą.")
            entry.configure(background='salmon')
            return False

    def generate_fields(self):
        if not self.validate_integer(self.d_entry, "Liczba dostawców"):
            return
        if not self.validate_integer(self.o_entry, "Liczba odbiorców"):
            return

        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        self.num_d = int(self.d_entry.get())
        self.num_o = int(self.o_entry.get())
        self.entries = {}
        row = 0

        ttk.Label(self.fields_frame, text="DOSTAWCY", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=4, pady=5)
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

        ttk.Label(self.fields_frame, text="ODBIORCY", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=4, pady=5)
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

        ttk.Label(self.fields_frame, text="KOSZTY TRANSPORTU", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=4, pady=5)
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

        błędne_pola = []

        def get_int(name):
            entry = self.entries[name]
            try:
                value = int(entry.get())
                if value < 0:
                    raise ValueError
                entry.configure(background='white')
                return value
            except:
                błędne_pola.append(entry)
                entry.configure(background='salmon')
                raise ValueError(f"Niepoprawna wartość w polu: {name}")

        try:
            dostawcy = [f"D{i+1}" for i in range(self.num_d)]
            odbiorcy = [f"O{j+1}" for j in range(self.num_o)]

            podaz = {d: get_int(f"{d}_supply") for d in dostawcy}
            koszt_zakupu = {d: get_int(f"{d}_cost") for d in dostawcy}
            popyt = {o: get_int(f"{o}_demand") for o in odbiorcy}
            cena = {o: get_int(f"{o}_price") for o in odbiorcy}
            koszt_transportu = {(d, o): get_int(f"{d}_{o}") for d in dostawcy for o in odbiorcy}

            if sum(podaz.values()) == 0 or sum(popyt.values()) == 0:
                raise ValueError("Podaż i popyt muszą być większe od zera.")

            zysk = {(d, o): cena[o] - koszt_zakupu[d] - koszt_transportu[(d, o)] for d in dostawcy for o in odbiorcy}

            prob = pulp.LpProblem("Zysk_Posrednika", pulp.LpMaximize)
            x = pulp.LpVariable.dicts("x", [(d, o) for d in dostawcy for o in odbiorcy], lowBound=0, cat='Integer')
            prob += pulp.lpSum(zysk[(d, o)] * x[(d, o)] for d in dostawcy for o in odbiorcy)
            for d in dostawcy:
                prob += pulp.lpSum(x[(d, o)] for o in odbiorcy) <= podaz[d]
            for o in odbiorcy:
                prob += pulp.lpSum(x[(d, o)] for d in dostawcy) <= popyt[o]

            prob.solve(pulp.PULP_CBC_CMD(msg=False))

            # Wyświetlanie macierzy zysków
            ttk.Label(self.result_frame, text="Macierz zysków jednostkowych", font=('Arial', 11, 'bold')).pack(anchor='w')
            tree1 = ttk.Treeview(self.result_frame, columns=odbiorcy, show='headings', height=len(dostawcy))
            for o in odbiorcy:
                tree1.heading(o, text=o)
                tree1.column(o, width=80, anchor='center')
            for d in dostawcy:
                tree1.insert('', 'end', values=[zysk[(d, o)] for o in odbiorcy])
            tree1.pack(pady=5, anchor='w')

            # Wyświetlanie transportu
            ttk.Label(self.result_frame, text="Optymalny transport", font=('Arial', 11, 'bold')).pack(anchor='w')
            tree2 = ttk.Treeview(self.result_frame, columns=odbiorcy, show='headings', height=len(dostawcy))
            for o in odbiorcy:
                tree2.heading(o, text=o)
                tree2.column(o, width=80, anchor='center')
            for d in dostawcy:
                tree2.insert('', 'end', values=[int(x[(d, o)].varValue or 0) for o in odbiorcy])
            tree2.pack(pady=5, anchor='w')

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
            # Wykres słupkowy
            fig, ax = plt.subplots(figsize=(5, 3))
            podaz_list = [sum(x[(d, o)].varValue for o in odbiorcy) for d in dostawcy]
            zysk_list = [sum(zysk[(d, o)] * x[(d, o)].varValue for o in odbiorcy) for d in dostawcy]
            x_labels = dostawcy
            x_pos = range(len(dostawcy))

            ax.bar(x_pos, podaz_list, width=0.4, label='Podaż', align='center')
            ax.bar([p + 0.4 for p in x_pos], zysk_list, width=0.4, label='Zysk', align='center')
            ax.set_xticks([p + 0.2 for p in x_pos])
            ax.set_xticklabels(x_labels)
            ax.set_title("Podaż i Zysk wg Dostawcy")
            ax.legend()
            ax.grid(True, axis='y')

            canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(anchor='w', pady=10)

        except ValueError as ve:
            for entry in błędne_pola:
                entry.configure(background='salmon')
            messagebox.showerror("Błąd danych", str(ve))
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił nieoczekiwany błąd:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PosrednikApp(root)
    root.mainloop()