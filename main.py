import requests
from bs4 import BeautifulSoup

# === Настройки ===
base_url = "https://git.altlinux.org/beehive/logs/Sisyphus/i586/latest/error/"
error_keywords = ["error", "fatal", "failed", "exception", "critical", "errors", "fatals", "exceptions", "criticals"]
output_file = "errors.txt"
max_links = 2
RANGE = 4  # Количество строк до и после найденной строки
split_chars = " \t\n\r\f\v.,:;!?'\"()[]{}<>|\\/="
# ==================

def split_line(line):
    """Разбивает строку по символам из split_chars"""
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
    """Получает все ссылки на логи с главной страницы"""
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
    """Парсит лог по ссылке и извлекает блоки строк с ошибками"""
    response = requests.get(url)
    lines = response.text.splitlines()
    error_blocks = []

    for index, line in enumerate(lines):
        words = list(split_line(line.lower()))
        if any(keyword in words for keyword in error_keywords):
            start = max(0, index - RANGE)
            end = min(len(lines), index + RANGE + 1)
            block = "\n".join(lines[start:end])
            error_blocks.append(f"============[ PACKAGE: {href} ]============\n{block}\n\n\n")

    return error_blocks

def main():
    links = get_links(base_url)
    with open(output_file, "w", encoding="utf-8") as f:
        for href, link in links:
            print(f"Сканирую: {link}")
            error_blocks = parse_log(href, link)
            if error_blocks:
                f.write("\n".join(error_blocks) + "\n\n")
    print(f"Готово! Все ошибки записаны в файл {output_file}.")

if __name__ == "__main__":
    main()
