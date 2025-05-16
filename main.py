import requests
from bs4 import BeautifulSoup

base_url = "https://git.altlinux.org/beehive/logs/Sisyphus/i586/latest/error/"
error_keywords = ["error", "fatal", "failed", "exception", "critical", "errors", "fatals", "exceptions", "criticals"]
output_file = "errors.txt"
max_links = 10

split_chars = " \t\n\r\f\v.,:;!?'\"()[]{}<>|\\/="

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
    # return links[:max_links]
    return links
def parse_log(href, url):
    """Парсит лог по ссылке и извлекает строки с ошибками"""
    response = requests.get(url)
    error_lines = []
    for line in response.text.splitlines():
        # Разбиваем строку с помощью split_line
        words = list(split_line(line.lower()))
        if any(keyword in words for keyword in error_keywords):
            error_lines.append(f"{href}: {line}")
    return error_lines

def main():
    links = get_links(base_url)
    with open(output_file, "w", encoding="utf-8") as f:
        for href, link in links:
            print(f"Сканирую: {link}")
            error_lines = parse_log(href, link)
            if error_lines:
                f.write("\n".join(error_lines) + "\n\n")
    print(f"Готово! Все ошибки записаны в файл {output_file}.")

if __name__ == "__main__":
    main()
