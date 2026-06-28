# Złap prezent — Julia i Norbert

Gra weselna w Pythonie/Pygame.

## Opis

Gracz steruje Julią i Norbertem i łapie spadające weselne prezenty.

Do zdobycia punktów są:
- obrączki,
- bukiety,
- tort,
- cytryny,
- serca.

Przeszkody:
- chmurka,
- stłuczony kieliszek.

Gra przyspiesza z czasem:
- przedmioty spadają coraz szybciej,
- przedmioty pojawiają się coraz częściej.

## Pliki graficzne

W folderze `assets`:

- `background.png` — tło gry,
- `player.png` — Julia i Norbert,
- `ring.png` — obrączki,
- `bouquet.png` — bukiet,
- `cake.png` — tort,
- `lemon.png` — cytryna,
- `heart.png` — serce,
- `cloud.png` — chmurka,
- `bad_glass.png` — stłuczony kieliszek.

## Uruchomienie w PyCharm

1. Otwórz cały folder projektu w PyCharm.
2. W terminalu wpisz:

```bash
pip install -r requirements.txt
python main.py
```

albo kliknij prawym przyciskiem na `main.py` i wybierz `Run main`.

## Sterowanie

- myszka,
- dotyk,
- strzałki,
- A / D.

## Publikacja online

Projekt zawiera gotowy workflow GitHub Pages przez `pygbag`.
W repozytorium GitHub ustaw:

`Settings -> Pages -> Build and deployment -> GitHub Actions`