# codhem

Streamlit project scaffold for a scientific data interface with filtering, plotting, and server-side ML workflows.

Run the app with:

uv run streamlit run main.py

## Server-local deploy reference

If production is only reachable inside a VPN, use the root-level `update.sh` script and the sample user service in `codhem.service`.

The service can run `update.sh` in `ExecStartPre`, so a single `systemctl restart codhem.service` can both update code and restart Streamlit.

The update script:

- fetches the target branch from `origin`
- resets the working tree to `origin/main`
- runs `uv sync --locked`
