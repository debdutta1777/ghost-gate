# 👻 Ghost-Gate: Zero-Trust Privacy Layer for LLMs
**"Chat with AI, keep your data."**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.5-orange?style=for-the-badge&logo=google&logoColor=white)
![Security](https://img.shields.io/badge/Security-Zero%20Trust-red?style=for-the-badge)

## 🔍 Overview
Ghost-Gate is a **Privacy Engineering Middleware** that sits between the user and public LLMs (like Google Gemini or OpenAI). It automatically intercepts prompts, detects sensitive entities (PII, Trade Secrets, Links), and redacts them **before** they leave the local device.

Once the AI responds, Ghost-Gate reconstructs the message, re-inserting the original data so the user sees a seamless response, while the cloud provider never sees the secrets.

## 🛡️ Key Features
* **Real-Time PII Redaction:** Automatically masks Names, Phone Numbers, Emails, and SSNs using Microsoft Presidio.
* **Custom Secret Defense:** Users can define "Deny Lists" for specific project code names (e.g., "Project Apollo").
* **Document RAG (Retrieval Augmented Generation):** Securely upload PDFs. The system extracts text, sanitizes it, and allows Q&A without leaking document secrets.
* **Link Scrubbing:** Detects and hides URLs (LinkedIn, GitHub) to prevent digital identity tracking.
* **Zero-Trust Architecture:** Data is sanitized *locally* on the client/server before any API call is made.

## 🏗️ Architecture
```mermaid
graph LR
    User[User Prompt] -->|Raw Text| Engine[Ghost-Gate Engine]
    Engine -->|Detects Secrets| Vault[(Local Vault)]
    Engine -->|Sanitized Prompt| Cloud[Google Gemini AI]
    Cloud -->|Generic Response| Engine
    Vault -->|Restores Secrets| Engine
    Engine -->|Final Response| User