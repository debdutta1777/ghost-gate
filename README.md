# Ghost-Gate: Zero-Trust PII Privacy Proxy

**Ghost-Gate** is a privacy layer for LLMs. It intercepts user prompts, detects sensitive data (Names, SSNs, Credit Cards), and replaces them with secure tokens before sending the data to the Cloud.

## Features
* **Zero-Trust:** PII never leaves your device.
* **Entities Supported:** Names, Phone Numbers, Emails, SSNs, Locations, Credit Cards.
* **Live Dashboard:** Watch the redaction happen in real-time.

## Setup
1. `pip install -r requirements.txt`
2. `python -m spacy download en_core_web_lg`
3. `python main.py`
