## Project Purpose

SQL Code Critic — an agentic AI application that accepts SQL queries and stored procedures, analyzes them, and returns:
1. **Findings** — identified issues (performance, correctness, style, security)
2. **Improved code** — a rewritten version with explanations of each change

Built as a capstone for the Watspeed Agentic AI course using the Anthropic Claude API.

## Development Instructions

1. **Always write code in `.ipynb` files including description and readme** — use Jupyter notebooks for exploration and development.
2. **Install Python packages in a venv** — create an isolated environment and run notebooks within it:
  ```bash
  ```
3. **Add comments at the beginning** — every notebook should start with a description of its purpose and key steps.
4. **Build code with DRY and keep it simple** — avoid repetition and unnecessary complexity.
5. **Use functions and OOP as necessary** — apply these patterns only when they add clarity, not for their own sake.

6. **Write only requested code** — do not add related features, utilities, or improvements unless explicitly asked. Generate only what is needed for the specific input.
7. **Highlight breaking changes** — if your code modifies or impacts other files in the project, explicitly name the affected file(s) and ask for confirmation before making changes.

## Tech Stack

- **A2A SDK** — framework for building multi-agent systems; each node runs as a standalone HTTP agent service communicating via the A2A protocol
- **LangChain** — LLM integration layer (structured output, message formatting) used inside each agent node
- **Anthropic Claude API** — LLM backbone for SQL analysis
- **Google AI Studio** — alternative LLM provider (Gemma for routing)
- **Python** — primary language


## Commands

```bash
# activate the virtual env. On Windows: venv\Scripts\activate
source venv/bin/activate  

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run a single test
pytest tests/test_critic.py::test_function_name -v
```



### Key design patterns

- **A2A agent services**: Each node (router, schema-fetcher, analyzers, synthesizer) is an independent HTTP server with an `AgentExecutor` that handles tasks via the A2A protocol.
- **LangChain for LLM calls**: Each executor uses `with_structured_output()` to get typed Pydantic responses from the LLM — no raw JSON parsing.
- **Structured output**: All findings are returned as a `FindingsReport` dataclass (severity, description, original snippet, suggested fix).
- **Single entry point**: `main.py` handles CLI argument parsing and prints the final report; all AI logic lives under `src/`.
