import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def normalize_text(s: str) -> str:
    # Нормализация пробелов и неразрывных пробелов, приведение к единому виду
    for ch in ("\u00A0", "\u202F", "\u2009"):
        s = s.replace(ch, " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def wait_visible_clickable(wait: WebDriverWait, by: By, selector: str):
    el = wait.until(EC.visibility_of_element_located((by, selector)))
    wait.until(EC.element_to_be_clickable((by, selector)))
    return el

def test_oxygen_percentage_in_earth_atmosphere(driver):
    # Шаг 1: Открыть главную страницу Википедии
    driver.get("https://ru.wikipedia.org")
    wait = WebDriverWait(driver, 15)

    # Шаг 2: Найти строку поиска, ввести "Земля" и выполнить поиск
    search_input = wait_visible_clickable(wait, By.ID, "searchInput")
    search_input.clear()
    search_input.send_keys("Земля")
    search_input.send_keys(Keys.RETURN)

    # Шаг 3: Перейти в статью "Земля"
    # Возможны два сценария: редирект сразу на статью, либо страница результатов
    try:
        # Если уже на статье "Земля", заголовок будет "Земля"
        heading = wait.until(EC.visibility_of_element_located((By.ID, "firstHeading")))
        if normalize_text(heading.text) != "Земля":
            # Иначе — клик по ссылке "Земля" на странице результатов
            earth_link = wait_visible_clickable(wait, By.LINK_TEXT, "Земля")
            earth_link.click()
            wait.until(EC.text_to_be_present_in_element((By.ID, "firstHeading"), "Земля"))
    except Exception:
        # Запасной вариант: попытаться кликнуть ссылку "Земля" (если заголовок не найден сразу)
        earth_link = wait_visible_clickable(wait, By.LINK_TEXT, "Земля")
        earth_link.click()
        wait.until(EC.text_to_be_present_in_element((By.ID, "firstHeading"), "Земля"))

    # Шаг 4: На странице "Земля" найти и перейти по ссылке "Атмосфера Земли"
    atmosphere_link = wait_visible_clickable(wait, By.LINK_TEXT, "Атмосфера Земли")
    atmosphere_link.click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "firstHeading"), "Атмосфера Земли"))

    # Шаг 5: На странице "Атмосфера Земли" найти и перейти по ссылке "Кислород"
    oxygen_link = wait_visible_clickable(wait, By.LINK_TEXT, "Кислород")
    oxygen_link.click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "firstHeading"), "Кислород"))

    # Шаг 6: Проверить, что на странице есть значение "20,95 %"
    # Берём видимый текст всей страницы и ищем точное значение с запятой и пробелом перед %
    body_text = driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
    body_text = normalize_text(body_text)

    # Возможны варианты написания: "20,95%", "20,95 %", "20,95 % объёма"
    patterns = [
        r"(?<!\d)20,95(?:\s|\u00A0|\u202F|\u2009)?%(?!\d)",
        r"(?<!\d)20,95(?:\s|\u00A0|\u202F|\u2009)?%\s+об",  # покрыть "20,95 % объёма"
    ]

    found = any(re.search(p, body_text, flags=re.IGNORECASE) for p in patterns)

    # Шаг 7: Если текст найден — тест проходит, иначе — падает с сообщением
    assert found, "На странице 'Кислород' не найдено упоминание концентрации свободного кислорода 20,95 % в атмосфере Земли."