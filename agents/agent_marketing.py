# agents/agent_marketing.py
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

try:
    import google.generativeai as genai
except Exception:
    genai = None

class MarketingAgentWrapper:
    def __init__(self):
        if GEMINI_API_KEY is None:
            raise RuntimeError("GEMINI_API_KEY not set")
        if genai is None:
            raise RuntimeError("google.generativeai not installed")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def ask(self, name: str, question: str, role_description: str = ""):
        # Build system prompt
        system_prompt = f"You are {name}. {role_description}\nAnswer concisely and give actionable steps."
        prompt = f"{system_prompt}\n\nQuestion: {question}"
        try:
            # Some genai SDKs expose .generate_content or .generate
            resp = None
            try:
                resp = self.model.generate_content(prompt)
                return resp.text if hasattr(resp, 'text') else str(resp)
            except Exception:
                # fallback using start_chat style
                chat = self.model.start_chat(history=[])
                r = chat.send_message(prompt)
                return r.text if hasattr(r, 'text') else str(r)
        except Exception as e:
            return f"ERROR: {str(e)}"

# singleton
_marketing_agent = None

def get_marketing_agent():
    global _marketing_agent
    if _marketing_agent is None:
        _marketing_agent = MarketingAgentWrapper()
    return _marketing_agent

def run_agent_marketing(input_text: str, context: dict = None) -> dict:
    agent = get_marketing_agent()
    # We'll query all three personas and return their responses
    personas = {
        "Strategic Sarah": "Marketing strategy, GTM, positioning.",
        "Campaign Chris": "Digital marketing, ads, social, SEO.",
        "Analytics Alex": "KPI, metrics, dashboards, A/B testing."
    }
    out = {}
    for name, role in personas.items():
        try:
            resp = agent.ask(name, input_text, role_description=role)
            out[name] = resp
        except Exception as e:
            out[name] = f"ERROR: {str(e)}"
    return {"combined": out}
