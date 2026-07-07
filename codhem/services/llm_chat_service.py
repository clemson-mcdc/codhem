import json

from openai import OpenAI

from codhem.config.settings import get_settings
from codhem.services.dft_calculations_service import search_dft_calculations
from codhem.services.literature_data_service import search_literature_data
from codhem.services.llm_tools import TOOLS
from codhem.services.rhea_mpnn_service import run_rhea_mpnn_prediction


RESPONSE_POLICY = (
    "Answer only what the user asks by default and do not add extra inferred "
    "information unless the user explicitly asks for it. Keep the tone formal. "
    "Do not use emoji. Do not ask follow-up questions by default or add closing "
    "prompts such as asking whether the user wants more help."
)


def build_system_prompt(base_prompt: str):
    normalized_base_prompt = base_prompt.strip()
    if not normalized_base_prompt:
        normalized_base_prompt = "You are MCDC LLM."

    return f"{normalized_base_prompt} {RESPONSE_POLICY}"


def _execute_tool_call(tool_call):
    arguments = json.loads(tool_call.function.arguments or "{}")

    if tool_call.function.name == "search_literature_data":
        records = search_literature_data(
            query=arguments.get("query", {}),
            limit=arguments.get("limit", 5),
        )
        return json.dumps({"records": records}, default=str)

    if tool_call.function.name == "run_rhea_mpnn_prediction":
        prediction = run_rhea_mpnn_prediction(
            composition=arguments.get("composition", ""),
        )
        return json.dumps(prediction, default=str)

    if tool_call.function.name == "search_dft_calculations":
        records = search_dft_calculations(
            query=arguments.get("query", {}),
            limit=arguments.get("limit", 5),
        )
        return json.dumps({"records": records}, default=str)

    raise RuntimeError(f"Unsupported tool call: {tool_call.function.name}")


def generate_assistant_reply(messages):
    llm_settings = get_settings().llm
    client = OpenAI(
        api_key=llm_settings.api_key,
        base_url=llm_settings.base_url,
    )

    conversation = list(messages)

    for _ in range(4):
        response = client.chat.completions.create(
            model=llm_settings.model,
            messages=conversation,
            tools=TOOLS,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            reply = message.content
            if not reply:
                raise RuntimeError("The LLM service returned an empty response.")
            return reply

        conversation.append(message.model_dump(exclude_none=True))
        for tool_call in message.tool_calls:
            tool_result = _execute_tool_call(tool_call)
            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result,
                }
            )

    raise RuntimeError("The LLM exceeded the tool-calling limit.")
