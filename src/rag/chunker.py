from typing import List
from langchain_core.documents import Document


def chunk_markdown_by_h2(content: str, principle: str) -> List[Document]:
    """
    Splits markdown into meaningful chunks:
    - H2 sections (##)
    - Inside 'Examples', further splits by H3 (###) so
      each poor/improved example becomes its own retrievable unit.
    """
    docs: List[Document] = []

    sections = content.split("## ")
    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.splitlines()
        section_title = lines[0].strip().lower().replace(" ", "_")
        body = "\n".join(lines[1:]).strip()

        if not body:
            continue

        # Special handling for Examples
        if section_title == "examples":
            examples = body.split("### ")
            for ex in examples:
                ex = ex.strip()
                if not ex:
                    continue

                ex_lines = ex.splitlines()
                ex_title = ex_lines[0].strip().lower()
                ex_body = "\n".join(ex_lines[1:]).strip()

                if not ex_body:
                    continue

                example_type = "unknown"
                if "poor" in ex_title:
                    example_type = "poor"
                elif "improved" in ex_title:
                    example_type = "improved"

                docs.append(
                    Document(
                        page_content=ex_body,
                        metadata={
                            "principle": principle,
                            "section": "examples",
                            "example_type": example_type,
                        },
                    )
                )
        else:
            # Normal section
            docs.append(
                Document(
                    page_content=body,
                    metadata={
                        "principle": principle,
                        "section": section_title,
                    },
                )
            )

    return docs
