def chunk_text(text, max_chars=1000, overlap=100):
    """
    Split a long text into overlapping chunks of max_chars length.
    Skips empty or whitespace-only chunks.

    Args:
        text (str): The text to split.
        max_chars (int): Maximum number of characters per chunk.
        overlap (int): Overlap between chunks to preserve context.

    Returns:
        list[str]: List of cleaned, non-empty text chunks.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()
        if chunk:  
            chunks.append(chunk)

        next_start = end - overlap
        if next_start <= start:  
            next_start = end
        start = next_start

    return chunks


def preview_text(text, length=200):
    """
    Return a safe preview of the first few characters of a string.

    Args:
        text (str): Input text.
        length (int): Max characters in preview.

    Returns:
        str: Preview text.
    """
    if not text:
        return ""
    return (text[:length] + "...") if len(text) > length else text
