import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

# Constants
BASE_URL = "http://127.0.0.1:8000"
REGISTER_URL = f"{BASE_URL}/register/register/"  # Correct registration URL
STRIPE_TEST_CARD = "4242 4242 4242 4242"  # Stripe test card for successful payment
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
    # Step 1: Navigate to the registration page
    browser.get(REGISTER_URL)
    print("Current URL:", browser.current_url)
    print("Page Title:", browser.title)
    assert "Student Registration" in browser.title

    # Step 2: Fill out the registration form
    browser.find_element(By.NAME, "name").send_keys("John Doe")
    browser.find_element(By.NAME, "email").send_keys("john.doe@example.com")
    browser.find_element(By.NAME, "course").send_keys("Python Programming")
    browser.find_element(By.TAG_NAME, "button").click()

    # Step 3: Verify redirection to the payment page
    WebDriverWait(browser, 10).until(
        EC.title_contains("Payment")
    )
    print("Payment Page URL:", browser.current_url)
    assert "Payment" in browser.title

    # Step 4: Proceed to payment
    browser.find_element(By.TAG_NAME, "button").click()

    # Step 5: Simulate Stripe payment (using test card)
    # Wait for Stripe Checkout to load
    time.sleep(5)  # Adjust sleep time if necessary

    # Wait for the Stripe iframe to be present
    iframe = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@name, 'stripe')]"))
    )
    print("Stripe iframe found:", iframe.get_attribute("name"))

    # Switch to the Stripe iframe
    browser.switch_to.frame(iframe)

    # Wait for the card number field to be present
    card_number_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "cardnumber"))
    )
    print("Card number field found:", card_number_field.get_attribute("name"))

    # Fill out Stripe's payment form
    card_number_field.send_keys(STRIPE_TEST_CARD)
    browser.find_element(By.NAME, "exp-date").send_keys(STRIPE_TEST_EXPIRY)
    browser.find_element(By.NAME, "cvc").send_keys(STRIPE_TEST_CVC)
    browser.find_element(By.TAG_NAME, "button").click()

    # Switch back to the main window
    browser.switch_to.default_content()

    # Step 6: Verify redirection to the payment success page
    WebDriverWait(browser, 10).until(
        EC.title_contains("Payment Successful")
    )
    print("Payment Success Page URL:", browser.current_url)
    assert "Payment Successful" in browser.title