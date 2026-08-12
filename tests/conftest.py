import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# URL aplikasi.
# Nilai default digunakan ketika test dijalankan di komputer lokal.
# Nanti pada GitHub Actions bisa diganti melalui environment variable.
BASE_URL = os.getenv("BASE_URL", "http://localhost/DamnCRUD")


@pytest.fixture
def driver():
    """
    Fixture untuk membuat WebDriver Chrome.

    Scope default adalah function, sehingga setiap test case
    mendapatkan browser/session sendiri. Hal ini penting agar
    setiap test bersifat independen dan siap dijalankan paralel.
    """

    options = Options()
    options.add_argument("--window-size=1920,1080")

    # Untuk pengujian lokal browser dibuat terlihat.
    # Pada GitHub Actions nanti HEADLESS=1.
    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Chrome(options=options)

    yield browser

    browser.quit()


@pytest.fixture
def logged_in_driver(driver):
    """
    Melakukan login sebagai precondition.

    Login bukan test case utama, tetapi diperlukan agar pengguna
    dapat mengakses fitur CRUD, Search, dan Profil.
    """

    driver.get(f"{BASE_URL}/login.php")

    wait = WebDriverWait(driver, 10)

    username = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "inputUsername")
        )
    )

    password = driver.find_element(
        By.ID,
        "inputPassword"
    )

    username.send_keys("admin")
    password.send_keys("nimda666!")

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    # Menunggu sampai login selesai dan Dashboard terbuka.
    wait.until(
        EC.url_contains("index.php")
    )

    assert "index.php" in driver.current_url

    return driver