import os
import pytest
import allure
from playwright.sync_api import expect
from snapper_portal.utils.email_helper import get_verification_code
import time
from snapper_portal.utils.portal_config import set_authority_config
from snapper_portal.pages.add_photo_page import AddPhotoPage
from snapper_portal.pages.incident_location_page import IncidentLocationPage
from snapper_portal.pages.verification_code_page import VerificationCodePage
from dotenv import load_dotenv

load_dotenv()

def remove_whitespace(text):
    return "".join(text.split())

def test_verification_code_attempt_limit(browser_context):
    set_authority_config("isReportRequireVerification", True)
    set_authority_config("isDuplicatesAvailable", False)
    browser, context = browser_context
    page = None

    try:
        # 定义图片路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path_1 = os.path.normpath(os.path.join(current_dir, '..', 'test_data', 'images', 'photo1.jpg'))
        image_path_2 = os.path.normpath(os.path.join(current_dir, '..', 'test_data', 'images', 'photo2.jpg'))

        assert os.path.exists(image_path_1), f"File not found: {image_path_1}"
        assert os.path.exists(image_path_2), f"File not found: {image_path_2}"

        with allure.step("Open the Snapper portal homepage"):
            context.grant_permissions(["geolocation", "notifications", "camera", "microphone"])
            context.set_geolocation({"latitude": -37.8239, "longitude": 145.0027})
            page = context.new_page()
            page.goto(os.getenv("SNAPPER_URL"), timeout=10000)

        with allure.step("Step 1 add photos screen"):
            add_photo_page = AddPhotoPage(page)
            add_photo_page.check_texts()
            add_photo_page.upload_photos(["photo1.jpg", "photo2.jpg"])
            page.wait_for_timeout(3000)
            add_photo_page.click_next()

        with allure.step("Step 2 fill incident address"):
            incident_page = IncidentLocationPage(page)
            incident_page.wait_until_loaded()
            incident_page.fill_address("570 church street Cremorne VIC")
            incident_page.click_next()

        with allure.step("Step 3 select incident type"):
            page.locator("a").filter(has_text="Test blur Snap Send Solve").click()

        with allure.step("Step 4 fill incident details"):
            page.locator(".snapper-details__textarea").fill("This is a test incident")
            page.get_by_role("button", name="Next").click()

        with allure.step("Step 5 your details page"):
            page.locator("input[name='firstName']").fill("test")
            page.locator("input[name='lastName']").fill("test")
            page.locator("input[name='email']").fill("haibo.cui@snapsendsolve.com")
            page.get_by_role("button", name="Next").click()

        with allure.step("step 6 verify email page"):
            next_button = page.locator("button", has_text="next")
            expect(next_button).to_be_visible(timeout=10000)
            expect(next_button).to_be_enabled(timeout=10000)
            next_button.click()

        with allure.step("step 7 verify email page loaded"):
            verification_page = VerificationCodePage(page)
            verification_page.wait_until_loaded()
            time.sleep(5)  # wait for the verification code to be sent

        with allure.step("step 8 Fill in the 5 times incorrect code"):
            verification_page.enter_multiple_wrong_codes(5)

        with allure.step("Verify the Too Many Attempts prompt"):
            verification_page.wait_until_too_many_attempts()

        with allure.step("Click the Start a new report button and verify the page"):
            verification_page.click_start_new_report()
            expect(page.locator("text=Add photo")).to_be_visible(timeout=5000)

    except Exception as e:
        if page:
            allure.attach(page.screenshot(), name="Error Screenshot", attachment_type=allure.attachment_type.PNG)
        raise e