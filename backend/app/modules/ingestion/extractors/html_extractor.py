from pathlib import Path
from bs4 import BeautifulSoup


def extract_html(file_path: str) -> dict:
    path = Path(file_path)

    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(" ", strip=True) if soup.title else path.stem

    for tag in soup(["script", "style", "noscript", "nav", "footer"]):
        tag.decompose()

    content = soup.find("main") or soup.body or soup

    lines = []
    for element in content.find_all(
        ["h1", "h2", "h3", "p", "li"],
    ):
        text = element.get_text(" ", strip=True)

        if text:
            if element.name.startswith("h"):
                lines.append(f"\n## {text}\n")
            else:
                lines.append(text)

    return {
        "title": title,
        "text": "\n".join(lines).strip()
    }