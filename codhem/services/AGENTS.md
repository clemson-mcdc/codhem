Read `../AGENTS.md` and follow it.

Tool definitions for MCDC LLM live in `llm_tools.py`.

When adding a new tool:
- Keep the tool description model-facing, concise, and non-sensitive.
- Expose user-facing query fields only; do not expose internal Mongo field paths.
- Prefer a small service function in this directory that accepts a structured `query` dict plus `limit`.
- Validate or constrain optional fields in the service layer, not only in the tool description.
- Keep result payloads compact and summary-oriented so chat responses stay readable.
- Update `llm_chat_service.py` dispatch when a new tool is added.
