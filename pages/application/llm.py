from codhem.components.llm_chat import render_llm_chat
from codhem.services.llm_tools import SEARCH_LITERATURE_DATA_TOOL

render_llm_chat(
    page_id="literature",
    title="LLM",
    summary=(
        "Search the COD'HEM literature database in plain language. Specify a composition, "
        'elements, phase, DOI, or numeric property thresholds to find matching records. The '
        'assistant reports results with their database source and query limit.'
    ),
    welcome_message=(
        "Welcome to COD'HEM LLM. Ask a question about literature records in the "
        "materials database to get started."
    ),
    page_instructions=(
        "This chat can search only the CODHEM literature database. Do not claim "
        "to run DFT searches or model predictions. Identify the CODHEM literature "
        "database as the source of returned records."
    ),
    tools=[SEARCH_LITERATURE_DATA_TOOL],
)
