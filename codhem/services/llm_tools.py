from openai.types.chat import ChatCompletionToolUnionParam


TOOLS: list[ChatCompletionToolUnionParam] = [
    {
        "type": "function",
        "function": {
            "name": "search_literature_data",
            "description": (
                "Fetch literature records that match a structured JSON query. "
                "Convert the user's natural-language request into a JSON object "
                "and only include the fields needed for that request. Supported "
                "external fields are composition, doi, record_id, phase, test_type, "
                "elements_present, density_min, density_max, elastic_modulus_min, "
                "and elastic_modulus_max. Omit fields that the user did not ask "
                "for. Use limit "
                "to control how many matching records to return."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": (
                            "Structured lookup object built from the user's request. "
                            "Use optional fields composition, doi, record_id, phase, test_type, "
                            "elements_present, density_min, density_max, "
                            "elastic_modulus_min, and elastic_modulus_max. Example: "
                            "{composition: AlCoCrFeNi, phase: FCC, density_min: 7.5}."
                        ),
                        "properties": {
                            "composition": {
                                "type": "string",
                                "description": "Material composition or alloy name requested by the user.",
                            },
                            "doi": {
                                "type": "string",
                                "description": "DOI value requested by the user.",
                            },
                            "record_id": {
                                "type": "string",
                                "description": "Record identifier requested by the user.",
                            },
                            "phase": {
                                "type": "string",
                                "description": "Phase label requested by the user.",
                            },
                            "test_type": {
                                "type": "string",
                                "description": "Test category requested by the user.",
                            },
                            "elements_present": {
                                "type": "array",
                                "description": "List of element symbols that must be present in the material.",
                                "items": {
                                    "type": "string"
                                },
                            },
                            "density_min": {
                                "type": "number",
                                "description": "Minimum density requested by the user.",
                            },
                            "density_max": {
                                "type": "number",
                                "description": "Maximum density requested by the user.",
                            },
                            "elastic_modulus_min": {
                                "type": "number",
                                "description": "Minimum elastic modulus requested by the user.",
                            },
                            "elastic_modulus_max": {
                                "type": "number",
                                "description": "Maximum elastic modulus requested by the user.",
                            },
                        },
                        "additionalProperties": False,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matching records to return.",
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_rhea_mpnn_prediction",
            "description": (
                "Run the RHEA-DOS-E predictor for a composition provided by the user. "
                "Use this when the user asks for predicted DOS at the Fermi level, "
                "predicted Young's modulus, or both for a refractory high-entropy alloy. "
                "Convert the user's natural-language request into the required composition string. "
                "Pass the composition in atomic-percent style such as Cr20Mo30V10Hf40."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "composition": {
                        "type": "string",
                        "description": "Alloy composition extracted from the user's request, formatted like Cr20Mo30V10Hf40.",
                    }
                },
                "required": ["composition"],
            },
        },
    },
]
