from typing import List

def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """Split text into manageable chunks (default 1000 chars)."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current = ""

    for p in paragraphs:
        if len(current) + len(p) + 1 <= max_chars:
            current = current + "\n" + p if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) <= max_chars:
                current = p
            else:
                for i in range(0, len(p), max_chars):
                    chunks.append(p[i:i + max_chars])
                current = ""
    if current:
        chunks.append(current)
    return chunks
