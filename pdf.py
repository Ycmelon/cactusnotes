import fitz  # pip install PyMuPDF


def pdf_from_pages(path: str, pages: set[int], label: str) -> str:
    file_handle = fitz.open(path)
    file_handle.select(sorted([x - 1 for x in pages]))  # 0-indexed, in order

    new_path = path.replace(".pdf", f" {label}.pdf")
    file_handle.save(new_path)

    return new_path
