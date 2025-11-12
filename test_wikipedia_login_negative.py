import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login_with_invalid_credentials_shows_error(driver):
    # Открыть главную страницу русской Википедии
    driver.get("https://ru.wikipedia.org/")

    # Перейти на страницу входа через ссылку "Войти" (варианты селекторов под разные скины)
    login_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "#pt-login a, #pt-login-2 a, a[href*='Служебная:Вход'], a[title='Войти']"
        ))
    )
    # Клик через JS на случай перекрытий/микролэйаута
    driver.execute_script("arguments[0].click();", login_link)

    # Дождаться формы входа и ввести логин и пароль
    username = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#wpName1"))
    )
    password = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#wpPassword1"))
    )

    # Ввести тестовые неверные данные
    username.clear()
    username.send_keys("VasiliyPupkin")
    password.clear()
    password.send_keys("PupkinVasiliy")

    # Нажать кнопку "Войти"
    submit = driver.find_element(By.CSS_SELECTOR, "#wpLoginAttempt")
    driver.execute_script("arguments[0].click();", submit)

    # Подождать, пока произойдёт одно из двух: появится ошибка ИЛИ отобразится пункт "Выйти"
    def wait_result(d):
        # Возможные контейнеры ошибок
        candidates = d.find_elements(By.CSS_SELECTOR, ".mw-message-box-error, .cdx-message--error, #userloginForm .error")
        for el in candidates:
            if el.is_displayed() and el.text.strip():
                return {"error": el.text.strip()}
        # Признак успешного входа — наличие пункта меню "Выйти"
        logout = d.find_elements(By.CSS_SELECTOR, "#pt-logout a, #pt-logout-2 a")
        if any(x.is_displayed() for x in logout):
            return {"logout": True}
        return False

    result = WebDriverWait(driver, 10).until(wait_result)

    # Проверки результата: ожидаем ошибку и отсутствие входа
    assert "error" in result and result["error"], "Не найдено сообщение об ошибке авторизации."

    error_text = result["error"]
    assert (
        "Введены неверные имя участника или пароль" in error_text
        or "Неверное имя участника или пароль" in error_text
        or "Неверное имя участника" in error_text
        or "Incorrect username or password" in error_text
    ), f"Ожидалась ошибка о неверных данных, получено: '{error_text}'"

    # Убедиться, что не появился пункт "Выйти"
    assert "logout" not in result, "Похоже, выполнен вход в систему, а это не ожидается с неверными данными."