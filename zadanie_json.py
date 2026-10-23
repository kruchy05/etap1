import json

zadania = [
    {"tytul": "Nauczyć się venv", "zrobione": True},
    {"tytul": "Zapisać JSON", "zrobione": False},
    {"tytul": "Pobrać dane z GitHuba", "zrobione": False},
]

# ZAPIS: "w" = write (nadpisuje plik)
with open("zadania.json", "w", encoding="utf-8") as plik:
    json.dump(zadania, plik, ensure_ascii=False, indent=2)

print("Zapisano do zadania.json")

# ODCZYT: "r" = read
with open("zadania.json", "r", encoding="utf-8") as plik:
    wczytane = json.load(plik)

for z in wczytane:
    znak = "✔" if z["zrobione"] else "✘"
    print(znak, z["tytul"])

print("Te same dane?", zadania == wczytane)