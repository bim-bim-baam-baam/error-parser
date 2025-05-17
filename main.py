import requests
import json
from bs4 import BeautifulSoup

# === Настройки ===
base_url = "https://git.altlinux.org/beehive/logs/Sisyphus/i586/latest/error/"
error_keywords = ["error", "fatal", "failed", "exception", "critical", "errors", "fatals", "exceptions", "criticals"]
output_file = "errors.json"
max_links = 10000
RANGE_UP = 1
RANGE_DOWN = 3
MAX_ERRORS_PER_LINK = 5
split_chars = " \t\n\r\f\v.,:;!?'\"()[]{}<>|\\/="


# ==================


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
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for tr in soup.select("table.project_list tr"):
        a_tag = tr.find("a", class_="link")
        if a_tag and a_tag.get("href") != "..":
            link = base_url + a_tag["href"]
            links.append((a_tag["href"], link))
    return links[:max_links]


def parse_log(href, url):
    response = requests.get(url)
    lines = response.text.splitlines()
    error_blocks = []

    error_count = 0
    for index, line in enumerate(lines):
        if error_count >= MAX_ERRORS_PER_LINK:
            print(f"Достигнут максимум ошибок ({MAX_ERRORS_PER_LINK}) для {href}.")
            break

        words = list(split_line(line.lower()))
        if any(keyword in words for keyword in error_keywords):
            start = max(0, index - RANGE_UP)
            end = min(len(lines), index + RANGE_DOWN + 1)
            block = "\n".join(lines[start:end])
            error_blocks.append(block)
            error_count += 1

    if error_blocks:
        joined_errors = "\n\n".join(error_blocks)
        return {
            "package": href,
            "errors": joined_errors
        }
    return None


def main():
    links = get_links(base_url)
    all_errors = []
    print(len(links))

    for href, link in links:
        print(f"Сканирую: {link}")
        error_entry = parse_log(href, link)
        if error_entry:
            all_errors.append(error_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_errors, f, indent=2, ensure_ascii=False)

    print(f"Готово! Все ошибки сохранены в файл {output_file}.")
    print(f"Количество пакетов с ошибками:{len(all_errors)}")


if __name__ == "__main__":
    main()
