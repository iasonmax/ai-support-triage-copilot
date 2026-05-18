# AI Support Triage Co-Pilot

A local proof-of-concept AI co-pilot for IT service desk triage.

The app uses Retrieval-Augmented Generation over local markdown knowledge base
articles to generate safe, structured IT support guidance, draft ticket fields,
source citations, and escalation criteria.

## Purpose

This project demonstrates how a local AI assistant can help IT support analysts:

- Reduce repetitive triage work
- Improve ticket quality
- Follow approved troubleshooting procedures
- Identify escalation criteria
- Support common end-user IT issues

The tool is designed to assist support analysts, not replace them.

## Tech Stack

- Python
- Streamlit
- Ollama
- LangChain
- ChromaDB
- Markdown knowledge base files

## Safety Principles

The assistant is designed to:

- Avoid requesting passwords, MFA codes, recovery codes, or sensitive personal data
- Refuse requests to bypass security controls
- Avoid claiming to perform real IT actions
- Use approved knowledge base content for procedural guidance
- Escalate when the knowledge base does not contain enough information

## Architecture

```text
User
 |
 v
Streamlit UI
 |
 v
Safety Checker
 |
 v
RAG Retriever
 |
 +--> Markdown Knowledge Base
 |
 +--> Chroma Vector Store
 |
 v
Ollama Local LLM
 |
 v
Structured Triage Response
```

## Status

Proof of concept in development.

## Disclaimer

This is a portfolio/demo project using generic example knowledge base content.
It does not connect to real ITSM, identity, endpoint management, or company
systems. All AI-generated output should be reviewed by a human analyst.
