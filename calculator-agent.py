# Pydantic AI agent, hibakezelés és OpenAI modell importálása
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.settings import ModelSettings

# Környezeti változók betöltése a .env fájlból (OPENAI_API_KEY)
from dotenv import load_dotenv
load_dotenv()


# --- BEÁLLÍTÁSOK ---
MODEL_NAME = "gpt-4o-mini"


# --- PYDANTIC AI AGENT ---
# OpenAI modell inicializálása
model = OpenAIChatModel(MODEL_NAME)

# Agent inicializálása; nincs szükség függőségekre (deps_type), mert eszközök önállóak,
# nem használnak RunContext-et a külső függőségek eléréséhez.
agent = Agent(
    model=model,
    # Párhuzamos hívásnál az LLM a még ki nem számolt részeredményeket találgatná.
    # Ezért letiltjuk a párhuzamos eszközhívásokat, így az LLM mindig az előző lépés eredményét használja a következőhöz.
    model_settings = ModelSettings(parallel_tool_calls=False),
    system_prompt=(
        "Te egy számológép asszisztens vagy. "
        "Minden számítási lépéshez kötelezően használd a rendelkezésre álló eszközöket "
        "(add, subtract, multiply, divide), fejben ne számolj. "
        "Egyszerre csak egy eszközt hívj, és a következő lépésben az előző eszköz eredményét használd. "
        "Magyarul válaszolj, és röviden mutasd be a számítás lépéseit."
    )
)


# --- AGENT ESZKÖZÖK ---
# A tool_plain dekorátor olyan eszközt regisztrál, amelynek nincs szüksége RunContext-re.
# Azaz olyan eszközök, amelyeknek nincs függősége a külső erőforrásokra.
# A docstring az LLM számára az eszköz leírásaként szolgál.

# Összeadás eszköz
@agent.tool_plain
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: First number.
        b: Second number.
    """
    print(f"Eszköz hívás: összeadás {a} + {b}")
    return a + b


# Kivonás eszköz
@agent.tool_plain
def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first.

    Args:
        a: Minuend.
        b: Subtrahend.
    """
    print(f"Eszköz hívás: kivonás {a} - {b}")
    return a - b


# Szorzás eszköz
@agent.tool_plain
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: First factor.
        b: Second factor.
    """
    print(f"Eszköz hívás: szorzás {a} * {b}")
    return a * b


# Osztás eszköz; nullával osztáskor a ModelRetry visszajelzést küld az LLM-nek összeomlás helyett
@agent.tool_plain
def divide(a: float, b: float) -> float:
    """Divide the first number by the second.

    Args:
        a: Dividend.
        b: Divisor, must not be zero.
    """
    print(f"Eszköz hívás: osztás {a} / {b}")
    if b == 0:
        raise ModelRetry("Nullával nem lehet osztani. Jelezd ezt a felhasználónak.")
    return a / b


#
# ---------------------------------- MAIN FUNCTION -------------------------------------
# A main függvény bekéri a kérdést a standard input-on és futtatja az AI agentet.
# --------------------------------------------------------------------------------------
#
def main():
    print("\nSzámológép agent (összeadás, kivonás, szorzás, osztás)\n")

    # Kérdés beolvasása a standard input-on
    try:
        question = input("Kérdés: ").strip()
    except EOFError:
        return
    if not question:
        print("Nem adtál meg kérdést.")
        return

    # Az AI Agent futtatása szinkron módon a megadott kérdéssel.
    # A kérdés átadása az agentnek, amely a megfelelő eszközöket használja a számítás elvégzéséhez.
    print("\n")
    result = agent.run_sync(question)
    print("\n")

    # Az AI Agent kimenetének (válaszának) kiiratása
    print(result.output)
    print("\n")


# A main függvény meghívása a script futtatásakor
if __name__ == "__main__":
    main()
