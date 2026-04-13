# app.py
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
from dotenv import load_dotenv
load_dotenv()

from agents import run_agent_financial, run_agent_marketing, run_agent_marketresearch

st.set_page_config(page_title="AIpreneur — Multi-Agent", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("brAIn — Multi-Agent Entrepreneur Assistant")
st.write("Integrates three local agents: Financial, Marketing, Market Research (Gemini-based).")

parallel=False
show_raw = st.checkbox("Show raw outputs", value=False)

# Input
idea = st.text_area("Describe your project / ask a question:", height=140)
col1, col2, col3 = st.columns([1,1,1])

# Buttons
if col1.button("Run all agents"):
    if not idea.strip():
        st.warning("Type an idea first.")
    else:
        placeholder = st.empty()
        placeholder.info("Running agents...")

        start = time.time()
        results = {}

        if parallel:
            with ThreadPoolExecutor(max_workers=3) as ex:
                futures = {
                    ex.submit(run_agent_financial, idea): "financial",
                    ex.submit(run_agent_marketing, idea): "marketing",
                    ex.submit(run_agent_marketresearch, idea): "marketresearch",
                }
                for fut in as_completed(futures):
                    key = futures[fut]
                    try:
                        results[key] = fut.result()
                    except Exception as e:
                        results[key] = {"error": str(e)}
        else:
            results["financial"] = run_agent_financial(idea)
            results["marketing"] = run_agent_marketing(idea)
            results["marketresearch"] = run_agent_marketresearch(idea)

        elapsed = time.time() - start
        placeholder.success(f"Done in {elapsed:.1f}s")

        # store to history
        st.session_state.history.insert(0, {"input": idea, "results": results, "ts": time.time()})
        st.session_state.history = st.session_state.history[:]
        st.rerun()  

if col2.button("Financial only"):
    if not idea.strip():
        st.warning("Type an idea first.")
    else:
        res = run_agent_financial(idea)
        st.session_state.history.insert(0, {"input": idea, "results": {"financial": res}, "ts": time.time()})
        st.rerun()

if col3.button("Market Research only"):
    if not idea.strip():
        st.warning("Type an idea first.")
    else:
        res = run_agent_marketresearch(idea)
        st.session_state.history.insert(0, {"input": idea, "results": {"marketresearch": res}, "ts": time.time()})
        st.rerun()

st.markdown("---")
# Show latest
st.subheader("Latest")
if st.session_state.history:
    latest = st.session_state.history[0]
    st.markdown(f"**Input:** {latest['input']}")
    results = latest["results"]

    cols = st.columns(len(results))
    for i,(k,v) in enumerate(results.items()):
        with cols[i]:
            st.markdown(f"### {k.capitalize()}")
            if isinstance(v, dict) and "error" in v:
                st.error(v["error"])
                continue
            # Financial
            if k == "financial":
                if isinstance(v, dict) and "text" in v:
                    if show_raw:
                        st.code(v["text"])
                    else:
                        st.write(v["text"][:1000])
                else:
                    st.write(v)
            # Marketing
            elif k == "marketing":
                if isinstance(v, dict) and "combined" in v:
                    for persona, text in v["combined"].items():
                        st.markdown(f"**{persona}**")
                        if show_raw:
                            st.code(text)
                        else:
                            st.write(text[:800])
                else:
                    st.write(v)
            # marketresearch
            elif k == "marketresearch":
                # v expected to be {"text": "...", "figure": matplotlib.figure.Figure}
                if isinstance(v, dict):
                    txt = v.get("text", "")
                    fig = v.get("figure", None)
                    if show_raw:
                        st.code(txt)
                    else:
                        st.write(txt[:800])
                    if fig is not None:
                        st.pyplot(fig)
                else:
                    st.write(v)
else:
    st.info("No runs yet — enter an idea and run the agents.")

st.markdown("---")
# History viewer
st.subheader("History")
for idx, item in enumerate(st.session_state.history):
    with st.expander(f"{idx+1}. {item['input']}"):
        st.write("Timestamp:", time.ctime(item["ts"]))
        if show_raw:
            st.json(item["results"])
        else:
            for key, val in item["results"].items():
                st.markdown(f"**{key}**")
                if isinstance(val, dict):
                    if key == "marketresearch":
                        st.write(val.get("text","")[:800])
                    elif key == "marketing":
                        if isinstance(val.get("combined"), dict):
                            for persona, t in val["combined"].items():
                                st.write(f"- {persona}: {t[:300]}")
                        else:
                            st.write(str(val)[:500])
                    else:
                        st.write(val.get("text","")[:800])
                else:
                    st.write(str(val)[:400])
