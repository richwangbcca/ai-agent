# Event Planner Bot

EventBot is a Discord bot that helps groups plan in-person meetups by suggesting venues via the Google Maps API and creating Google Calendar events. It uses the Mistral API for lightweight conversational planning support.

This was built as the final project for Stanford's CS153: Infrastructure at Scale. This project achieves basic functionality under real-world constraints but does not meet production-scale design expectations. 

<p align="center"><img width="530" height="440" alt="Screenshot of EventBot" src="https://github.com/user-attachments/assets/3111931d-08e3-47b7-88ac-315de4066492" /></p>

## Features
- Suggests venues based on user preferences using the Google Maps API
- Creates shareable Google Calendar invites via the Google Calendar API
- Responds to natural language prompts in Discord using the Mistral API
- Maintains short-term planning context via in-memory conversation history

## Limitations
This project was built without LangChain, AutoGen, or other agent frameworks. The LLM agent is manually managed, relying on a linear conversation model stored in Python lists. Some known issues:
- No long-term memory or true function chaining
- Occasional event parsing errors under ambiguous input
- Hard-coded logic paths; brittle to phrasing variations
- Rate limits and API keys are not production-hardened

## Tech Stack
- Mistral API (LLM inference)
- Discord.py
- Google Maps API
- Google Calendar API

## Areas for Improvements
- Migrate to an agent framework (e.g., LangChain, CrewAI)
- Use vector store for context persistence
- Add unit tests and error handling
- OAuth2 flow for user-specific calendar permissions
