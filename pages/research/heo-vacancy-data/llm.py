from codhem.components.llm_chat import render_llm_chat
from codhem.services.llm_tools import SEARCH_HEO_VACANCY_DATA_TOOL


render_llm_chat(
    page_id="heo_vacancy_data",
    title="HEO Vacancy Data LLM",
    summary=(
        'Search HEO oxygen-vacancy records in plain language. Specify a system, vacancy '
        'position, neighbor elements, or thresholds for energy, Bader charge, volume, and '
        'displacement values. The assistant returns matching records with their source and '
        'query limit.'
    ),
    welcome_message=(
        "Welcome to the HEO Vacancy Data assistant. Ask a question about oxygen "
        "vacancy records to get started."
    ),
    page_instructions=(
        "This chat can search only the HEO oxygen-vacancy database. Do not claim "
        "to search CODHEM literature or DFT calculation records. Identify the HEO "
        "oxygen-vacancy database as the source of returned records."
    ),
    tools=[SEARCH_HEO_VACANCY_DATA_TOOL],
)
