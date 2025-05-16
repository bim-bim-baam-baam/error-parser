import requests
from bs4 import BeautifulSoup

# === Настройки ===
base_url = "https://git.altlinux.org/beehive/logs/Sisyphus/i586/latest/error/"
error_keywords = ["error", "fatal", "failed", "exception", "critical", "errors", "fatals", "exceptions", "criticals"]
output_file = "errors"
max_links = 100               # Сколько ссылок максимально забираем
RANGE_UP = 1                  # Количество строк ДО найденной строки
RANGE_DOWN = 3                # Количество строк ПОСЛЕ найденной строки
MAX_LOGS_IN_FILE = 10         # Максимальное количество обработанных пакетов на файл
MAX_ERRORS_PER_LINK = 5       # Максимальное количество ошибок, записанных с одного лога
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

    error_count = 0
    for index, line in enumerate(lines):
        if error_count >= MAX_ERRORS_PER_LINK:
            print(f"Достигнут максимум ошибок ({MAX_ERRORS_PER_LINK}) для {href}. Переход к следующему пакету.")
            break

        words = list(split_line(line.lower()))
        if any(keyword in words for keyword in error_keywords):
            start = max(0, index - RANGE_UP)
            end = min(len(lines), index + RANGE_DOWN + 1)
            block = "\n".join(lines[start:end])
            error_blocks.append(f"============[ PACKAGE: {href} ]============\n{block}\n\n\n")
            error_count += 1

    return error_blocks


def main():
    links = get_links(base_url)
    file_index = 1
    current_count = 0
    output_filename = f"{output_file}_part{file_index}.txt"
    f = open(output_filename, "w", encoding="utf-8")

    for href, link in links:
        if current_count >= MAX_LOGS_IN_FILE:
            f.close()
            file_index += 1
            output_filename = f"{output_file}_part{file_index}.txt"
            f = open(output_filename, "w", encoding="utf-8")
            current_count = 0
            print(f"Создан новый файл: {output_filename}")

        print(f"Сканирую: {link}")
        error_blocks = parse_log(href, link)
        if error_blocks:
            f.write("\n".join(error_blocks) + "\n\n")
            current_count += 1

    f.close()
    print(f"Готово! Все ошибки записаны в файлы errors_partX.txt.")


if __name__ == "__main__":
    main()
