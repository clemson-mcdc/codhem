SCIENTIFIC_DATA_QUERY = """
SELECT dataset_id, material, temperature, signal, instrument
FROM scientific_data
WHERE (:material = 'All' OR material = :material)
  AND (:instrument = 'All' OR instrument = :instrument)
  AND temperature BETWEEN :min_temperature AND :max_temperature
"""
