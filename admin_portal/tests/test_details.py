import pytest
from playwright.sync_api import sync_playwright
import allure

# test url
URL = "https://me-dev-1.snapsendsolve.com/report/rw3xw4"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # if true no head
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)
    yield page
    context.close()

def test_check_elements(page):

    try:
        with allure.step("Check the copy on the page"):
            text_to_check_1 = "This Snap is no longer available"
            text_to_check_2 = "It may have been set to private or cancelled by the Snapper."

            page_text = page.locator("body").text_content()

            assert text_to_check_1 in page_text, f"error no such copy: {text_to_check_1}"
            assert text_to_check_2 in page_text, f"error no such copy: {text_to_check_2}"

    except Exception as e:
        raise e

    finally:
        # Ensure browser is closed properly in case of failure
        if 'browser' in locals():
            browser.close()
        
        
