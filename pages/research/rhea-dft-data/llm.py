from codhem.components.llm_chat import render_llm_chat
from codhem.services.llm_tools import SEARCH_DFT_CALCULATIONS_TOOL


render_llm_chat(
    page_id="rhea_dft_data",
    title="RHEA DFT Data LLM",
    summary=(
        'Search RHEA DFT calculation records in plain language. Ask for alloys, structures, '
        'element combinations, elastic-data availability, or atom-count, bulk-modulus, and '
        'Pugh-ratio ranges. The assistant returns matching records with their source and '
        'query limit.'
    ),
    welcome_message=(
        "Welcome to the RHEA DFT Data assistant. Ask about alloys, structures, "
        "elastic properties, or available calculations."
    ),
    page_instructions=(
        "This chat can search only the DFT calculation database. Do not claim to "
        "search CODHEM literature records or run model predictions. Identify the "
        "DFT calculation database as the source of returned records."
    ),
    tools=[SEARCH_DFT_CALCULATIONS_TOOL],
)
