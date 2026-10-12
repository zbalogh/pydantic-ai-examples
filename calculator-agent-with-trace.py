# Python beépített modulok importálása
import asyncio
import json

# Pydantic AI agent, hibakezelés és OpenAI modell importálása
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.settings import ModelSettings

# Az LLM-mel váltott üzenetek részeinek (part) típusai a nyomkövetéshez
from pydantic_ai.messages import (
    RetryPromptPart,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)

# Környezeti változók betöltése a .env fájlból (OPENAI_API_KEY)
from dotenv import load_dotenv
load_dotenv()


# --- BEÁLLÍTÁSOK ---
MODEL_NAME = "gpt-4o-mini"

# Az LLM kommunikáció nyomkövetésének (és az eszközhívások kiírásának) ki/be kapcsolása
TRACE_ENABLED = True
TRACE_MAX_CHARS = 500


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
    if TRACE_ENABLED:
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
    if TRACE_ENABLED:
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
    if TRACE_ENABLED:
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
    if TRACE_ENABLED:
        print(f"Eszköz hívás: osztás {a} / {b}")
    if b == 0:
        raise ModelRetry("Nullával nem lehet osztani. Jelezd ezt a felhasználónak.")
    return a / b


# --- LLM KOMMUNIKÁCIÓ NYOMKÖVETÉSE ---
# Hosszú szövegek levágása, hogy a kimenet áttekinthető maradjon
def shorten(text: str) -> str:
    return text if len(text) <= TRACE_MAX_CHARS else text[:TRACE_MAX_CHARS] + " ..."


# Egy üzenetrész (part) olvasható, egysoros leírása a típusa alapján
def describe_part(part) -> str:
    if isinstance(part, SystemPromptPart):
        return f"[system-prompt] {shorten(part.content)}"
    if isinstance(part, UserPromptPart):
        return f"[user-prompt] {shorten(str(part.content))}"
    if isinstance(part, ToolCallPart):
        return f"[tool-call] {part.tool_name}({part.args_as_json_str()})  id={part.tool_call_id}"
    if isinstance(part, ToolReturnPart):
        return f"[tool-return] {part.tool_name} -> {shorten(str(part.content))}  id={part.tool_call_id}"
    if isinstance(part, RetryPromptPart):
        return f"[retry-prompt] {part.tool_name}: {shorten(part.model_response())}"
    if isinstance(part, TextPart):
        return f"[text] {shorten(part.content)}"
    return f"[{part.part_kind}] {shorten(repr(part))}"


def print_parts(title: str, parts) -> None:
    print(f"\n===== {title} =====")
    for part in parts:
        print(f"  {describe_part(part)}")


def print_model_request(node) -> None:
    print_parts("KÉRÉS AZ LLM FELÉ", node.request.parts)
    request_context = node.last_request_context
    if request_context is None:
        print("  Az eszközlista nem érhető el.")
        return

    tools = request_context.model_request_parameters.function_tools
    print("\n===== ESZKÖZÖK AZ LLM-KÉRÉSBEN =====")
    if not tools:
        print("  (nincs)")
        return
    for tool in tools:
        description = f": {shorten(tool.description)}" if tool.description else ""
        schema = json.dumps(tool.parameters_json_schema, ensure_ascii=False)
        print(f"  {tool.name}{description}")
        print(f"    paraméterek: {schema}")


# Az agent futtatása lépésenként: minden gráf csomópontot (node) kiírunk, mielőtt végrehajtódik.
# ModelRequestNode = kérés az LLM felé, CallToolsNode = LLM válasza (eszközválasztás vagy szöveg).
async def run_agent_with_trace(question: str) -> str:
    output = ""
    pending_request_node = None
    async with agent.iter(question) as run:
        async for node in run:
            if pending_request_node is not None:
                print_model_request(pending_request_node)
                pending_request_node = None
            if Agent.is_user_prompt_node(node):
                print(f"\n===== FELHASZNÁLÓI KÉRDÉS =====\n  {node.user_prompt}")
            elif Agent.is_model_request_node(node):
                pending_request_node = node
            elif Agent.is_call_tools_node(node):
                print_parts("LLM VÁLASZA", node.model_response.parts)
            elif Agent.is_end_node(node):
                output = node.data.output
                print("\n===== FUTÁS VÉGE =====")
        print(f"  Token használat: {run.usage}")
    return output


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

    # Az AI Agent futtatása, bekapcsolt TRACE_ENABLED esetén lépésenkénti nyomkövetéssel.
    # A kérdés átadása az agentnek, amely a megfelelő eszközöket használja a számítás elvégzéséhez.
    if TRACE_ENABLED:
        output = asyncio.run(run_agent_with_trace(question))
    else:
        output = asyncio.run(agent.run(question)).output

    # Az AI Agent kimenetének (válaszának) kiiratása
    print("\n===== VÁLASZ =====\n")
    print(output)
    print("\n")


# A main függvény meghívása a script futtatásakor
if __name__ == "__main__":
    main()
