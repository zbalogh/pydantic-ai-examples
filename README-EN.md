# Pydantic AI Agent Demos

This project demonstrates two AI agents built with [Pydantic AI](https://ai.pydantic.dev/), each available in two versions:

| Agent | Standard version | Traced version | What it demonstrates |
|---|---|---|---|
| RAG agent | `rag-agent.py` | `rag-agent-with-trace.py` | Searching a local Markdown knowledge base (ChromaDB + a local embedding model) |
| Calculator agent | `calculator-agent.py` | `calculator-agent-with-trace.py` | Basic tool use: addition, subtraction, multiplication, and division |

- The **standard versions** print only the question and the final answer.
- The **traced versions** also show the communication with the LLM step by step: what is sent to the LLM, how it selects a tool, what the tool returns, and how many tokens the run used.


# Initialize the Project and Create Its Structure

```
uv init --app
```


# Expected Directory Structure

```
my-rag-project/
├── .venv/                          # Local virtual environment (managed automatically by uv)
├── chromadb/                       # ChromaDB vector database (populated by the RAG agent)
├── embedding-model/                # Local embedding model cache (downloaded on first run)
├── tudasbazis/                     # Markdown files for the knowledge base
├── .env                            # OpenAI API key (not tracked by version control)
├── pyproject.toml                  # Project configuration and dependencies
├── .python-version                 # Python version file
├── .gitignore                      # Files excluded from version control
├── rag-agent.py                    # RAG agent - standard version
├── rag-agent-with-trace.py         # RAG agent - with tracing
├── calculator-agent.py             # Calculator agent - standard version
├── calculator-agent-with-trace.py  # Calculator agent - with tracing
└── README.md                       # README file
```


# Add Project Dependencies

Instead of editing `pyproject.toml` manually, run the `uv add` command.
It downloads the packages into the local `.venv` environment and automatically adds them to `pyproject.toml`.
```
uv add chromadb langchain-text-splitters pydantic-ai openai sentence-transformers python-dotenv
```


# Manage API Keys (`.env` File)

To make the project portable, create a file named `.env` in the project root and add your OpenAI API key to it.
```
OPENAI_API_KEY=sk-proj-aBc123XyZ...

```


# Create Directories

Create these directories in the project:
```
mkdir embedding-model
mkdir chromadb
```


# RAG Knowledge Base Files

The knowledge base content is stored in Markdown files in the `tudasbazis` directory. It is an English-language operations manual for a fictional software product.

The fictional product is called Aster Communication Server (ACS), and the following Markdown files are included:
```
overview.md - product, components, and concepts
installation.md - installation and initial verification
configuration.md - settings and version-specific rules
backup-restore.md - backup and restore
troubleshooting.md - symptoms and diagnostics
release-notes.md - changes, upgrades, and rollbacks
```
The `ACS-README.md` file contains sample questions and expected answers. It is excluded from indexing so that the questions genuinely test retrieval from the six documentation files.


# Run the Agents

When running the code, use the `uv run` command. It automatically runs the script in the project's `.venv` environment.
Each agent prompts for a question on standard input, runs the agent, and then prints the answer.


## RAG Agent (Knowledge-Base Search)

At startup, the script reads the Markdown files in the `tudasbazis` directory, splits them into chunks, and updates the ChromaDB database
(it rewrites only changed chunks and removes chunks belonging to deleted files).
The agent searches the knowledge base using the `search_knowledge_base` tool and answers based on the retrieved documents, citing its sources.

```
uv run rag-agent.py
uv run rag-agent-with-trace.py
```

Example questions:
`What should I do before upgrading from 2.3 to 2.4?` or `What is the default API port in ACS 2.3 and 2.4?`


## Calculator Agent (Basic Tool Use)

The agent is provided with four tools (`add`, `subtract`, `multiply`, and `divide`) and must use them for every calculation step.
When a division by zero is attempted, the tool raises a `ModelRetry` exception. This gives the LLM feedback so it can explain the problem instead of crashing.

```
uv run calculator-agent.py
uv run calculator-agent-with-trace.py
```

Example questions:
`What is (12 + 8) * 3 / 4?` or `What is 10 divided by 0?`


# Tracing (the `*-with-trace.py` Versions)

The traced versions run the agent step by step using `agent.iter()` and print what is happening before each step:

| Output section | Meaning |
|---|---|
| `FELHASZNÁLÓI KÉRDÉS` | The input question |
| `KÉRÉS AZ LLM FELÉ` | The message parts sent to the LLM |
| `ESZKÖZÖK AZ LLM-KÉRÉSBEN` | The list of tools available to the LLM |
| `LLM VÁLASZA` | The LLM's decision: a tool call or a text response |
| `FUTÁS VÉGE` | Token usage, cost, and the number of requests and tool calls |

Message part types:

| Type | Meaning |
|---|---|
| `[system-prompt]` | The agent's instructions (system prompt) |
| `[user-prompt]` | The user's question |
| `[tool-call]` | The LLM selected a tool: its name, JSON arguments, and call ID |
| `[tool-return]` | The tool result sent back to the LLM |
| `[retry-prompt]` | An error message sent to the LLM (for example, division by zero) so it can correct its step |
| `[text]` | The LLM's text response |

Example output (calculator agent):
```
===== LLM VÁLASZA =====
  [tool-call] add({"a":12,"b":8})  id=call_UyjfZPRQvxSakEQhLMHblvUe
Eszköz hívás: összeadás 12.0 + 8.0

===== KÉRÉS AZ LLM FELÉ =====
  [tool-return] add -> 20.0  id=call_UyjfZPRQvxSakEQhLMHblvUe
```


## Settings

Tracing can be configured in the `BEÁLLÍTÁSOK` section at the beginning of the scripts:

| Variable | Default | Meaning |
|---|---|---|
| `TRACE_ENABLED` | `True` | Set to `False` to disable tracing and display only the final answer (the calculator's `Tool call` lines are still displayed) |
| `TRACE_MAX_CHARS` | `500` | Text longer than this (for example, retrieved chunks) is truncated in the output |


# Helpful Tips

- The banner displayed at startup by Pydantic AI can be disabled with the `PYDANTIC_AI_NO_BANNER` environment variable (PowerShell):
  ```
  $env:PYDANTIC_AI_NO_BANNER=1
  ```
- On its first run, the RAG agent downloads the local embedding model to the `embedding-model` directory. This may take some time.