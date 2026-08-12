import os
import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost/DamnCRUD"
)


def test_tc03_create_contact(logged_in_driver):
    """
    TC-03:
    Memastikan contact baru dapat ditambahkan
    menggunakan data yang valid.
    """

    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # UUID digunakan agar data setiap eksekusi test unik.
    unique_id = uuid.uuid4().hex[:8]

    name = f"UAS Tester {unique_id}"
    email = f"uas_{unique_id}@example.com"
    phone = "081234567890"
    title = "QA Tester"

    # 1. Membuka halaman Add New Contact.
    driver.get(f"{BASE_URL}/create.php")

    # 2. Mengisi seluruh field menggunakan data valid.
    driver.find_element(
        By.ID,
        "name"
    ).send_keys(name)

    driver.find_element(
        By.ID,
        "email"
    ).send_keys(email)

    driver.find_element(
        By.ID,
        "phone"
    ).send_keys(phone)

    driver.find_element(
        By.ID,
        "title"
    ).send_keys(title)

    # 3. Menekan tombol Save.
    driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][value='Save']"
    ).click()

    # 4. Memastikan aplikasi kembali ke Dashboard.
    wait.until(
        EC.url_contains("index.php")
    )

    assert "index.php" in driver.current_url

    # 5. Menggunakan Search DataTable untuk mencari
    # contact yang baru saja dibuat.
    search_box = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "#employee_filter input[type='search']"
            )
        )
    )

    search_box.send_keys(email)

    # 6. Memastikan contact baru tampil pada tabel.
    def contact_is_displayed(browser):
        rows = browser.find_elements(
            By.CSS_SELECTOR,
            "#employee tbody tr"
        )

        return any(
            email in row.text
            for row in rows
            if row.is_displayed()
        )

    wait.until(contact_is_displayed)

    visible_rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#employee tbody tr"
    )

    assert any(
        name in row.text and email in row.text
        for row in visible_rows
        if row.is_displayed()
    )


#TC 4 
def test_tc04_required_field_validation(logged_in_driver):
    """
    TC-04:
    Memastikan form Add New Contact tidak dapat disubmit
    ketika salah satu field wajib dikosongkan.
    """

    driver = logged_in_driver

    # 1. Membuka halaman Add New Contact.
    driver.get(f"{BASE_URL}/create.php")

    # 2. Field Name sengaja dibiarkan kosong.
    name_field = driver.find_element(
        By.ID,
        "name"
    )

    # 3. Mengisi field wajib lainnya.
    driver.find_element(
        By.ID,
        "email"
    ).send_keys("required_test@example.com")

    driver.find_element(
        By.ID,
        "phone"
    ).send_keys("081111111111")

    driver.find_element(
        By.ID,
        "title"
    ).send_keys("Tester")

    # 4. Menekan tombol Save.
    driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][value='Save']"
    ).click()

    # 5. Mengecek validasi HTML5 pada field Name.
    value_missing = driver.execute_script(
        "return arguments[0].validity.valueMissing;",
        name_field
    )

    # 6. Assertion:
    # Name harus terdeteksi kosong dan form tidak berpindah
    # ke Dashboard.
    assert value_missing is True
    assert "create.php" in driver.current_url


#TC 5
def test_tc05_update_contact(logged_in_driver):
    """
    TC-05:
    Memastikan data contact dapat diperbarui
    dan perubahan tampil pada Dashboard.
    """

    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # Membuat data unik agar tidak bertabrakan
    # dengan data dari eksekusi sebelumnya.
    unique_id = uuid.uuid4().hex[:8]

    original_name = f"Update Tester {unique_id}"
    original_email = f"before_{unique_id}@example.com"

    updated_name = f"Updated Tester {unique_id}"
    updated_email = f"after_{unique_id}@example.com"
    updated_phone = "089999999999"
    updated_title = "Senior QA"

    # ==========================================
    # 1. Membuat contact sebagai data awal
    # ==========================================

    driver.get(f"{BASE_URL}/create.php")

    driver.find_element(
        By.ID, "name"
    ).send_keys(original_name)

    driver.find_element(
        By.ID, "email"
    ).send_keys(original_email)

    driver.find_element(
        By.ID, "phone"
    ).send_keys("081234567890")

    driver.find_element(
        By.ID, "title"
    ).send_keys("QA Tester")

    driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][value='Save']"
    ).click()

    wait.until(
        EC.url_contains("index.php")
    )

    # ==========================================
    # 2. Mencari contact yang baru dibuat
    # ==========================================

    search_box = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "#employee_filter input[type='search']"
            )
        )
    )

    search_box.send_keys(original_email)

    def find_original_row(browser):
        rows = browser.find_elements(
            By.CSS_SELECTOR,
            "#employee tbody tr"
        )

        for row in rows:
            if (
                row.is_displayed()
                and original_email in row.text
            ):
                return row

        return False

    contact_row = wait.until(find_original_row)

    # ==========================================
    # 3. Klik tombol Edit
    # ==========================================

    edit_button = contact_row.find_element(
        By.CSS_SELECTOR,
        "a[href^='update.php?id=']"
    )

    edit_button.click()

    wait.until(
        EC.url_contains("update.php")
    )

    # ==========================================
    # 4. Mengubah data contact
    # ==========================================

    name_field = driver.find_element(By.ID, "name")
    email_field = driver.find_element(By.ID, "email")
    phone_field = driver.find_element(By.ID, "phone")
    title_field = driver.find_element(By.ID, "title")

    name_field.clear()
    name_field.send_keys(updated_name)

    email_field.clear()
    email_field.send_keys(updated_email)

    phone_field.clear()
    phone_field.send_keys(updated_phone)

    title_field.clear()
    title_field.send_keys(updated_title)

    # ==========================================
    # 5. Klik Update
    # ==========================================

    driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][value='Update']"
    ).click()

    wait.until(
        EC.url_contains("index.php")
    )

    # ==========================================
    # 6. Cari data yang sudah diperbarui
    # ==========================================

    search_box = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "#employee_filter input[type='search']"
            )
        )
    )

    search_box.send_keys(updated_email)

    def updated_contact_is_displayed(browser):
        rows = browser.find_elements(
            By.CSS_SELECTOR,
            "#employee tbody tr"
        )

        for row in rows:
            if (
                row.is_displayed()
                and updated_email in row.text
            ):
                return row

        return False

    updated_row = wait.until(
        updated_contact_is_displayed
    )

    # ==========================================
    # 7. Assertion
    # ==========================================

    assert updated_name in updated_row.text
    assert updated_email in updated_row.text
    assert updated_phone in updated_row.text
    assert updated_title in updated_row.text


#TC 8
def test_tc08_search_contact(logged_in_driver):
    """
    TC-08:
    Memastikan fitur Search pada Dashboard dapat
    menemukan contact berdasarkan kata kunci.
    """

    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # Membuat data unik agar mudah dicari
    # dan tidak bertabrakan dengan test lain.
    unique_id = uuid.uuid4().hex[:8]

    name = f"Search Tester {unique_id}"
    email = f"search_{unique_id}@example.com"
    phone = "082222222222"
    title = "Search QA"

    # ==========================================
    # 1. Membuat contact sebagai data awal
    # ==========================================

    driver.get(f"{BASE_URL}/create.php")

    driver.find_element(
        By.ID, "name"
    ).send_keys(name)

    driver.find_element(
        By.ID, "email"
    ).send_keys(email)

    driver.find_element(
        By.ID, "phone"
    ).send_keys(phone)

    driver.find_element(
        By.ID, "title"
    ).send_keys(title)

    driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][value='Save']"
    ).click()

    wait.until(
        EC.url_contains("index.php")
    )

    # ==========================================
    # 2. Mencari contact melalui Search DataTable
    # ==========================================

    search_box = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "#employee_filter input[type='search']"
            )
        )
    )

    search_box.clear()
    search_box.send_keys(email)

    # ==========================================
    # 3. Menunggu hasil filtering
    # ==========================================

    def search_result_found(browser):
        rows = browser.find_elements(
            By.CSS_SELECTOR,
            "#employee tbody tr"
        )

        return any(
            row.is_displayed() and email in row.text
            for row in rows
        )

    wait.until(search_result_found)

    # ==========================================
    # 4. Assertion
    # ==========================================

    visible_rows = [
        row
        for row in driver.find_elements(
            By.CSS_SELECTOR,
            "#employee tbody tr"
        )
        if row.is_displayed()
    ]

    assert len(visible_rows) >= 1

    assert any(
        email in row.text
        and name in row.text
        for row in visible_rows
    )


#TC 10
def test_tc10_invalid_profile_upload(logged_in_driver, tmp_path):
    """
    TC-10:
    Memastikan file dengan ekstensi selain JPG/JPEG
    ditolak ketika di-upload sebagai foto profil.
    """

    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # ==========================================
    # 1. Membuka halaman Profil
    # ==========================================

    driver.get(f"{BASE_URL}/profil.php")

    # ==========================================
    # 2. Membuat file PNG sementara
    # ==========================================
    # tmp_path adalah fixture bawaan Pytest.
    # File ini hanya digunakan selama test berlangsung.

    invalid_file = tmp_path / "invalid_profile.png"
    invalid_file.write_bytes(b"dummy png file for selenium test")

    # ==========================================
    # 3. Memilih file pada input upload
    # ==========================================

    file_input = wait.until(
        EC.presence_of_element_located(
            (By.ID, "formFile")
        )
    )

    file_input.send_keys(str(invalid_file))

    # ==========================================
    # 4. Menekan tombol Change / Submit
    # ==========================================

    driver.find_element(
        By.CSS_SELECTOR,
        "form button[type='submit']"
    ).click()

    # ==========================================
    # 5. Memastikan pesan penolakan muncul
    # ==========================================

    expected_message = (
        "Ekstensi tidak diijinkan. "
        "Hanya menerima file JPG/JPEG"
    )

    wait.until(
        lambda browser:
        expected_message in browser.page_source
    )

    # ==========================================
    # 6. Assertion
    # ==========================================

    assert expected_message in driver.page_source