from codhem.components.llm_chat import render_llm_chat
from codhem.services.llm_tools import RUN_RHEA_MPNN_PREDICTION_TOOL


render_llm_chat(
    page_id="ml_models",
    title="ML Models LLM",
    summary=(
        'Request RHEA-DOS-E predictions in plain language by supplying an alloy composition '
        'in atomic percent, such as Cr20Mo30V10Hf40. The assistant runs the predictor and '
        "reports electronic density of states at the Fermi level and Young's modulus."
    ),
    welcome_message=(
        "Welcome to the ML Models assistant. Ask for a RHEA-DOS-E prediction by "
        "providing a refractory high-entropy alloy composition."
    ),
    page_instructions=(
        "This chat can only run the RHEA-DOS-E predictor. Do not claim to search "
        "CODHEM literature, DFT calculation, or HEO vacancy records. Identify "
        "the RHEA MPNN model as the source of predictions."
    ),
    tools=[RUN_RHEA_MPNN_PREDICTION_TOOL],
)
