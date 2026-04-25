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

- **Agentic loop**: The agent runs in a `while` loop, processing tool calls until the model returns a final text response with no more tool calls.
- **Structured output**: All findings are returned as a `FindingsReport` dataclass (severity, description, original snippet, suggested fix).
- **Single entry point**: `main.py` handles CLI argument parsing and prints the final report; all AI logic lives under `src/`.
