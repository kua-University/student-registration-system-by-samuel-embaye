import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

# Constants
BASE_URL = "http://127.0.0.1:8000"
REGISTER_URL = f"{BASE_URL}/register/register/"  # Correct registration URL
STRIPE_TEST_CARD_SUCCESS = "4242 4242 4242 4242"  # Stripe test card for successful payment
STRIPE_TEST_CARD_FAIL = "4000 0000 0000 0002"
STRIPE_TEST_CVC = "123"
STRIPE_TEST_EXPIRY = "12/28"

@pytest.fixture(scope="module")
def browser():
    # Initialize the browser (e.g., Chrome)
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH
    yield driver
    driver.quit()  # Close the browser after the test

def test_student_registration_and_payment_flow(browser):
    """
    System test for the student registration and payment flow:
    1. Navigate to the registration page.
    2. Fill out and submit the registration form.
    3. Verify redirection to the payment page.
    4. Simulate payment using Stripe's test card.
    5. Verify payment success and database update.
    """
    
    browser.get(REGISTER_URL)
    assert "Student Registration" in browser.title

    browser.find_element(By.NAME, "name").send_keys("Instructor Messele")
    browser.find_element(By.NAME, "email").send_keys("inst.mese@example.com")
    browser.find_element(By.NAME, "course").send_keys("Testing Exam kebid neru")
    browser.find_element(By.TAG_NAME, "button").click()

    WebDriverWait(browser, 10).until(EC.title_contains("Payment"))
    assert "Payment" in browser.title

    browser.find_element(By.TAG_NAME, "button").click()

    time.sleep(5)  # Adjust sleep time if necessary

    # Wait for the Stripe iframe to be present
    iframe = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@name, 'stripe')]"))
    )
    browser.switch_to.frame(iframe)

    card_number_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='cardnumber']"))
    )
    
    card_number_field.send_keys(STRIPE_TEST_CARD_SUCCESS)
    browser.find_element(By.NAME, "exp-date").send_keys(STRIPE_TEST_EXPIRY)
    browser.find_element(By.NAME, "cvc").send_keys(STRIPE_TEST_CVC)
    browser.find_element(By.TAG_NAME, "button").click()

    browser.switch_to.default_content()
    WebDriverWait(browser, 10).until(EC.title_contains("Payment Successful"))
    assert "Payment Successful" in browser.title
    def test_invalid_registration(browser):
    """
    Test invalid registration form submission:
    1. Navigate to the registration page.
    2. Submit an empty form.
    3. Verify form validation errors.
    """
    browser.get(REGISTER_URL)

    browser.find_element(By.TAG_NAME, "button").click()  # Submit without filling fields

    error_messages = WebDriverWait(browser, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "error-message"))
    )

    assert len(error_messages) > 0, "Expected validation errors but found none."

def test_failed_payment_flow(browser):
    """
    Test failed payment flow:
    1. Register a student.
    2. Attempt payment with a declined test card.
    3. Verify redirection to the payment failure page.
    """
    browser.get(REGISTER_URL)
    browser.find_element(By.NAME, "name").send_keys("Test User")
    browser.find_element(By.NAME, "email").send_keys("testuser@example.com")
    browser.find_element(By.NAME, "course").send_keys("Python Testing")
    browser.find_element(By.TAG_NAME, "button").click()

    WebDriverWait(browser, 10).until(EC.title_contains("Payment"))
    browser.find_element(By.TAG_NAME, "button").click()
    time.sleep(5)

    iframe = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@name, 'stripe')]"))
    )
    browser.switch_to.frame(iframe)

    card_number_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='cardnumber']"))
    )

    card_number_field.send_keys(STRIPE_TEST_CARD_FAIL)  # Declined card
    browser.find_element(By.NAME, "exp-date").send_keys(STRIPE_TEST_EXPIRY)
    browser.find_element(By.NAME, "cvc").send_keys(STRIPE_TEST_CVC)
    browser.find_element(By.TAG_NAME, "button").click()

    browser.switch_to.default_content()
    WebDriverWait(browser, 10).until(EC.title_contains("Payment Failed"))
    assert "Payment Failed" in browser.title
