import pytest
from playwright.sync_api import sync_playwright

# Fixture to manage the browser context for the tests
@pytest.fixture(scope="session")
def browser_context():
    # Using Playwright to launch the browser
    with sync_playwright() as p:
        # Launch Chromium browser with the settings provided
        browser = p.chromium.launch(headless=False, slow_mo=1000)  # Slow motion for debugging
        context = browser.new_context()  # Create a new browser context
        # Grant permissions for geolocation, notifications, camera, and microphone
        context.grant_permissions(["geolocation", "notifications", "camera", "microphone"], 
                                  origin="https://me-dev-1.snapsendsolve.com")
        
        # Yield browser and context to tests so they can use it
        yield browser, context
        
        # Teardown: Close the browser after all tests are done
        browser.close()

# Fixture to initialize a new page for each test case
@pytest.fixture
def page(browser_context):
    browser, context = browser_context  # Retrieve browser and context from the fixture
    page = context.new_page()  # Create a new page
    yield page  # Return the page for test to interact with
    
    # Teardown: Close the page after test execution
    page.close()

# Fixture to clean up any leftover resources after all tests have finished

@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    # Cleanup actions to be executed after each test
    print("Test completed. Performing cleanup tasks.")