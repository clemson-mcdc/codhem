from openai.types.chat import ChatCompletionToolUnionParam


def _range_property(description):
    return {
        "type": "object",
        "description": description,
        "properties": {
            "lt": {"type": "number", "description": "Less than."},
            "gt": {"type": "number", "description": "Greater than."},
            "eq": {"type": "number", "description": "Equal to."},
        },
        "additionalProperties": False,
    }


TOOLS: list[ChatCompletionToolUnionParam] = [
    {
        "type": "function",
        "function": {
            "name": "search_literature_data",
            "description": (
                "Fetch literature records that match a structured JSON query. "
                "Literature data is also referred to as CODHEM/COD'HEM data. "
                "Convert the user's natural-language request into a JSON object "
                "and only include the fields needed for that request. Supported "
                "external fields are composition, doi, record_id, phase, test_type, "
                "elements_present, density, elastic_modulus, sigma_at_23_c, "
                "sigma_at_1000_c, sigma_at_1200_c, shear_modulus, c11, "
                "fracture_toughness, and ductility. Numeric fields use an object "
                "with any needed lt, gt, or eq properties. Omit fields that the user did "
                "not ask for. Use limit to control how many matching records to return."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": (
                            "Structured lookup object built from the user's request. "
                            "Use optional fields composition, doi, record_id, phase, "
                            "test_type, elements_present, and numeric fields density, "
                            "elastic_modulus, sigma_at_23_c, sigma_at_1000_c, "
                            "sigma_at_1200_c, shear_modulus, c11, fracture_toughness, "
                            "and ductility. Numeric values use {lt: number, gt: number, "
                            "or eq: number} as needed. Example: {composition: AlCoCrFeNi, "
                            "phase: FCC, density: {gt: 7.5}}."
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
                                "items": {"type": "string"},
                            },
                            "density": _range_property("Density filter."),
                            "elastic_modulus": _range_property("Elastic modulus filter."),
                            "sigma_at_23_c": _range_property("Strength at 23 C filter."),
                            "sigma_at_1000_c": _range_property("Strength at 1000 C filter."),
                            "sigma_at_1200_c": _range_property("Strength at 1200 C filter."),
                            "shear_modulus": _range_property("Shear modulus filter."),
                            "c11": _range_property("C11 filter."),
                            "fracture_toughness": _range_property("Fracture toughness filter."),
                            "ductility": _range_property("Ductility filter."),
                        },
                        "additionalProperties": False,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matching records to return.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_dft_calculations",
            "description": (
                "Fetch DFT calculation records using a structured JSON query. "
                "Convert the user's natural-language request into a JSON object "
                "and only include the fields needed. Supported external fields are "
                "alloy, record_id, structure, has_elastic, elements_present, "
                "complexity, atom_count_min, atom_count_max, bulk_modulus_min, "
                "bulk_modulus_max, pugh_ratio_min, and pugh_ratio_max. Use this "
                "when the user asks about DFT calculation records, elastic "
                "availability, alloy coverage, or filtered DFT results. Use limit "
                "to control how many records to return."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": (
                            "Structured DFT lookup object built from the user's "
                            "request. Use optional fields alloy, record_id, "
                            "structure, has_elastic, elements_present, complexity, "
                            "atom_count_min, atom_count_max, bulk_modulus_min, "
                            "bulk_modulus_max, pugh_ratio_min, and pugh_ratio_max. "
                            "Example: {alloy: NbMoTaW, has_elastic: true, "
                            "bulk_modulus_min: 150}."
                        ),
                        "properties": {
                            "alloy": {
                                "type": "string",
                                "description": "Alloy name or composition requested by the user.",
                            },
                            "record_id": {
                                "type": "string",
                                "description": "DFT record identifier requested by the user.",
                            },
                            "structure": {
                                "type": "string",
                                "description": "Structure label requested by the user.",
                            },
                            "has_elastic": {
                                "type": "boolean",
                                "description": "Whether elastic tensor data must be available.",
                            },
                            "elements_present": {
                                "type": "array",
                                "description": "List of element symbols that must be present in the alloy.",
                                "items": {"type": "string"},
                            },
                            "complexity": {
                                "type": "string",
                                "description": "Requested alloy complexity label such as Binary, Ternary, or Quinary.",
                            },
                            "atom_count_min": {
                                "type": "number",
                                "description": "Minimum atom count requested by the user.",
                            },
                            "atom_count_max": {
                                "type": "number",
                                "description": "Maximum atom count requested by the user.",
                            },
                            "bulk_modulus_min": {
                                "type": "number",
                                "description": "Minimum bulk modulus requested by the user.",
                            },
                            "bulk_modulus_max": {
                                "type": "number",
                                "description": "Maximum bulk modulus requested by the user.",
                            },
                            "pugh_ratio_min": {
                                "type": "number",
                                "description": "Minimum Pugh ratio requested by the user.",
                            },
                            "pugh_ratio_max": {
                                "type": "number",
                                "description": "Maximum Pugh ratio requested by the user.",
                            },
                        },
                        "additionalProperties": False,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matching DFT records to return.",
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
