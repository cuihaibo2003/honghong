import os
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright

class AddPhotoPage:
    def __init__(self, page: Page):
        self.page = page
        self.upload_button = page.locator("#sss-upload-btn")
        self.next_button = page.locator("button:has-text('Next')")
        self.title_text = "Help Solvers locate your issue"
        self.description_text = "Add close-ups to show details and wider shots to capture landmarks like buildings or street signs."
        self.warning_text = "Avoid adding personal details or identifying business information."

        # Config photo path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_folder = os.path.normpath(os.path.join(current_dir, '..', 'test_data', 'images'))

    def open(self, url: str):
        self.page.goto(url, timeout=10000)


    def check_texts(self):
        assert self.page.locator(f"text={self.title_text}").is_visible(), f"Error - Missing title text: '{self.title_text}'"
        assert self.page.locator(f"text={self.description_text}").is_visible(), f"Error - Missing description text: '{self.description_text}'"
        assert self.page.locator(f"text={self.warning_text}").is_visible(), f"Error - Missing warning text: '{self.warning_text}'"

    def upload_photos(self, filenames: list[str]):
        image_paths = [os.path.join(self.image_folder, name) for name in filenames]
        for path in image_paths:
            assert os.path.exists(path), f"File not found: {path}"

        with self.page.expect_file_chooser() as file_chooser_info:
            self.upload_button.click()
            file_chooser = file_chooser_info.value
            file_chooser.set_files(image_paths)
        self.page.wait_for_timeout(3000)

    def click_next(self):
        self.next_button.click()
        
if __name__ == "__main__":
    def run_test():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            add_photo_page = AddPhotoPage(page)
            add_photo_page.open("https://me-dev-1.snapsendsolve.com/snap")
            add_photo_page.check_texts()
            
            # Add photo
            add_photo_page.upload_photos(["photo1.jpg", "photo2.jpg"])     
            add_photo_page.click_next()
            print("AddPhotoPage test completed.")
  

    run_test()