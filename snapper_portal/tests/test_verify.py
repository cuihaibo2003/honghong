import os
import pytest
import allure
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from snapper_portal.utils.email_helper import get_verification_code
import time
from snapper_portal.utils.portal_config import set_email_verification


def test_open_website(browser_context):
    set_email_verification(True)
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
        # Steps2.1: Check the after photo screen UI before uploading the photos
        with allure.step("Check the text on the after photo screen"):
            assert page.locator("text=Help Solvers locate your issue").is_visible(), "Error-No copy is found: Help Solvers locate your issue"
            assert page.locator("text=Add close-ups to show details and wider shots to capture landmarks like buildings or street signs.").is_visible(), "Error-No copy is found: Add close-ups..."
 
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
        with allure.step("Load the Incident location page"):
            page.wait_for_load_state('load')
            page.wait_for_selector('text=Incident location', timeout=10000)
            page.on('dialog', lambda dialog: dialog.accept())  

        allure.attach(
            page.screenshot(),
            name="After fill incident location",
            attachment_type=allure.attachment_type.PNG
        )

        # Fill out a new locatoin
        with allure.step("Fill out the incident location"):
            page.get_by_placeholder("Search address").click()
            page.get_by_placeholder("Search address").fill("570 church")
            page.get_by_text("570 Church StreetCremorne VIC, Australia").click()
            page.get_by_role("button", name="Next").click()
            
         # Incident type list page
        with allure.step("Incident type list page"):   
            page.locator("a").filter(has_text="Test blur Snap Send Solve").click()
        with allure.step("Incident details page"):
            
            Details_placeholder = page.locator(".snapper-details__textarea").get_attribute("placeholder") 
            expected_placeholder = "Avoid adding personal details in this description. And keep it respectful, no swearing please." 
            assert Details_placeholder == expected_placeholder, f"Details placeholder text is incorrect. Found: {Details_placeholder}, Expected: {expected_placeholder}"     
            
            page.locator(".snapper-details__textarea").click()
            page.locator(".snapper-details__textarea").fill("test the verification code")
            page.get_by_role("button", name="Next").click()
            
            
            
        with allure.step("Your details screen"):    
    
            page.locator("input[name='firstName']").fill("test")
            page.locator("input[name='lastName']").fill("test")
            page.locator("input[name='email']").fill("haibo.cui@snapsendsolve.com")
            
            page.get_by_role("button", name="Next").click()
            
        with allure.step("Confirm details screen"):   
            
            confirm_title = page.locator(".snapper__main-title").inner_text()
            assert confirm_title == "Confirm details", f"Title mismatch: {confirm_title}"
            
            next_button = page.locator("button", has_text="next")    
            expect(next_button).to_be_visible(timeout=10000)
            expect(next_button).to_be_enabled(timeout=10000)
            next_button.click()
            
        with allure.step("One last step screen"):
            # Get the verification code and the session value
            page.wait_for_load_state("networkidle")
            locator = page.locator("text=Verify your email address")
            locator.first.wait_for(state="visible", timeout=10000)
            assert locator.first.is_visible(), "Text 'Verify your email address' not found on page"
            time.sleep(5)
            verification_code = get_verification_code() 
            print(f"Extracted Verification Code: {verification_code}")
            session_value = page.evaluate("() => sessionStorage.getItem('EVuuid')")
            print(f"SessionStorage uuid value: {session_value}")
            

            # Fill out the verification code on the "One last step screen"
            
        with allure.step("Fill in the incorrect verification code"):
            # Find the input fields on the page
            input_elements = page.locator('.code-input-container input')

            # Get the number of the input fields on the page
            input_elements_count = input_elements.count()

            # Fill out the fields with '0' (incorrect verification code)
            for i in range(input_elements_count): 
                input_element = input_elements.nth(i)  # Get the i-th input element
                input_element.click()
                input_element.type('0')  # Fill '0' in each input field
            
            # Locate the error message
            error_message_locator = page.locator(".code-error-tips")  # Adjust this locator to match the actual error message
            
      
            # Check if the error message appears
            error_message_locator.wait_for(state="visible", timeout=5000)  # Wait for the error message to be visible within 5 seconds
            # Assert that the error message text matches the expected one
            assert error_message_locator.inner_text() == "Invalid code, please try again.", "Error message text is incorrect"
            
            # Optionally, check if the error icon exists (if you want to validate the presence of the icon)
            error_icon_locator = page.locator(".code-error-tips img[src='/images/4codeError.svg']")
            assert error_icon_locator.is_visible(), "Error icon is not visible"
            
            print("Error message and icon are displayed correctly.")
      
            
        with allure.step("Fill in the correct verification code"):
            # Find the input fields on the page
            input_elements = page.locator('.code-input-container input')

            # get the number of the input fields on the page
            input_elements_count = input_elements.count()

            # fill out the number
            for i in range(input_elements_count): 
                input_element = input_elements.nth(i)  # get the first input element
                input_element.click()
                input_element.type(verification_code[i])  # fill out the first input

    except Exception as e:
        # If error will catch the screenshot to help check the issue
        if page: 
            allure.attach(
                page.screenshot(),
                name="Error Screenshot",
                attachment_type=allure.attachment_type.PNG
            )
       
        raise e