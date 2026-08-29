import io

import streamlit as st


@st.cache_data(show_spinner=False)
def pdf_to_pages(file_bytes):
    import pdfplumber

    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append((page_number, text))
    return pages


def locate_page(pages, keywords, window=1):
    import re

    if not pages:
        return "", None

    best_score = -1
    best_index = 0

    for index, (page_number, text) in enumerate(pages):
        keyword_score = sum(3 for keyword in keywords if keyword and keyword in text)

        number_matches = re.findall(r"\b\d[\d,]*\b", text)
        number_score = sum(1 for item in number_matches if len(item.replace(",", "")) >= 6)
        number_score = min(number_score, 10)

        total_score = keyword_score + number_score
        if total_score > best_score:
            best_score = total_score
            best_index = index

    start_index = max(0, best_index - window)
    end_index = min(len(pages), best_index + window + 1)
    combined_text = "\n\n".join(text for _, text in pages[start_index:end_index])

    return combined_text, pages[best_index][0]
