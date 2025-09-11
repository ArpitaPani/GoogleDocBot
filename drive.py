from googleapiclient.discovery import build


def list_google_docs(creds):
    """Return a list of Google Docs (id, name) from Drive."""
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.document' and trashed=false",
        pageSize=200,
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])


def get_doc_content(creds, file_id):
    """Fetch text content of a Google Doc using Docs API."""
    docs_service = build('docs', 'v1', credentials=creds)
    doc = docs_service.documents().get(documentId=file_id).execute()

    def _read_structural_elements(elements):
        text = ""
        for el in elements:
            if "paragraph" in el:
                for p_el in el["paragraph"].get("elements", []):
                    tr = p_el.get("textRun")
                    if tr:
                        text += tr.get("content", "")
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        text += _read_structural_elements(cell.get("content", []))
            elif "tableOfContents" in el:
                text += _read_structural_elements(el["tableOfContents"].get("content", []))
        return text

    return _read_structural_elements(doc.get("body", {}).get("content", []))
