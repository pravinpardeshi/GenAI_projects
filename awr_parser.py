# awr_parser.py

from bs4 import BeautifulSoup
from typing import List, Tuple

def parse_awr_html(html: str) -> List[str]:
    """
    Parses HTML-based AWR report and returns a list of meaningful text chunks.
    """
    soup = BeautifulSoup(html, "html.parser")
    sections = []

    # Oracle AWR reports often use <h2>, <h3>, or bold text to denote sections
    current_section = ""
    for tag in soup.find_all(['h1', 'h2', 'h3', 'b', 'table']):
        if tag.name in ['h1', 'h2', 'h3', 'b']:
            section_title = tag.get_text(strip=True)
            if section_title:
                current_section = section_title
        elif tag.name == 'table':
            table_text = extract_table_text(tag)
            if table_text:
                full_text = f"{current_section}\n{table_text}"
                sections.append(full_text)

    return sections

def extract_table_text(table_tag) -> str:
    """
    Converts an HTML <table> tag into a readable text format.
    """
    rows = []
    for row in table_tag.find_all('tr'):
        cols = row.find_all(['td', 'th'])
        row_text = " | ".join(col.get_text(strip=True) for col in cols)
        if row_text:
            rows.append(row_text)
    return "\n".join(rows)


