import tkinter as tk
from tkinter import messagebox, ttk
import pulp


class PosrednikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zadanie Pośrednika – Dynamiczna wersja")


        self.d_label = tk.Label(root, text="Liczba dostawców:")
        self.d_label.grid(row=0, column=0)
        self.d_entry = tk.Entry(root, width=5)
        self.d_entry.grid(row=0, column=1)

        self.o_label = tk.Label(root, text="Liczba odbiorców:")
        self.o_label.grid(row=0, column=2)
        self.o_entry = tk.Entry(root, width=5)
        self.o_entry.grid(row=0, column=3)

        self.generate_btn = tk.Button(root, text="Generuj pola", command=self.generate_fields)
        self.generate_btn.grid(row=0, column=4)

        self.fields_frame = tk.Frame(root)
        self.fields_frame.grid(row=1, column=0, columnspan=5, sticky='nw')

    def generate_fields(self):
        # Wyczyść wcześniejsze pola
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        try:
            self.num_d = int(self.d_entry.get())
            self.num_o = int(self.o_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawne liczby całkowite.")
            return

        self.entries = {}

        row = 0
        tk.Label(self.fields_frame, text="DOSTAWCY").grid(row=row, column=0, columnspan=2); row += 1
        for i in range(self.num_d):
            d = f"D{i+1}"
            tk.Label(self.fields_frame, text=f"{d} - Podaż:").grid(row=row, column=0)
            self.entries[f"{d}_supply"] = tk.Entry(self.fields_frame, width=5)
            self.entries[f"{d}_supply"].grid(row=row, column=1)

            tk.Label(self.fields_frame, text=f"{d} - Koszt zakupu:").grid(row=row, column=2)
            self.entries[f"{d}_cost"] = tk.Entry(self.fields_frame, width=5)
            self.entries[f"{d}_cost"].grid(row=row, column=3)
            row += 1

        tk.Label(self.fields_frame, text="ODBIORCY").grid(row=row, column=0, columnspan=2); row += 1
        for j in range(self.num_o):
            o = f"O{j+1}"
            tk.Label(self.fields_frame, text=f"{o} - Popyt:").grid(row=row, column=0)
            self.entries[f"{o}_demand"] = tk.Entry(self.fields_frame, width=5)
            self.entries[f"{o}_demand"].grid(row=row, column=1)

            tk.Label(self.fields_frame, text=f"{o} - Cena sprzedaży:").grid(row=row, column=2)
            self.entries[f"{o}_price"] = tk.Entry(self.fields_frame, width=5)
            self.entries[f"{o}_price"].grid(row=row, column=3)
            row += 1

        tk.Label(self.fields_frame, text="KOSZTY TRANSPORTU").grid(row=row, column=0, columnspan=4); row += 1
        for i in range(self.num_d):
            d = f"D{i+1}"
            for j in range(self.num_o):
                o = f"O{j+1}"
                key = f"{d}_{o}"
                tk.Label(self.fields_frame, text=f"{d} → {o}:").grid(row=row, column=0)
                self.entries[key] = tk.Entry(self.fields_frame, width=5)
                self.entries[key].grid(row=row, column=1)
                row += 1

        tk.Button(self.fields_frame, text="Oblicz zysk", command=self.solve).grid(row=row, column=0, columnspan=4, pady=10)

    def solve(self):
        try:
            # Pobierz dane
            dostawcy = [f"D{i+1}" for i in range(self.num_d)]
            odbiorcy = [f"O{j+1}" for j in range(self.num_o)]

            podaz = {d: int(self.entries[f"{d}_supply"].get()) for d in dostawcy}
            koszt_zakupu = {d: int(self.entries[f"{d}_cost"].get()) for d in dostawcy}
            popyt = {o: int(self.entries[f"{o}_demand"].get()) for o in odbiorcy}
            cena = {o: int(self.entries[f"{o}_price"].get()) for o in odbiorcy}
            koszt_transportu = {}
            for d in dostawcy:
                for o in odbiorcy:
                    koszt_transportu[(d, o)] = int(self.entries[f"{d}_{o}"].get())


            zysk = {(d, o): cena[o] - koszt_zakupu[d] - koszt_transportu[(d, o)] for d in dostawcy for o in odbiorcy}


            prob = pulp.LpProblem("Zysk_Posrednika", pulp.LpMaximize)
            x = pulp.LpVariable.dicts("x", [(d, o) for d in dostawcy for o in odbiorcy], lowBound=0, cat='Integer')

            prob += pulp.lpSum([zysk[(d, o)] * x[(d, o)] for d in dostawcy for o in odbiorcy])
            for d in dostawcy:
                prob += pulp.lpSum([x[(d, o)] for o in odbiorcy]) <= podaz[d]
            for o in odbiorcy:
                prob += pulp.lpSum([x[(d, o)] for d in dostawcy]) <= popyt[o]

            prob.solve(pulp.PULP_CBC_CMD(msg=False))


            wynik = ""
            for d in dostawcy:
                for o in odbiorcy:
                    val = x[(d, o)].varValue
                    if val and val > 0:
                        wynik += f"{d} → {o}: {val} szt.\n"

            przychod = sum(cena[o] * sum(x[(d, o)].varValue for d in dostawcy) for o in odbiorcy)
            koszt_z = sum(koszt_zakupu[d] * sum(x[(d, o)].varValue for o in odbiorcy) for d in dostawcy)
            koszt_t = sum(koszt_transportu[(d, o)] * x[(d, o)].varValue for d in dostawcy for o in odbiorcy)
            zysk_calkowity = przychod - koszt_z - koszt_t

            wynik += f"\nPrzychód: {przychod:.2f} zł\nKoszt zakupu: {koszt_z:.2f} zł\nKoszt transportu: {koszt_t:.2f} zł\nZysk: {zysk_calkowity:.2f} zł"

            messagebox.showinfo("Wynik", wynik)

        except Exception as e:
            messagebox.showerror("Błąd", f"Coś poszło nie tak.\n{e}")


# === URUCHOMIENIE APLIKACJI ===
if __name__ == "__main__":
    root = tk.Tk()
    app = PosrednikApp(root)
    root.mainloop()
