import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def normalize_text(s: str) -> str:
    # Нормализация пробелов и неразрывных пробелов
    for ch in ("\u00A0", "\u202F", "\u2009"):
        s = s.replace(ch, " ")
    return re.sub(r"\s+", " ", s).strip()

def wait_visible_clickable(wait: WebDriverWait, by: By, selector: str):
    # Ожидать видимость и кликабельность элемента
    el = wait.until(EC.visibility_of_element_located((by, selector)))
    wait.until(EC.element_to_be_clickable((by, selector)))
    return el

def test_oxygen_value_on_earth_page(driver):
    # Шаг 1: Открыть главную страницу Википедии
    driver.get("https://ru.wikipedia.org")
    wait = WebDriverWait(driver, 8)

    # Шаг 2: Найти строку поиска и ввести запрос "Земля", затем выполнить поиск
    search_input = wait_visible_clickable(wait, By.ID, "searchInput")
    search_input.clear()
    search_input.send_keys("Земля")
    search_input.send_keys(Keys.RETURN)

    # Шаг 3: На странице результатов найти и перейти по ссылке на статью "Земля"
    # С короткими ожиданиями для ускорения
    try:
        heading = WebDriverWait(driver, 4).until(EC.visibility_of_element_located((By.ID, "firstHeading")))
        if normalize_text(heading.text) != "Земля":
            earth_link = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.LINK_TEXT, "Земля")))
            earth_link.click()
    except Exception:
        earth_link = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.LINK_TEXT, "Земля")))
        earth_link.click()
    # Подтвердить загрузку страницы статьи
    WebDriverWait(driver, 6).until(EC.text_to_be_present_in_element((By.ID, "firstHeading"), "Земля"))

    # Шаг 4: На странице "Земля" найти элемент, где упоминается "Кислород",
    # и проверить, что рядом с ним указано значение 20,95
    found = False

    # Попытка 1: быстрый поиск строки таблицы (без явного ожидания)
    rows = driver.find_elements(
        By.XPATH,
        "//table[contains(@class,'infobox') or contains(@class,'wikitable')]//*[contains(normalize-space(.), 'Кислород')]/ancestor::tr[1]",
    )
    if rows:
        row_text = normalize_text(rows[0].text)
        if re.search(r"(?<!\d)20,95\s*%?(?!\d)", row_text):
            found = True

    # Попытка 2 (резерв): поиск близости слов по всей странице
    if not found:
        page_text = normalize_text(driver.find_element(By.TAG_NAME, "body").get_attribute("innerText"))
        if re.search(r"Кислород.{0,120}20,95|20,95.{0,120}Кислород", page_text, flags=re.IGNORECASE | re.DOTALL):
            found = True

    # Шаг 5: Если текст найден — тест проходит успешно, если нет — падает с сообщением
    assert found, "На странице 'Земля' не найдено упоминание 'Кислород' со значением 20,95 %."