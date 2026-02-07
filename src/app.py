import streamlit as st
from main import run_pipeline

st.set_page_config(
    page_title="Technical Writing Enhancer (6 C’s)",
    page_icon="",
    layout="centered"
)

st.title("Technical Writing Enhancer (6 C’s)")
st.caption("Agentic AI using Ollama + RAG (ChromaDB). Conservative rewriting: only changes when needed.")

text = st.text_area(
    "Enter a sentence or short paragraph",
    height=160,
    placeholder="e.g., The contract should be signed by Mr. Aguirre on the dotted line."
)

col1, col2 = st.columns([1, 1])
with col1:
    run_btn = st.button("Analyze & Enhance", use_container_width=True)
with col2:
    debug = st.checkbox("Show debug (analysis + retrieved C's)", value=False)

if run_btn:
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Analyzing..."):
            result = run_pipeline(text.strip(), debug=debug)

        st.subheader("Original")
        st.write(result["original"])

        if result["cleaned"] != result["original"]:
            st.subheader("Mechanics-corrected")
            st.write(result["cleaned"])


        st.subheader("Enhanced")
        st.write(result["enhanced"])

        if result["applied_principles"]:
            st.subheader("Applied Principles")
            st.write(", ".join(result["applied_principles"]))

            st.subheader("Explanation")
            st.write(result["explanation"])
        else:
            if result["cleaned"].strip() != result["original"].strip():
                st.info("No 6C enhancement applied, but grammar/mechanics were corrected.")
            else:
                st.success("No enhancement needed. The sentence is already effective.")
        
        if debug:
            st.subheader("Debug: Retrieved Chunks (Top-K)")
            for i, item in enumerate(result.get("debug_retrieved", []), start=1):
                st.markdown(f"**#{i}**  \nMetadata: `{item['metadata']}`")
                st.code(item["content"])