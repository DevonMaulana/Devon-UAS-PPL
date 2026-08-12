import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost/DamnCRUD"
)


@pytest.fixture
def driver():
    """
    Membuat WebDriver Chrome baru untuk setiap test case.

    Pada local environment Selenium Manager digunakan otomatis.
    Pada GitHub Actions, Chrome dan ChromeDriver dari workflow
    digunakan secara eksplisit agar versinya kompatibel.
    """

    options = Options()
    options.add_argument("--window-size=1920,1080")

    # GitHub Actions tidak memiliki tampilan GUI,
    # sehingga Chrome dijalankan dalam mode headless.
    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # Path Chrome yang diberikan GitHub Actions.
    chrome_binary = os.getenv("CHROME_BIN")

    if chrome_binary:
        options.binary_location = chrome_binary

    # Path ChromeDriver yang diberikan GitHub Actions.
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

    if chromedriver_path:
        service = Service(
            executable_path=chromedriver_path
        )

        browser = webdriver.Chrome(
            service=service,
            options=options
        )
    else:
        # Pada Windows lokal, Selenium Manager akan
        # memilih ChromeDriver yang sesuai secara otomatis.
        browser = webdriver.Chrome(
            options=options
        )

    try:
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def logged_in_driver(driver):
    """
    Login digunakan sebagai precondition.

    Login bukan salah satu dari lima test case utama
    yang diuji pada Soal 3 dan Soal 4.
    """

    driver.get(f"{BASE_URL}/login.php")

    wait = WebDriverWait(driver, 10)

    # Menunggu field username muncul.
    username = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "inputUsername")
        )
    )

    # Mengambil field password.
    password = driver.find_element(
        By.ID,
        "inputPassword"
    )

    # Mengisi kredensial valid.
    username.send_keys("admin")
    password.send_keys("nimda666!")

    # Menekan tombol login.
    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    # Menunggu sampai aplikasi masuk ke Dashboard.
    wait.until(
        EC.url_contains("index.php")
    )

    # Assertion precondition login.
    assert "index.php" in driver.current_url

    return driver