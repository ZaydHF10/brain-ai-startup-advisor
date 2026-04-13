# agents/agent_financial.py
import os
import json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Defer import until runtime to give clearer errors if lib missing
try:
    import google.generativeai as genai
except Exception:
    genai = None

class BusinessFinancialAgent:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = GEMINI_API_KEY
        if api_key is None:
            raise RuntimeError("GEMINI_API_KEY not set in environment")
        if genai is None:
            raise RuntimeError("google.generativeai library not available. Install google-generativeai.")
        genai.configure(api_key=api_key)
        # Use a safe model name; adjust if you want a different gemini variant
        try:
            self.model = genai.GenerativeModel(model_name='gemini-2.0-flash')
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            # fallback attempt if API surface differs
            self.model = None
            self.chat_session = None
            self._init_error = str(e)

        self.business_data = {
            'name': '', 'industry': '', 'stage': '', 'target_market': '',
            'value_proposition': '', 'competitors': [], 'costs': {},
            'revenue_streams': [], 'pricing': {}, 'team_size': 0, 'funding': 0
        }

    def _get_system_prompt(self):
        return ("You are an expert Business Model & Financial Planning AI Agent..."
                " Be professional and structured. Respond clearly.")

    def chat(self, user_message: str) -> str:
        # If model/chat_session exist, use them, else return error
        if getattr(self, '_init_error', None):
            return f"ERROR initializing Gemini model: {self._init_error}"
        if self.chat_session is None:
            return "ERROR: chat session not initialized."
        try:
            self._extract_business_data(user_message)
            response = self.chat_session.send_message(user_message)
            return response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _extract_business_data(self, message: str):
        ml = message.lower()
        if 'saas' in ml or 'software' in ml:
            self.business_data['industry'] = 'SaaS/Software'
        # add other heuristics if needed
        if 'idea' in ml:
            self.business_data['stage'] = 'Idea'

    # convenience helpers
    def generate_business_canvas(self):
        prompt = f"Generate a business model canvas for industry {self.business_data.get('industry','not specified')}"
        return self.chat(prompt)

# Single persistent instance
_fin_agent = None

def get_financial_agent():
    global _fin_agent
    if _fin_agent is None:
        _fin_agent = BusinessFinancialAgent()
    return _fin_agent

def run_agent_financial(input_text: str, context: dict = None) -> Dict[str, Any]:
    agent = get_financial_agent()
    try:
        text = agent.chat(input_text)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}
