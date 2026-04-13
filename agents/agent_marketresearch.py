# agents/agent_marketresearch.py
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class MarketResearchAgent:
    def __init__(self):
        if GEMINI_API_KEY is None:
            raise RuntimeError("GEMINI_API_KEY not set")
        if genai is None:
            raise RuntimeError("google.generativeai not installed")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        # optional history
        self.history = []

    def ask(self, question: str, visualize: bool = False):
        prompt = f"You are a market research assistant. {question}"
        try:
            resp = None
            try:
                resp = self.model.generate_content(prompt)
                text = resp.text if hasattr(resp, 'text') else str(resp)
            except Exception:
                chat = self.model.start_chat(history=[])
                r = chat.send_message(prompt)
                text = r.text if hasattr(r, 'text') else str(r)
        except Exception as e:
            text = f"ERROR: {str(e)}"
        fig = None
        if visualize and plt is not None:
            # simple heuristic: visualize market segments if the question contains 'segments'
            if 'segment' in question.lower():
                data = {"Health-Conscious": 30, "Busy Professionals": 25, "Families": 20, "Others": 25}
                fig = self._plot_pie(data, title="Market Segments (example)")
            elif 'trend' in question.lower():
                data = {"2023": 15, "2024": 18, "2025": 22}
                fig = self._plot_line(data, title="Trend (example)")
            elif 'competitor' in question.lower():
                data = {"Competitor A": 40, "Competitor B": 30, "Others": 30}
                fig = self._plot_bar(data, title="Competitor Share (example)")

        self.history.append((question, text))
        return {"text": text, "figure": fig}

    def _plot_pie(self, data, title=""):
        labels = list(data.keys())
        sizes = list(data.values())
        fig, ax = plt.subplots(figsize=(5,4))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(title)
        plt.tight_layout()
        return fig

    def _plot_bar(self, data, title=""):
        labels = list(data.keys())
        vals = list(data.values())
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(labels, vals)
        ax.set_title(title)
        plt.tight_layout()
        return fig

    def _plot_line(self, data, title=""):
        labels = list(data.keys())
        vals = list(data.values())
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(labels, vals, marker='o')
        ax.set_title(title)
        plt.tight_layout()
        return fig

_market_agent = None

def get_market_agent():
    global _market_agent
    if _market_agent is None:
        _market_agent = MarketResearchAgent()
    return _market_agent

def run_agent_marketresearch(input_text: str, context: dict = None) -> dict:
    agent = get_market_agent()
    try:
        res = agent.ask(input_text, visualize=True)
        # result contains 'text' and 'figure'
        return res
    except Exception as e:
        return {"error": str(e)}
