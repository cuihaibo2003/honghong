import os
import pytest
import allure
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from snapper_portal.utils.portal_config import set_authority_config
from snapper_portal.pages.add_photo_page import AddPhotoPage
from snapper_portal.pages.incident_location_page import IncidentLocationPage


def test_open_website(browser_context):
    set_authority_config("isReportRequireVerification", False)
    set_authority_config("isDuplicatesAvailable", False)
    browser, context = browser_context  # return browser and context from  fixture 
    page = None  
    try:

        # Step1: Open the website
        with allure.step("Open the Snapper portal first step page"):
            # Set the locatioin permisstion
            context.grant_permissions(["geolocation", "notifications", "camera", "microphone"])
            context.set_geolocation({"latitude": -37.8239, "longitude": 145.0027})  # Config the default current location
            page = context.new_page()
            page.goto("https://me-dev-1.snapsendsolve.com/snap", timeout=10000)

        # Steps2: Add photos screen testing
        with allure.step("Operate on Add Photo screen"):
            add_photo_page = AddPhotoPage(page)
            add_photo_page.check_texts()
            add_photo_page.upload_photos(["photo1.jpg", "photo2.jpg"])
            page.wait_for_timeout(3000)  
            add_photo_page.click_next()

        # Wait for the “Incident location” screen loaded
        with allure.step("Incident location page"):
            incident_page = IncidentLocationPage(page)
            incident_page.wait_until_loaded()
            incident_page.fill_address("570 church street Cremorne VIC")
            allure.attach(page.screenshot(), name="After fill incident location", attachment_type=allure.attachment_type.PNG)
            incident_page.click_next()
            
         # Incident type list page
        with allure.step("Incident type list page"):   
            page.locator("a").filter(has_text="Test blur Snap Send Solve").click()
        with allure.step("Incident details page"):
            
            Details_placeholder = page.locator(".snapper-details__textarea").get_attribute("placeholder") 
            #expected_placeholder = "Avoid adding personal details or identifying business information in this description. And keep it respectful, no swearing please."
           # assert Details_placeholder == expected_placeholder, f"Details placeholder text is incorrect. Found: {Details_placeholder}, Expected: {expected_placeholder}"     
            
            page.locator(".snapper-details__textarea").click()
            page.locator(".snapper-details__textarea").fill("My address is 123 Fake Street and my phone number is 0412 345 678. If you don’t fix this, I will hurt you badly.")
            page.get_by_role("button", name="Next").click()
            
            
            
        with allure.step("Your details screen"):    
    
            page.locator("input[name='firstName']").fill("test")
            page.locator("input[name='lastName']").fill("test")
            page.locator("input[name='email']").fill("haibo.cui+123@snapsendsolve.com")
            
            page.get_by_role("button", name="Next").click()
            
        with allure.step("Confirm details screen"):   
            
            confirm_title = page.locator(".snapper__main-title").inner_text()
            assert confirm_title == "Confirm details", f"Title mismatch: {confirm_title}"
            
            send_button = page.locator("button", has_text="Send")    
            expect(send_button).to_be_visible(timeout=10000)
            expect(send_button).to_be_enabled(timeout=10000)
            send_button.click()
            
        with allure.step(f"Send screen"):
            # check url
            page.wait_for_load_state("networkidle")
            page.wait_for_url('**/snap-sent', timeout=10000)
            current_url = page.url
            assert page.url.endswith("/snap-sent"), f"URL mismatch: {current_url}"
            

    except Exception as e:
        # If error will catch the screenshot to help check the issue
        if page: 
            allure.attach(
                page.screenshot(),
                name="Error Screenshot",
                attachment_type=allure.attachment_type.PNG
            )
       
        raise e