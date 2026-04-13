# AstroPreneur — Multi-Agent Streamlit App

## Overview
This app integrates three local AI agents (Business/Financial, Marketing, Market Research) using Google Gemini models (via google-generativeai). It runs as a Streamlit web app.

## Setup
1. Copy `.env.example` → `.env` and set `GEMINI_API_KEY`.
2. Install deps:
   pip install -r requirements.txt
3. Run:
   streamlit run app.py

## Notes
- The agents call Google Gemini APIs. Ensure API key and quota available.
- For heavy workloads (large models / GPU), consider hosting agents as microservices.

