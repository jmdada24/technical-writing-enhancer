import argparse
from pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Technical Writing Enhancer (6Cs) - CLI")
    parser.add_argument("--text", type=str, required=True, help="Text to enhance")
    parser.add_argument("--strength", type=str, default="light", choices=["light", "medium", "strong"])
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.text, rewrite_strength=args.strength, debug=args.debug)

    print("\n=== Applied 6Cs ===")
    print(result.get("applied_principles", []))

    print("\n=== Enhanced ===")
    print(result.get("enhanced", ""))

    if args.debug:
        print("\n=== Analysis (debug) ===")
        print(result.get("analysis", {}))

if __name__ == "__main__":
    main()
