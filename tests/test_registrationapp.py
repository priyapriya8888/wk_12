import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import time
import requests
import signal


# ------------------------------------------------------------
# Fixture: Start Flask app before all tests and stop after
# ------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def start_flask_app():
    """
    Start the Flask app before running tests and stop it afterwards.
    """
    print("\n🚀 Starting Flask app...")
    process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # required for Windows
    )

    # Wait and capture logs to confirm it's running
    started = False
    for i in range(10):  # try for ~10 seconds
        line = process.stdout.readline()
        if line:
            print(f"   [Flask] {line.strip()}")
            if "Running on http://" in line:
                started = True
                break
        time.sleep(1)

    if not started:
        process.kill()
        pytest.fail("❌ Flask app did not start properly. Check app.py for errors.")

    print("✅ Flask app is running at http://127.0.0.1:5000")

    yield  # run all tests

    # Stop Flask after all tests
    print("\n🛑 Shutting down Flask app...")
    try:
        process.send_signal(signal.CTRL_BREAK_EVENT)
        time.sleep(2)
        process.kill()
        print("✅ Flask app stopped.")
    except Exception as e:
        print(f"⚠️ Error stopping Flask app: {e}")


# ------------------------------------------------------------
# Fixture: Selenium WebDriver setup/teardown
# ------------------------------------------------------------
@pytest.fixture
def setup_teardown():
    """
    Setup Selenium WebDriver with automatic ChromeDriver version.
    """
    print("\n🔧 Launching Chrome browser...")

    chrome_options = Options()
    # Uncomment the next line if running inside Jenkins or headless
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # ✅ Automatically installs the matching ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.maximize_window()
    yield driver
    print("🧹 Closing browser...")
    driver.quit()


# ------------------------------------------------------------
# Helper: Handle alert safely
# ------------------------------------------------------------
def get_alert_text(driver):
    alert = Alert(driver)
    text = alert.text
    alert.accept()
    return text


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def test_empty_username(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "pwd").send_keys("Password123")
    driver.find_element(By.NAME, "sb").click()

    time.sleep(1)
    alert_text = get_alert_text(driver)
    assert alert_text == "Username cannot be empty."


def test_empty_password(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    driver.find_element(By.NAME, "username").send_keys("John Doe")
    driver.find_element(By.NAME, "pwd").clear()
    driver.find_element(By.NAME, "sb").click()

    time.sleep(1)
    alert_text = get_alert_text(driver)
    assert alert_text == "Password cannot be empty."


def test_short_password(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    driver.find_element(By.NAME, "username").send_keys("Jane")
    driver.find_element(By.NAME, "pwd").send_keys("abc1")
    driver.find_element(By.NAME, "sb").click()

    time.sleep(1)
    alert_text = get_alert_text(driver)
    assert alert_text == "Password must be atleast 6 characters long."


def test_valid_input(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    driver.find_element(By.NAME, "username").send_keys("Alice")
    driver.find_element(By.NAME, "pwd").send_keys("abc123")
    driver.find_element(By.NAME, "sb").click()

    time.sleep(2)
    current_url = driver.current_url
    assert "/submit" in current_url, f"Expected redirect to greeting page, got: {current_url}"

    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Hello, Alice! Welcome to the website" in body_text, f"Greeting missing: {body_text}"
