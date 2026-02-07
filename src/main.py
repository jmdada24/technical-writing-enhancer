from agents.mechanics_agent import MechanicsAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.enhancement_agent import EnhancementAgent
from agents.justification_agent import JustificationAgent
from agents.critique_agent import CritiqueAgent
from config import LLM_MODEL
from rag.retriever import retrieve_docs

MAX_ITERATIONS = 3  # safety guard


def run_pipeline(user_text: str, debug: bool = False) -> dict:
    mechanics = MechanicsAgent(model=LLM_MODEL)
    analyzer = AnalyzerAgent(model=LLM_MODEL)
    enhancer = EnhancementAgent(model=LLM_MODEL)
    critic = CritiqueAgent(model=LLM_MODEL)
    justifier = JustificationAgent(model=LLM_MODEL)

    original = (user_text or "").strip()
    if not original:
        return {
            "original": "",
            "cleaned": "",
            "enhanced": "",
            "applied_principles": [],
            "analysis": {},
            "critique": None,
            "explanation": "No input provided.",
            "debug_retrieved": [],
        }

    # 0) Grammar/mechanics first
    cleaned = mechanics.correct(original)

    # Optional debug: what would retriever return for this text?
    debug_retrieved = []
    if debug:
        docs = retrieve_docs(cleaned, k=8)
        debug_retrieved = [
            {"metadata": d.metadata, "content": d.page_content[:800]} for d in docs
        ]

    # 1) 6C analysis
    analysis = analyzer.analyze(cleaned)
    target_cs = analysis.get("target_cs", [])
    needs = analysis.get("needs_enhancement", False)

    current = cleaned
    revised = cleaned
    critique_result = None

    # 2) Enhancement + critique loop (only if needed)
    if needs and target_cs:
        for _ in range(MAX_ITERATIONS):
            revised = enhancer.enhance(current, target_cs)

            # stop if no change
            if revised.strip() == current.strip():
                break

            critique_result = critic.critique(original=cleaned, revised=revised)

            if critique_result.get("acceptable", False):
                break

            current = revised

    # 3) Explanation
    explanation = justifier.justify(original, revised, target_cs)

    return {
        "original": original,
        "cleaned": cleaned,
        "enhanced": revised,
        "applied_principles": target_cs,
        "analysis": analysis,
        "critique": critique_result,
        "explanation": explanation,
        "debug_retrieved": debug_retrieved,
    }


if __name__ == "__main__":
    print("Technical Writing Enhancer (6 C’s) — type 'exit' to quit.\n")
    while True:
        s = input("Enter text: ").strip()
        if not s:
            continue
        if s.lower() == "exit":
            break

        result = run_pipeline(s)

        print("\nOriginal:", result["original"])
        if result["cleaned"] != result["original"]:
            print("Mechanics-corrected:", result["cleaned"])

        print("Enhanced:", result["enhanced"])
        print("Principles:", result["applied_principles"])
        print("Explanation:", result["explanation"])

        if result.get("critique"):
            print("Critique acceptable:", result["critique"].get("acceptable"))

        print("-" * 50)
