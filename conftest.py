import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def driver():
    # Инициализация Chrome WebDriver
    options = Options()
    # Включить безголовый режим при HEADLESS=1
    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    # Рекомендуемые флаги для стабильности в CI/VM
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 900)
    yield driver
    driver.quit()