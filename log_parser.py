import requests
from bs4 import BeautifulSoup

error_keywords = ["error", "fatal", "failed", "exception", "critical", "errors", "fatals", "exceptions", "criticals"]
max_links = 10
RANGE_UP = 1
RANGE_DOWN = 3
MAX_ERRORS_PER_LINK = 5
split_chars = " \t\n\r\f\v.,:;!?'\"()[]{}<>|\\/="

def split_line(line):
    temp_word = ""
    for char in line:
        if char in split_chars:
            if temp_word:
                yield temp_word
                temp_word = ""
        else:
            temp_word += char
    if temp_word:
        yield temp_word

def get_links(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for tr in soup.select("table.project_list tr"):
        a_tag = tr.find("a", class_="link")
        if a_tag and a_tag.get("href") != "..":
            link = url + a_tag["href"]
            links.append((a_tag["href"], link))
    return links[:max_links]

def parse_log(href, url):
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.splitlines()
    error_blocks = []
    error_count = 0

    for index, line in enumerate(lines):
        if error_count >= MAX_ERRORS_PER_LINK:
            break

        words = list(split_line(line.lower()))
        if any(keyword in words for keyword in error_keywords):
            start = max(0, index - RANGE_UP)
            end = min(len(lines), index + RANGE_DOWN + 1)
            block = "\n".join(lines[start:end])
            error_blocks.append(block)
            error_count += 1

    if error_blocks:
        return {
            "package": href,
            "errors": "\n\n".join(error_blocks)
        }
    return None
