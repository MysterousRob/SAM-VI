SAM-CPU-SIM to lekki, wieloplatformowy symulator zwierzaka reagującego na użycie CPU, zaprojektowany do działania jako zawsze-widoczna nakładka pulpitu (always-on-top). Wykorzystuje backend w języku Rust do wydajnych obliczeń metryk CPU oraz frontend w Pythonie (z użyciem Pygame) do obsługi wizualnego zwierzaka i logiki interakcji.

## 🚀 Kluczowe funkcje

* **Nakładka pulpitu:** Działa płynnie na wierzchu innych aplikacji (obsługa Windows poprzez `win32gui`).
* **Rdzeń w Rust:** Wykorzystuje język Rust do krytycznych wydajnościowo symulacji CPU i obliczania metryk poprzez moduł `rust_core`.
* **Emocjonalny zwierzak:** Zwierzak o imieniu Clippy reaguje na metryki systemowe (temperatura CPU, pobór mocy itp.) i udziela głosowych odpowiedzi z użyciem syntezy mowy (`edge-tts`).
* **Interaktywne menu:** Menu sterowania umożliwiające zmianę motywów oraz podgląd szczegółowych metryk (otwierane prawym przyciskiem myszy).

## ⚙️ Wymagania wstępne

Aby **zbudować** i **uruchomić** aplikację, musisz mieć zainstalowane następujące oprogramowanie:

1. **Python:** Wersja 3.10 lub nowsza.
2. **Rust:** Pełny toolchain Rust (wraz z `cargo`) musi być zainstalowany. Instalacja przez [rustup](https://www.rust-lang.org/tools/install).
3. **Maturin:** Niezbędne narzędzie do budowania mostu Python–Rust.

## 🛠️ Konfiguracja i instalacja

Wykonaj poniższe kroki, aby skonfigurować środowisko i zbudować wymagane komponenty.

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/MysterousRob/SAM-VI.git
```

```cd SAM-CPU-SIM/CPU_PET_SIM/
```

### Konfiguracja wirtualnego środowiska Pythona

```
python -m venv venv
```

```
.\venv\Scripts\Activate
```

### 4. Budowanie backendu w Rust (rust_core)

```
maturin develop
```


## Uruchamianie aplikacji
```
python python_app/main.py
```

# Rozwiązywanie typowych problemów

* Ponieważ aplikacja łączy synchroniczną pętlę Pygame z asynchroniczną biblioteką syntezy mowy (edge-tts), mogą występować problemy z współbieżnością.

* Problem 1: RuntimeError: asyncio.run() cannot be called from a running event loop

* Ten błąd występuje, ponieważ główna pętla Pygame jest synchroniczna, natomiast wywołania edge-tts (w pliku Clippy_Personality.py) są asynchroniczne i używają asyncio.run(), którego nie wolno wielokrotnie wywoływać w tym samym wątku.

## Rozwiązanie:

* Aktualny kod rozwiązuje ten problem poprzez uruchamianie generowania mowy w oddzielnym, niezależnym wątku.

* Jest to realizowane przez funkcję opakowującą _run_speak_async_in_thread oraz użycie threading.Thread w pliku Clippy_Personality.py.

* Jeśli napotkasz ten błąd, upewnij się, że funkcja _run_speak_async_in_thread jest zdefiniowana poza klasą Personality oraz że metody say_for_mood i say_random_idle uruchamiają ją za pomocą threading.Thread.


### Problem 2: ImportError: cannot import name 'CPU' from 'rust_core'

*Ten błąd oznacza, że moduł Rust nie został poprawnie zbudowany lub zainstalowany w środowisku Pythona.

# Rozwiązanie:

* Upewnij się, że wirtualne środowisko jest aktywne (.\venv\Scripts\Activate).

* Przejdź do katalogu zawierającego plik Cargo.toml.

# Uruchom ponownie:
```
maturin develop
```

# Problem 3: AttributeError: 'ControlMenu' object has no attribute 'close'
```
linie 66–80

def close_control_menu():
    global menu, menu_open
    if menu_open:
        print("Control menu Closed")
        # menu.close()  # <-- TĘ LINIĘ NALEŻY USUNĄĆ LUB ZAKOMENTOWAĆ
        menu = None
        menu_open = False
```