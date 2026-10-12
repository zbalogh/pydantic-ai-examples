# Pydantic AI agent demók

A projekt két, [Pydantic AI](https://ai.pydantic.dev/) alapú AI agentet mutat be, mindkettőt két változatban:

| Agent | Egyszerű változat | Nyomkövetéses változat | Mit mutat be |
|---|---|---|---|
| RAG agent | `rag-agent.py` | `rag-agent-with-trace.py` | Keresés egy helyi Markdown tudásbázisban (ChromaDB + helyi embedding modell) |
| Számológép agent | `calculator-agent.py` | `calculator-agent-with-trace.py` | Egyszerű eszközhasználat: összeadás, kivonás, szorzás, osztás |

- Az **egyszerű változatok** csak a kérdést és a végső választ írják ki.
- A **nyomkövetéses változatok** lépésenként megmutatják az LLM-mel folytatott kommunikációt is: mi megy az LLM felé, hogyan választ eszközt, mit ad vissza az eszköz, és mennyi tokent használt a futás.


# Projekt inicializálása és a mappa felépítése

```
uv init --app
```


# A mappaszerkezet így fog kinézni

```
my-rag-project/
├── .venv/                          # A helyi virtuális környezet (az uv automatikusan kezeli)
├── chromadb/                       # A ChromaDB vektoradatbázis (a RAG agent tölti fel)
├── embedding-model/                # A helyi embedding modell gyorsítótára (első futáskor töltődik le)
├── tudasbazis/                     # A tudásbázis Markdown fájljai
├── .env                            # OpenAI API kulcs (nem kerül verziókövetésbe)
├── pyproject.toml                  # A projekt konfigurációja és függőségei
├── .python-version                 # Python verzió fájl
├── .gitignore                      # Git verziókövetésből kizárt fájlok
├── rag-agent.py                    # RAG agent – egyszerű változat
├── rag-agent-with-trace.py         # RAG agent – nyomkövetéssel
├── calculator-agent.py             # Számológép agent – egyszerű változat
├── calculator-agent-with-trace.py  # Számológép agent – nyomkövetéssel
└── README.md                       # README fájl
```


# Függőségek hozzáadása a projekthez

Ahelyett, hogy manuálisan szerkesztenéd a pyproject.toml fájlt, futtasd az uv add parancsot.
Ez letölti a csomagokat a helyi .venv környezetbe, és automatikusan beírja őket a pyproject.toml fájlba.
```
uv add chromadb langchain-text-splitters pydantic-ai openai sentence-transformers python-dotenv
```


# Az API kulcsok kezelése (.env fájl)

Hogy a projekt hordozható legyen, hozz létre egy .env nevű fájlt a projekt gyökerében, és add meg az OpenAI API kulcsodat.
```
OPENAI_API_KEY=sk-proj-aBc123XyZ...

```


# Könyvtárak létrehozása

Hozd létre ezeket a könyvtárakat a project-ben:
```
mkdir embedding-model
mkdir chromadb
```


# RAG tudásbázis fájlok

A tudásbázis anyaga Markdown fájlokban találhatók a `tudasbazis` könyvtárban. Ez egy fiktív szoftvertermék angol nyelvű üzemeltetési kézikönyve.

A fiktív szoftvertermék neve Aster Communication Server (ACS), és ezek a Markdown fájlok tartoznak hozzá:
```
overview.md – termék, komponensek és fogalmak
installation.md – telepítés és kezdeti ellenőrzés
configuration.md – beállítások és verziófüggő szabályok
backup-restore.md – mentés és visszaállítás
troubleshooting.md – hibajelenségek és diagnosztika
release-notes.md – változások, frissítés és visszaállás
```
Az `ACS-README.md` fájl mintakérdéseket és elvárt válaszokat ad. Ezt kihagyjuk az indexelésből, hogy a kérdések valóban a hat dokumentum visszakeresését teszteljék.


# Az agentek futtatása

Amikor futtatni szeretnéd a kódot, az uv run parancsot használd. Ez automatikusan a projekt .venv környezetében fogja végrehajtani a szkriptet.
Minden agent egy kérdést kér be a standard bemeneten, lefuttatja az agentet, majd kiírja a választ.


## RAG agent (tudásbázis alapú keresés)

Indításkor a szkript beolvassa és chunkokra bontja a `tudasbazis` könyvtár Markdown fájljait, majd frissíti a ChromaDB adatbázist
(csak a megváltozott chunkokat írja újra, a törölt fájlokhoz tartozókat eltávolítja).
Az agent a `search_knowledge_base` eszközzel keres a tudásbázisban, és a talált dokumentumok alapján, forrásmegjelöléssel válaszol.

```
uv run rag-agent.py
uv run rag-agent-with-trace.py
```

Példa kérdések:
`What should I do before upgrading from 2.3 to 2.4?` vagy `What is the default API port in ACS 2.3 and 2.4?`


## Számológép agent (egyszerű eszközhasználat)

Az agent négy eszközt (`add`, `subtract`, `multiply`, `divide`) kap, és minden számítási lépéshez ezeket kell használnia.
Nullával való osztáskor az eszköz `ModelRetry` hibát dob, így az LLM visszajelzést kap, és összeomlás helyett elmagyarázza a problémát.

```
uv run calculator-agent.py
uv run calculator-agent-with-trace.py
```

Példa kérdések:
`Mennyi (12 + 8) * 3 / 4?` vagy `Mennyi 10 osztva 0-val?`


# Nyomkövetés (a `*-with-trace.py` változatok)

A nyomkövetéses változatok az `agent.iter()` segítségével lépésenként futtatják az agentet, és minden lépés előtt kiírják, mi történik:

| Kiírt blokk | Jelentése |
|---|---|
| `FELHASZNÁLÓI KÉRDÉS` | A bemeneti kérdés |
| `KÉRÉS AZ LLM FELÉ` | Az LLM-nek küldött üzenetrészek |
| `ESZKÖZÖK AZ LLM-KÉRÉSBEN` | Az LLM-nek küldött elérhető eszközök listája |
| `LLM VÁLASZA` | Az LLM döntése: eszközhívás vagy szöveges válasz |
| `FUTÁS VÉGE` | Token használat, költség, kérések és eszközhívások száma |

Az üzenetrészek (part) típusai:

| Típus | Jelentése |
|---|---|
| `[system-prompt]` | Az agent utasításai (system prompt) |
| `[user-prompt]` | A felhasználó kérdése |
| `[tool-call]` | Az LLM egy eszközt választott: az eszköz neve, JSON argumentumai és a hívás azonosítója |
| `[tool-return]` | Az eszköz eredménye, amelyet visszaküldünk az LLM-nek |
| `[retry-prompt]` | Hibaüzenet az LLM felé (pl. nullával osztás), hogy javítsa a lépését |
| `[text]` | Az LLM szöveges válasza |

Példa kimenet (számológép agent):
```
===== LLM VÁLASZA =====
  [tool-call] add({"a":12,"b":8})  id=call_UyjfZPRQvxSakEQhLMHblvUe
Eszköz hívás: összeadás 12.0 + 8.0

===== KÉRÉS AZ LLM FELÉ =====
  [tool-return] add -> 20.0  id=call_UyjfZPRQvxSakEQhLMHblvUe
```


## Beállítások

A nyomkövetés a szkriptek elején, a `BEÁLLÍTÁSOK` szakaszban szabályozható:

| Változó | Alapérték | Jelentése |
|---|---|---|
| `TRACE_ENABLED` | `True` | `False` esetén a nyomkövetés kikapcsol, és csak a végső válasz jelenik meg (a számológépnél az „Eszköz hívás” sorok is) |
| `TRACE_MAX_CHARS` | `500` | Ennél hosszabb szövegek (pl. a talált chunkok) levágásra kerülnek a kiírásban |


# Hasznos tippek

- A Pydantic AI indításkor kiírt bannere kikapcsolható a `PYDANTIC_AI_NO_BANNER` környezeti változóval (PowerShell):
  ```
  $env:PYDANTIC_AI_NO_BANNER=1
  ```
- A RAG agent első futásakor a helyi embedding modell letöltődik az `embedding-model` könyvtárba, ez hosszabb ideig tarthat.
