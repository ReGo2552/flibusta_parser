import urllib.parse
import re
import requests
from bs4 import BeautifulSoup
import time
import random
import json


def build_search_url(query, page=0):
    """
    Создает URL для поиска на Flibusta на основе запроса пользователя.

    Args:
        query (str): Поисковый запрос пользователя
        page (int, optional): Номер страницы результатов. По умолчанию 0.

    Returns:
        str: URL для поиска
    """
    # Убираем лишние пробелы и разделяем слова
    words = query.strip().split()

    # Кодируем каждое слово для URL
    encoded_words = [urllib.parse.quote(word) for word in words]

    # Соединяем слова знаком '+'
    formatted_query = '+'.join(encoded_words)

    # Формируем URL для поиска
    url = f"https://flibusta.is/booksearch?page={page}&ask={formatted_query}"

    return url


def get_max_page_number(html_content):
    """
    Извлекает максимальный номер страницы из HTML-кода страницы результатов поиска.

    Args:
        html_content (str): HTML-код страницы

    Returns:
        int: Максимальный номер страницы или 1, если не найдено
    """
    # Используем регулярные выражения для поиска ссылок на страницы
    page_links_pattern = r'booksearch\?page=(\d+)&amp;ask='
    matches = re.findall(page_links_pattern, html_content)

    max_page = 0
    if matches:
        # Преобразуем найденные номера страниц в целые числа
        page_numbers = [int(page) + 1 for page in matches]  # page=0 соответствует странице 1
        max_page = max(page_numbers)

    # Если ничего не найдено, возвращаем 1 (текущая страница)
    return max_page if max_page > 0 else 1


def get_search_results_page(query, page=0):
    """
    Получает HTML-код страницы результатов поиска.

    Args:
        query (str): Поисковый запрос пользователя
        page (int, optional): Номер страницы результатов. По умолчанию 0.

    Returns:
        str: HTML-код страницы или None в случае ошибки
    """
    url = build_search_url(query, page)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://flibusta.is/'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка при запросе: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None


def make_request(url):
    """
    Выполняет HTTP-запрос и возвращает HTML-код страницы.

    Args:
        url (str): URL страницы

    Returns:
        str: HTML-код страницы или None в случае ошибки
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://flibusta.is/'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка при запросе: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None


def parse_series(html_content):
    """
    Извлекает информацию о сериях книг из HTML-кода страницы.

    Args:
        html_content (str): HTML-код страницы

    Returns:
        list: Список словарей с информацией о сериях
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    series_list = []

    # Ищем заголовок раздела серий
    series_header = soup.find(string=lambda text: isinstance(text, str) and 'Найденные серии' in text)

    if series_header:
        # Получаем следующий после заголовка элемент <ul>, который содержит список серий
        series_ul = series_header.find_next('ul')

        if series_ul:
            series_items = series_ul.find_all('li')

            for item in series_items:
                series_info = {}

                # Находим ссылку на серию
                series_link = item.find('a')
                if series_link:
                    # Получаем URL серии
                    series_info['url'] = 'https://flibusta.is' + series_link['href']

                    # Получаем название серии
                    series_name = series_link.get_text().strip()
                    series_info['name'] = series_name

                    # Пытаемся извлечь количество книг в серии
                    series_text = item.get_text()
                    books_count_match = re.search(r'\((\d+) книг', series_text)
                    if books_count_match:
                        series_info['books_count'] = int(books_count_match.group(1))

                    series_list.append(series_info)

    return series_list


def parse_authors(html_content):
    """
    Извлекает информацию об авторах из HTML-кода страницы.

    Args:
        html_content (str): HTML-код страницы

    Returns:
        list: Список словарей с информацией об авторах
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    authors_list = []

    # Ищем заголовок раздела авторов
    authors_header = soup.find(string=lambda text: isinstance(text, str) and 'Найденные писатели' in text)

    if authors_header:
        # Получаем следующий после заголовка элемент <ul>, который содержит список авторов
        authors_ul = authors_header.find_next('ul')

        if authors_ul:
            author_items = authors_ul.find_all('li')

            for item in author_items:
                author_info = {}

                # Находим ссылку на автора
                author_link = item.find('a')
                if author_link:
                    # Получаем URL автора
                    author_info['url'] = 'https://flibusta.is' + author_link['href']

                    # Получаем имя автора
                    author_name = author_link.get_text().strip()
                    author_info['name'] = author_name

                    # Пытаемся извлечь количество книг автора
                    author_text = item.get_text()
                    books_count_match = re.search(r'\((\d+) книг', author_text)
                    if books_count_match:
                        author_info['books_count'] = int(books_count_match.group(1))

                    authors_list.append(author_info)

    return authors_list


def parse_books(html_content):
    """
    Извлекает информацию о книгах из HTML-кода страницы.

    Args:
        html_content (str): HTML-код страницы

    Returns:
        list: Список словарей с информацией о книгах
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    books_list = []

    # Ищем заголовок раздела книг
    books_header = soup.find(string=lambda text: isinstance(text, str) and 'Найденные книги' in text)

    if books_header:
        # Получаем следующий после заголовка элемент <ul>, который содержит список книг
        books_ul = books_header.find_next('ul')

        if books_ul:
            book_items = books_ul.find_all('li')

            for item in book_items:
                book_info = {}

                # Находим ссылку на книгу (первая ссылка в элементе)
                book_link = item.find('a')
                if book_link:
                    # Получаем URL книги
                    book_info['url'] = 'https://flibusta.is' + book_link['href']

                    # Получаем название книги
                    book_title = book_link.get_text().strip()
                    book_info['title'] = book_title

                    # Находим всех авторов книги (все ссылки после первой)
                    author_links = item.find_all('a')[1:]
                    authors = []

                    for author_link in author_links:
                        author_info = {
                            'name': author_link.get_text().strip(),
                            'url': 'https://flibusta.is' + author_link['href']
                        }
                        authors.append(author_info)

                    book_info['authors'] = authors

                    books_list.append(book_info)

    return books_list


def get_max_page_number_from_url(html_content, base_url_pattern):
    """
    Извлекает максимальный номер страницы из HTML-кода страницы.

    Args:
        html_content (str): HTML-код страницы
        base_url_pattern (str): Базовый шаблон URL для поиска страниц

    Returns:
        int: Максимальный номер страницы или 0, если не найдено
    """
    # Используем регулярные выражения для поиска ссылок на страницы
    page_links_pattern = rf'{base_url_pattern}\?page=(\d+)'
    matches = re.findall(page_links_pattern, html_content)

    max_page = 0
    if matches:
        # Преобразуем найденные номера страниц в целые числа
        page_numbers = [int(page) for page in matches]
        max_page = max(page_numbers)

    return max_page + 1  # +1 потому что нумерация начинается с 0


def parse_series_books(html_content):
    """
    Извлекает информацию о книгах из страницы серии.

    Args:
        html_content (str): HTML-код страницы серии

    Returns:
        dict: Словарь с информацией о серии и список книг
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    series_info = {}
    books_list = []

    # Получаем название серии
    title = soup.find('h1', class_='title')
    if title:
        series_info['name'] = title.get_text().strip()

    # Получаем информацию о серии
    series_table = soup.find('table', style="width: auto")
    if series_table:
        rows = series_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text().strip().replace(':', '')
                value = cells[1].get_text().strip()
                series_info[key] = value

    # Получаем список книг
    # На странице серии книги представлены не в ul/li, а просто строками, разделенными <br>
    # Ищем все ссылки на книги, которые идут после тега img и перед тегом <br>
    book_links = soup.find_all('a', href=lambda href: href and href.startswith('/b/'))

    for book_link in book_links:
        # Проверяем, что перед ссылкой идет img (значок книги)
        prev_elem = book_link.previous_sibling
        while prev_elem and prev_elem.name != 'img' and prev_elem.name != 'br':
            prev_elem = prev_elem.previous_sibling

        if prev_elem and prev_elem.name == 'img':
            book_info = {
                'title': book_link.get_text().strip(),
                'url': 'https://flibusta.is' + book_link['href']
            }

            # Ищем авторов книги
            next_elem = book_link.next_sibling
            authors = []

            # Ищем следующий тег <a> с href, начинающимся с /a/ (авторы)
            while next_elem and not (hasattr(next_elem, 'name') and next_elem.name == 'br'):
                if hasattr(next_elem, 'name') and next_elem.name == 'a' and next_elem.get('href', '').startswith('/a/'):
                    author_info = {
                        'name': next_elem.get_text().strip(),
                        'url': 'https://flibusta.is' + next_elem['href']
                    }
                    authors.append(author_info)
                next_elem = next_elem.next_sibling

            book_info['authors'] = authors

            # Ищем форматы для скачивания
            download_links = []
            next_elem = book_link.next_sibling
            while next_elem and not (hasattr(next_elem, 'name') and next_elem.name == 'br'):
                if hasattr(next_elem, 'name') and next_elem.name == 'a' and 'скачать' in str(
                        next_elem.previous_sibling):
                    format_match = re.search(r'\((.*?)\)', next_elem.get_text())
                    if format_match:
                        download_info = {
                            'format': format_match.group(1),
                            'url': 'https://flibusta.is' + next_elem['href']
                        }
                        download_links.append(download_info)
                next_elem = next_elem.next_sibling

            book_info['download_links'] = download_links

            books_list.append(book_info)

    # Проверяем наличие пагинации
    pager = soup.find('div', class_='item-list').find('ul', class_='pager')
    if pager:
        # Находим максимальный номер страницы
        max_page = 0

        # Ищем ссылку на последнюю страницу
        last_page_link = pager.find('li', class_='pager-last')
        if last_page_link and last_page_link.find('a'):
            last_page_url = last_page_link.find('a')['href']
            page_match = re.search(r'page=(\d+)', last_page_url)
            if page_match:
                max_page = int(page_match.group(1)) + 1  # +1 потому что нумерация начинается с 0

        series_info['total_pages'] = max_page + 1  # +1 для учета текущей страницы
    else:
        series_info['total_pages'] = 1

    return {
        'series_info': series_info,
        'books': books_list
    }


def parse_author_books(html_content):
    """
    Извлекает информацию о книгах из страницы автора.

    Args:
        html_content (str): HTML-код страницы автора

    Returns:
        dict: Словарь с информацией об авторе и список книг
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    author_info = {}
    books_list = []

    # Получаем имя автора
    title = soup.find('h1', class_='title')
    if title:
        author_info['name'] = title.get_text().strip()

    # Получаем жанры автора
    genre_p = soup.find('p', class_='genre')
    if genre_p:
        genres = []
        genre_links = genre_p.find_all('a', class_='genre')
        for genre_link in genre_links:
            genre_info = {
                'name': genre_link.get_text().strip(),
                'url': 'https://flibusta.is' + genre_link['href']
            }
            genres.append(genre_info)
        author_info['genres'] = genres

    # Получаем список книг
    book_links = soup.find_all('a', href=lambda href: href and href.startswith('/b/'))

    for book_link in book_links:
        # Проверяем, что перед ссылкой идет img (значок книги) или текст с оценкой
        prev_elem = book_link.previous_sibling
        img_found = False

        while prev_elem and not img_found:
            if hasattr(prev_elem, 'name') and prev_elem.name == 'img':
                img_found = True
            elif hasattr(prev_elem, 'name') and prev_elem.name == 'svg':
                img_found = True
            prev_elem = prev_elem.previous_sibling

        if img_found:
            book_info = {
                'title': book_link.get_text().strip(),
                'url': 'https://flibusta.is' + book_link['href']
            }

            # Ищем форматы для скачивания
            download_links = []
            next_elem = book_link.next_sibling
            while next_elem and not (hasattr(next_elem, 'name') and next_elem.name == 'br'):
                if hasattr(next_elem, 'name') and next_elem.name == 'a' and 'скачать' in str(
                        next_elem.previous_sibling):
                    format_match = re.search(r'\((.*?)\)', next_elem.get_text())
                    if format_match:
                        download_info = {
                            'format': format_match.group(1),
                            'url': 'https://flibusta.is' + next_elem['href']
                        }
                        download_links.append(download_info)
                next_elem = next_elem.next_sibling

            book_info['download_links'] = download_links

            books_list.append(book_info)

    # Проверяем наличие пагинации
    pager = soup.find('div', class_='item-list')
    if pager and pager.find('ul', class_='pager'):
        # Находим максимальный номер страницы
        max_page = 0

        # Ищем ссылку на последнюю страницу
        last_page_link = pager.find('li', class_='pager-last')
        if last_page_link and last_page_link.find('a'):
            last_page_url = last_page_link.find('a')['href']
            page_match = re.search(r'page=(\d+)', last_page_url)
            if page_match:
                max_page = int(page_match.group(1)) + 1  # +1 потому что нумерация начинается с 0

        author_info['total_pages'] = max_page + 1  # +1 для учета текущей страницы
    else:
        author_info['total_pages'] = 1

    return {
        'author_info': author_info,
        'books': books_list
    }


def get_series_books(series_url):
    """
    Получает информацию о книгах из серии, включая все страницы пагинации.

    Args:
        series_url (str): URL страницы серии

    Returns:
        dict: Словарь с информацией о серии и полный список книг
    """
    # Получаем HTML первой страницы
    html_content = make_request(series_url)

    if not html_content:
        print(f"Не удалось получить страницу серии: {series_url}")
        return None

    # Парсим первую страницу
    result = parse_series_books(html_content)

    # Если есть дополнительные страницы, парсим их
    total_pages = result['series_info'].get('total_pages', 1)

    if total_pages > 1:
        all_books = result['books']

        for page in range(1, total_pages):
            page_url = f"{series_url}?page={page}"
            time.sleep(1 + random.random() * 2)  # Добавляем случайную задержку

            html_content = make_request(page_url)

            if html_content:
                page_result = parse_series_books(html_content)
                all_books.extend(page_result['books'])
            else:
                print(f"Не удалось получить страницу {page + 1} серии")

        result['books'] = all_books

    return result


def get_author_books(author_url):
    """
    Получает информацию о книгах автора, включая все страницы пагинации.

    Args:
        author_url (str): URL страницы автора

    Returns:
        dict: Словарь с информацией об авторе и полный список книг
    """
    # Получаем HTML первой страницы
    html_content = make_request(author_url)

    if not html_content:
        print(f"Не удалось получить страницу автора: {author_url}")
        return None

    # Парсим первую страницу
    result = parse_author_books(html_content)

    # Если есть дополнительные страницы, парсим их
    total_pages = result['author_info'].get('total_pages', 1)

    if total_pages > 1:
        all_books = result['books']

        for page in range(1, total_pages):
            page_url = f"{author_url}?page={page}"
            time.sleep(1 + random.random() * 2)  # Добавляем случайную задержку

            html_content = make_request(page_url)

            if html_content:
                page_result = parse_author_books(html_content)
                all_books.extend(page_result['books'])
            else:
                print(f"Не удалось получить страницу {page + 1} автора")

        result['books'] = all_books

    return result


def parse_all_pages(query, max_pages=None):
    """
    Проходит по всем страницам результатов поиска и собирает информацию.

    Args:
        query (str): Поисковый запрос пользователя
        max_pages (int, optional): Максимальное количество страниц для обработки
                                  Если None, обрабатываются все найденные страницы

    Returns:
        dict: Словарь с собранной информацией о сериях, авторах и книгах
    """
    # Получаем HTML-код первой страницы
    html_content = get_search_results_page(query)

    if not html_content:
        print("Не удалось получить результаты поиска.")
        return None

    # Определяем количество страниц с результатами
    total_pages = get_max_page_number(html_content)

    if max_pages is not None and max_pages < total_pages:
        total_pages = max_pages

    print(f"Всего страниц с результатами: {total_pages}")

    # Инициализируем структуры данных для хранения результатов
    all_series = []
    all_authors = []
    all_books = []

    # Обрабатываем первую страницу
    series = parse_series(html_content)
    authors = parse_authors(html_content)
    books = parse_books(html_content)

    all_series.extend(series)
    all_authors.extend(authors)
    all_books.extend(books)

    print(f"Страница 1: найдено {len(series)} серий, {len(authors)} авторов, {len(books)} книг")

    # Обрабатываем остальные страницы
    for page in range(1, total_pages):
        print(f"Обработка страницы {page + 1}...")

        # Добавляем случайную задержку перед запросом для имитации человеческого поведения
        time.sleep(1 + random.random() * 2)

        # Получаем HTML-код текущей страницы
        html_content = get_search_results_page(query, page)

        if html_content:
            # Парсим данные с текущей страницы
            series = parse_series(html_content)
            authors = parse_authors(html_content)
            books = parse_books(html_content)

            all_series.extend(series)
            all_authors.extend(authors)
            all_books.extend(books)

            print(f"Страница {page + 1}: найдено {len(series)} серий, {len(authors)} авторов, {len(books)} книг")
        else:
            print(f"Не удалось получить страницу {page + 1}")

    # Формируем итоговый результат
    results = {
        'query': query,
        'total_pages': total_pages,
        'series': all_series,
        'authors': all_authors,
        'books': all_books,
        'stats': {
            'series_count': len(all_series),
            'authors_count': len(all_authors),
            'books_count': len(all_books)
        }
    }

    return results


def save_results_to_json(results, filename):
    """
    Сохраняет результаты поиска в JSON-файл.

    Args:
        results (dict): Словарь с результатами поиска
        filename (str): Имя файла для сохранения
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Результаты сохранены в файл: {filename}")


def main():
    # Получаем поисковый запрос от пользователя
    search_query = input("Введите поисковый запрос: ")

    # Формируем URL для поиска
    search_url = build_search_url(search_query)

    # Выводим базовую ссылку для поиска
    print("\nСформированная ссылка для поиска:")
    print(search_url)

    # Запускаем процесс сбора данных со всех страниц
    print("\nНачинаем обработку результатов поиска...")
    results = parse_all_pages(search_query)

    if results:
        # Выводим статистику
        print("\nСбор данных завершен.")
        print(f"Всего найдено серий: {results['stats']['series_count']}")
        print(f"Всего найдено авторов: {results['stats']['authors_count']}")
        print(f"Всего найдено книг: {results['stats']['books_count']}")

        # Сохраняем результаты в JSON-файл
        filename = f"flibusta_search_{search_query.replace(' ', '_')}.json"
        save_results_to_json(results, filename)

        # Спрашиваем, нужно ли собрать подробную информацию о сериях и авторах
        get_details = input("\nСобрать подробную информацию о сериях и авторах? (y/n): ")

        if get_details.lower() == 'y':
            detailed_results = {
                'query': search_query,
                'series_details': [],
                'authors_details': []
            }

            # Собираем информацию о сериях
            if results['series']:
                print("\nСбор информации о сериях...")
                for i, series in enumerate(results['series']):
                    print(f"Обрабатываем серию {i + 1}/{len(results['series'])}: {series['name']}")
                    series_details = get_series_books(series['url'])
                    if series_details:
                        detailed_results['series_details'].append(series_details)
                    # Добавляем задержку между запросами
                    time.sleep(2 + random.random() * 3)

            # Собираем информацию об авторах
            if results['authors']:
                print("\nСбор информации об авторах...")
                for i, author in enumerate(results['authors']):
                    print(f"Обрабатываем автора {i + 1}/{len(results['authors'])}: {author['name']}")
                    author_details = get_author_books(author['url'])
                    if author_details:
                        detailed_results['authors_details'].append(author_details)
                    # Добавляем задержку между запросами
                    time.sleep(2 + random.random() * 3)

            # Сохраняем подробные результаты в JSON-файл
            detailed_filename = f"flibusta_detailed_{search_query.replace(' ', '_')}.json"
            save_results_to_json(detailed_results, detailed_filename)
            print(f"\nПодробные результаты сохранены в файл: {detailed_filename}")
    else:
        print("\nНе удалось собрать данные.")


if __name__ == '__main__':
    main()
