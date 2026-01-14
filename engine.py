from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from vault import Vault, generate_token

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
vault = Vault()

def protect_prompt(text: str):
    # Added GPE (Locations) and NRP (Credit Cards) to detection list
    results = analyzer.analyze(
        text=text, 
        entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN", "GPE", "NRP"], 
        language='en'
    )

    results.sort(key=lambda x: x.start, reverse=True)

    protected_text_list = list(text)
    mapping_snapshot = {}

    for result in results:
        start, end = result.start, result.end
        real_value = text[start:end]

        token = generate_token(result.entity_type)
        vault.store(token, real_value)
        mapping_snapshot[token] = real_value

        protected_text_list[start:end] = list(token)

    return "".join(protected_text_list), mapping_snapshot

def restore_response(text: str, current_mapping: dict):
    restored_text = text
    for token, original_value in current_mapping.items():
        restored_text = restored_text.replace(token, original_value)
    return restored_text