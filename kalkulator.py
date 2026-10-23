import math
import re

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OPERATORY = {"+", "−", "×", "÷", "^"}
FUNKCJE = {"√", "x²", "1/x", "%", "±"}

# Dozwolone znaki w wyrażeniu (zabezpieczenie przed wpisaniem czegoś dziwnego)
DOZWOLONE = re.compile(r"^[0-9e+\-*/. ]+$")
LICZBA = re.compile(r"\d+\.?\d*(?:e[+-]?\d+)?|\.\d+")


class Kalkulator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator")
        self.geometry("360x560")
        self.resizable(False, False)

        self.wyrazenie = ""      # to, co widać na ekranie
        self.po_wyniku = False   # czy przed chwilą policzyliśmy wynik

        # --- Ekran ---
        self.historia = ctk.CTkLabel(self, text="", anchor="e",
                                     font=("Segoe UI", 16), text_color="gray")
        self.historia.pack(fill="x", padx=20, pady=(20, 0))

        self.ekran = ctk.CTkLabel(self, text="0", anchor="e",
                                  font=("Segoe UI", 40, "bold"))
        self.ekran.pack(fill="x", padx=20, pady=(0, 15))

        # --- Przyciski ---
        ramka = ctk.CTkFrame(self, fg_color="transparent")
        ramka.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        uklad = [
            ["C", "⌫", "%", "÷"],
            ["√", "x²", "xʸ", "×"],
            ["7", "8", "9", "−"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "1/x"],
            ["±", "0", ".", "="],
        ]

        for r, wiersz in enumerate(uklad):
            ramka.grid_rowconfigure(r, weight=1)
            for c, znak in enumerate(wiersz):
                ramka.grid_columnconfigure(c, weight=1)
                kolor, hover = self.kolor_przycisku(znak)
                ctk.CTkButton(
                    ramka, text=znak, font=("Segoe UI", 22, "bold"),
                    fg_color=kolor, hover_color=hover, corner_radius=12,
                    command=lambda z=znak: self.nacisnij(z),
                ).grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        # Obsługa klawiatury
        self.bind("<Key>", self.klawisz)

    # ---------- wygląd ----------
    def kolor_przycisku(self, znak):
        if znak.isdigit() or znak in (".", "±"):
            return "#3a3a3a", "#4a4a4a"      # cyfry
        if znak in ("+", "−", "×", "÷", "xʸ"):
            return "#ff9500", "#ffad33"      # działania
        if znak == "=":
            return "#34c759", "#5dd879"      # wynik
        if znak == "C":
            return "#ff3b30", "#ff6259"      # czyszczenie
        return "#5e5ce6", "#7d7bf0"          # funkcje (√, x², % ...)

    def odswiez(self):
        tekst = self.wyrazenie or "0"
        rozmiar = 40 if len(tekst) <= 12 else 28 if len(tekst) <= 18 else 20
        self.ekran.configure(text=tekst, font=("Segoe UI", rozmiar, "bold"))

    # ---------- logika ----------
    def nacisnij(self, znak):
        if znak == "xʸ":
            znak = "^"

        if znak.isdigit() or znak == ".":
            self.dodaj_cyfre(znak)
        elif znak in OPERATORY:
            self.dodaj_operator(znak)
        elif znak in FUNKCJE:
            self.funkcja(znak)
        elif znak == "=":
            self.rownasie()
        elif znak == "C":
            self.wyrazenie = ""
            self.historia.configure(text="")
        elif znak == "⌫":
            self.wyrazenie = self.wyrazenie[:-1]
        self.odswiez()

    def dodaj_cyfre(self, znak):
        if self.po_wyniku:               # nowa liczba po "=" zaczyna od zera
            self.wyrazenie = ""
            self.po_wyniku = False

        ostatnia_liczba = re.split(r"[+−×÷^]", self.wyrazenie)[-1]
        if znak == ".":
            if "." in ostatnia_liczba:   # nie pozwalamy na dwie kropki
                return
            if ostatnia_liczba == "":
                znak = "0."
        if self.wyrazenie == "0" and znak != ".":
            self.wyrazenie = ""
        self.wyrazenie += znak

    def dodaj_operator(self, znak):
        self.po_wyniku = False
        if not self.wyrazenie:
            self.wyrazenie = "0"
        if self.wyrazenie[-1] in OPERATORY:  # zamiana np. "+" na "×"
            self.wyrazenie = self.wyrazenie[:-1]
        self.wyrazenie += znak

    def oblicz(self, tekst):
        """Zamienia tekst z ekranu na liczbę."""
        while tekst and tekst[-1] in OPERATORY:   # "5+" -> "5"
            tekst = tekst[:-1]
        wyr = (tekst.replace("−", "-").replace("×", "*")
                    .replace("÷", "/").replace("^", "**"))
        if not wyr or not DOZWOLONE.match(wyr):
            raise ValueError
        # każdą liczbę traktujemy jako float (chroni przed gigantycznymi potęgami)
        wyr = LICZBA.sub(lambda m: repr(float(m.group())), wyr)
        wynik = eval(wyr, {"__builtins__": {}}, {})
        if isinstance(wynik, complex):  # np. pierwiastek z liczby ujemnej
            raise ValueError
        return float(wynik)

    def formatuj(self, liczba):
        if liczba.is_integer() and abs(liczba) < 1e15:
            tekst = str(int(liczba))
        else:
            tekst = f"{liczba:.10g}"
        return tekst.replace("-", "−")

    def pokaz_blad(self, blad):
        if isinstance(blad, ZeroDivisionError):
            komunikat = "Nie dziel przez 0"
        elif isinstance(blad, OverflowError):
            komunikat = "Za duża liczba"
        else:
            komunikat = "Błąd"
        self.wyrazenie = ""
        self.po_wyniku = True
        self.historia.configure(text="")
        self.ekran.configure(text=komunikat, font=("Segoe UI", 28, "bold"))

    def rownasie(self):
        if not self.wyrazenie:
            return
        try:
            wynik = self.oblicz(self.wyrazenie)
        except Exception as blad:
            self.pokaz_blad(blad)
            return
        self.historia.configure(text=self.wyrazenie + " =")
        self.wyrazenie = self.formatuj(wynik)
        self.po_wyniku = True

    def funkcja(self, znak):
        try:
            x = self.oblicz(self.wyrazenie or "0")
            stary = self.formatuj(x)
            if znak == "√":
                if x < 0:
                    raise ValueError
                wynik, opis = math.sqrt(x), f"√({stary})"
            elif znak == "x²":
                wynik, opis = x ** 2, f"({stary})²"
            elif znak == "1/x":
                wynik, opis = 1 / x, f"1/({stary})"
            elif znak == "%":
                wynik, opis = x / 100, f"{stary}%"
            else:  # ±
                wynik, opis = -x, ""
        except Exception as blad:
            self.pokaz_blad(blad)
            return
        if opis:
            self.historia.configure(text=opis + " =")
        self.wyrazenie = self.formatuj(wynik)
        self.po_wyniku = znak != "±"   # po ± można dalej dopisywać cyfry

    def klawisz(self, event):
        mapa = {"*": "×", "/": "÷", "-": "−", "+": "+", "^": "^", "=": "=",
                ",": ".", "Return": "=", "KP_Enter": "=",
                "BackSpace": "⌫", "Escape": "C", "Delete": "C"}
        znak = event.char
        if znak.isdigit() or znak == ".":
            self.nacisnij(znak)
        elif znak in mapa:
            self.nacisnij(mapa[znak])
        elif event.keysym in mapa:
            self.nacisnij(mapa[event.keysym])


if __name__ == "__main__":
    Kalkulator().mainloop()