import streamlit as st

from pipeline import run_pipeline

C_LABELS = {
    "clarity": "Clarity",
    "completeness": "Completeness",
    "conciseness": "Conciseness",
    "consistency": "Consistency",
    "concreteness": "Concreteness",
    "courtesy": "Courtesy",
}

st.set_page_config(
    page_title="Technical Writing Enhancer (6 C’s)",
    page_icon="📝",
    layout="centered",
)

st.title("Technical Writing Enhancer (6 C’s)")
st.caption("An agentic writing assistant that analyzes and selectively applies the 6C principles to improve technical communication.")

text = st.text_area(
    "Enter a sentence or paragraph",
    height=220,
    placeholder="Paste your text here...",
)

show_applied = st.checkbox("Show applied 6Cs", value=True)
show_analysis = st.checkbox("Show analysis (debug)", value=False)

rewrite_strength = st.selectbox(
    "Rewrite strength",
    ["light", "medium", "strong"],
    index=0,
)

run_btn = st.button("Analyze & Enhance", use_container_width=True)

if run_btn:
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    with st.spinner("Analyzing & enhancing..."):
        try:
            result = run_pipeline(text.strip(), rewrite_strength=rewrite_strength, debug=show_analysis)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    original = (result.get("original") or "").strip()
    enhanced = (result.get("enhanced") or "").strip()
    applied = result.get("applied_principles", []) or []
    changed = bool(result.get("changed", False))

    st.subheader("Original")
    st.write(original)

    st.subheader("Enhanced")
    st.write(enhanced)

    if show_applied:
        st.subheader("Applied 6Cs")
        if applied:
            pretty = [C_LABELS.get(c, c) for c in applied]
            st.write(", ".join(pretty))
        else:
            st.info("No 6C changes needed.")

    if show_analysis and "analysis" in result:
        st.subheader("Analysis (debug)")
        st.json(result["analysis"])
