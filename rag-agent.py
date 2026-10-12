# Python beépített modulok importálása
import hashlib
from pathlib import Path
from dataclasses import dataclass
import chromadb

# Beimportáljuk a helyi SentenceTransformer Embedding funkciót
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# A markdown fájlok darabolásához használjuk a MarkdownTextSplitter-t.
from langchain_text_splitters import MarkdownTextSplitter

# Pydantic AI agent és OpenAI modell importálása
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

# Környezeti változók betöltése a .env fájlból
from dotenv import load_dotenv
load_dotenv()


# --- BEÁLLÍTÁSOK ---
DOCS_DIR = "./tudasbazis"
CHROMA_PATH = "./chromadb"
COLLECTION_NAME = "tudasbazis_collection"


# --- HELYI ERŐS EMBEDDING MODELL KONFIGURÁCIÓJA ---
# A modell magyarul is használható; alapértelmezett maximális bemenete 128 token.
# Ez a beállítás lehetővé teszi, hogy a ChromaDB a helyi embedding modellt használja a dokumentumok vektorizálásához.
local_embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    cache_folder="./embedding-model"
)


# --- REKURZÍV BEOLVASÁS NAGYOBB CHUNK MÉRETTEL ---
# A Markdown fájlok beolvasása és chunkokra bontása a tudásbázis frissítéséhez.
# Ez a funkció a megadott könyvtár összes Markdown fájlját beolvassa,
# chunkokra bontja, és frissíti a ChromaDB gyűjteményt.
def ingest_markdown_directory(directory_path: str, collection: chromadb.Collection):
    """A Markdown fájlok chunkjait frissíti, az elavultakat eltávolítja."""
    root = Path(directory_path)
    if not root.is_dir():
        raise FileNotFoundError(f"A tudásbázis könyvtára nem létezik: {root}")

    splitter = MarkdownTextSplitter(chunk_size=400, chunk_overlap=50)
    documents = []
    metadatas = []
    ids = []

    for file_path in sorted(root.rglob("*.md")):
        try:
            content = file_path.read_text(encoding="utf-8")
            chunks = splitter.split_text(content)
            source = file_path.relative_to(root).as_posix()
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "source": str(file_path),
                    "filename": file_path.name,
                    "chunk_index": i
                })
                ids.append(f"md_{hashlib.sha256(source.encode('utf-8')).hexdigest()}_{i}")
        except (OSError, UnicodeError) as exc:
            raise RuntimeError(f"Nem sikerült beolvasni: {file_path}") from exc

    existing = collection.get(include=["documents", "metadatas"])
    previous = dict(zip(existing["ids"], zip(existing["documents"], existing["metadatas"])))
    changed = [(key, doc, meta) for key, doc, meta in zip(ids, documents, metadatas)
               if previous.get(key) != (doc, meta)]
    for start in range(0, len(changed), 100):
        batch = changed[start:start + 100]
        collection.upsert(ids=[row[0] for row in batch],
                          documents=[row[1] for row in batch],
                          metadatas=[row[2] for row in batch])

    stale = set(previous) - set(ids)
    stale_ids = sorted(stale)
    for start in range(0, len(stale_ids), 100):
        collection.delete(ids=stale_ids[start:start + 100])
    print(f"Indexelés: {len(documents)} chunk, {len(changed)} frissítve, {len(stale)} eltávolítva.")


# ChromaDB inicializálása a SAJÁT embedding függvénnyel
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Fontos: A get_or_create_collection-nek át kell adni az embedding_function-t!
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=local_embedding_function
)


# --- PYDANTIC AI AGENT ---
# Ez csak egy olyan adatleíró osztály, amely az agent függőségeit tartalmazza.
# Később ezt használjuk arra, hogy az agent számára elérhetővé tegyük a ChromaDB kollekciót.
@dataclass
class AgentDependencies:
    chroma_collection: chromadb.Collection


# OpenAI modell inicializálása
model = OpenAIChatModel('gpt-4o-mini')

# Agent inicializálása
agent = Agent(
    model=model,
    deps_type=AgentDependencies,
    system_prompt=(
        "Te egy belső vállalati asszisztens vagy. "
        "Mindig használd a 'search_knowledge_base' eszközt a kereséshez. "
        "Csak a megtalált dokumentumok alapján válaszolj, és nevezd meg a forrásokat. "
        "Ha nincs releváns találat, jelezd, hogy nem tudsz választ adni."
    )
)

# Agent eszközök definiálása
# Agent Tool a tudázbázisban történő kereséshez (RAG).
# Ez az eszköz lehetővé teszi az AI agent számára, hogy a helyi tudásbázisban keressen.
# A search_knowledge_base eszköz aszinkron függvényként van definiálva,
# és a RunContext segítségével fér hozzá az agent függőségeihez.
@agent.tool
async def search_knowledge_base(ctx: RunContext[AgentDependencies], query: str) -> str:
    """Keresés a nagyméretű kontextust támogató helyi tudásbázisban.
    
    Args:
        query: Keresési kifejezés.
    """
    
    # A ChromaDB a háttérben a korábban  már beállított embedding modellel alakítja át a query-t is.
    # Fontos, hogy ugyanaz a modell-t használja a keresésnél, mint az indexálásnál használt a tudázbázis fájlokhoz.
    results = ctx.deps.chroma_collection.query(
        query_texts=[query],
        n_results=6,
        include=["documents", "metadatas"]
    )

    formatted_results = []
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    for doc, meta in zip(docs, metas):
        if doc and meta:
            formatted_results.append(f"Forrás: {meta['source']}\nTartalom:\n{doc}")

    return "\n\n---\n\n".join(formatted_results) if formatted_results else "Nincs találat."


#
# ---------------------------------- MAIN FUNCTION -------------------------------------
# A main függvény bekéri a kérdést a standard input-on és futtatja az AI agentet.
# --------------------------------------------------------------------------------------
#
def main():
    print("\nIndexelés folyamatban...\n")
    # a tudásbázis MarkDown fájlok darabolása és beillesztése a ChromaDB adatbázisba
    ingest_markdown_directory(DOCS_DIR, collection)
    print("\nIndexelés befejezve.\n")
    
    # kérdés beolvasása a standard input-on
    try:
        question = input("Kérdés: ").strip()
    except EOFError:
        return
    if not question:
        print("Nem adtál meg kérdést.")
        return
    
    print("\n")
    # Az agent futtatása szinkron módon a megadott kérdéssel.
    # Átadásra kerül a kérdés és az agent függőségei: a ChromaDB kollekció.
    # Ezt használja a tudásbázisban történő kereséshez.
    result = agent.run_sync(question, deps=AgentDependencies(chroma_collection=collection))
    print("\n")
    
    # Az AI Agent kimenetének (válaszának) kiiratása
    print(result.output)
    print("\n")


# A main függvény meghívása a script futtatásakor
if __name__ == "__main__":
    main()
