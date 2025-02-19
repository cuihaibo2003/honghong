import os
import pytest
import allure
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.grant_permissions(["geolocation"], origin="https://me-dev-1.snapsendsolve.com")
        yield browser, context  
        browser.close()

def test_open_website(browser_context):
    browser, context = browser_context  # return browser and context from  fixture 
    page = None  
    try:
        # Return the current folder，and define the photo's path.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path_1 = os.path.normpath(os.path.join(current_dir, '..', 'test_data', 'images', 'photo1.jpg'))
        image_path_2 = os.path.normpath(os.path.join(current_dir, '..', 'test_data', 'images', 'photo2.jpg'))

        # Check whether have the photos
        assert os.path.exists(image_path_1), f"File not found: {image_path_1}"
        assert os.path.exists(image_path_2), f"File not found: {image_path_2}"

        # Step1: Open the website
        with allure.step("Open the Snapper portal first step page"):
            # Set the locatioin permisstion
            context.grant_permissions(["geolocation", "notifications", "camera", "microphone"])
            context.set_geolocation({"latitude": -37.8239, "longitude": 145.0027})  # Config the default current location
            page = context.new_page()
            page.goto("https://me-dev-1.snapsendsolve.com/snap", timeout=10000)

        # Steps2: Add photos screen testing
 
        with allure.step("Upload photos on the add photo screen"):
            # Wait for the file chooser
            with page.expect_file_chooser() as file_chooser_info: # file chooser 
                page.locator("#sss-upload-btn").click()  # Click the add photo button
                file_chooser = file_chooser_info.value
                file_chooser.set_files([image_path_1, image_path_2])

        # wait for uploading the photos
        print("Before waiting...")
        page.wait_for_timeout(3000)
        print("After waiting...")
    
        # wait for uploading the photos
        allure.attach(
            page.screenshot(),
            name="After Photo Upload",
            attachment_type=allure.attachment_type.PNG
        )

        # Click the next button go to the incident location screen
        with allure.step("Click the Next button"):
            next_button = page.locator("button:has-text('Next')")
            next_button.click()

        # Wait for the “Incident location” screen loaded
        with allure.step("Incident location page"):
            page.wait_for_load_state('load')
            page.wait_for_selector('text=Incident location', timeout=10000)
            page.on('dialog', lambda dialog: dialog.accept())  

        allure.attach(
            page.screenshot(),
            name="After fill incident location",
            attachment_type=allure.attachment_type.PNG
        )

        # Fill out a new locatoin
        with allure.step("Incident location page2"):
            page.get_by_placeholder("Search address").click()
            page.get_by_placeholder("Search address").fill("570 church")
            page.get_by_text("570 Church StreetCremorne VIC, Australia").click()
            page.get_by_role("button", name="Next").click()
            
         # Incident type list page
        with allure.step("Incident type list page"):   
            page.locator("a").filter(has_text="Test blur Snap Send Solve").click()
            page.get_by_placeholder("No swear words, please — a").click()
            page.get_by_placeholder("No swear words, please — a").fill("test")
            page.get_by_role("button", name="Next").click()
            
            
            
        with allure.step("Your details screen"):    
            page.get_by_placeholder("First name").click()
            page.get_by_placeholder("First name").fill("test")
            page.get_by_placeholder("Last name").click()
            page.get_by_placeholder("Last name").fill("test")
            page.get_by_placeholder("Email address").click()
            page.get_by_placeholder("Email address").fill("haibo.cui@snapsendsolve.com")
            page.get_by_role("button", name="Next").click()
            page.get_by_role("button", name="Send").click()

    except Exception as e:
        # If error will catch the screenshot to help check the issue
        if page: 
            allure.attach(
                page.screenshot(),
                name="Error Screenshot",
                attachment_type=allure.attachment_type.PNG
            )
       
        raise e