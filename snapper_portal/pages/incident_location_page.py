import allure
from playwright.sync_api import sync_playwright

class IncidentLocationPage:
    def __init__(self, page):
        self.page = page
        self.search_input = page.get_by_placeholder("Search address")
        self.next_button = page.get_by_role("button", name="Next")

    def wait_until_loaded(self):
        with allure.step("Wait for Incident Location page to load"):
            self.page.wait_for_load_state('load')
            self.page.wait_for_selector("text=Incident location", timeout=10000)
            self.page.on('dialog', lambda dialog: dialog.accept())

    def fill_address(self, address: str):
        with allure.step(f"Fill address: {address}"):
            self.search_input.click()
            self.search_input.fill(address)
            self.page.wait_for_selector(".pac-item", timeout=5000)
            if not self.page.locator(".pac-item").first.is_visible():
                raise Exception("No address suggestions found in the dropdown.")
            self.page.locator(".pac-item").first.click()

    def click_next(self):
        with allure.step("Click Next button"):
            self.next_button.click()

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            permissions=["geolocation"],
            geolocation={"longitude": 144.9831, "latitude": -37.8333},
            locale="en-AU"
        )
        page = context.new_page()
        incident_page = IncidentLocationPage(page)

        page.goto("https://me-dev-1.snapsendsolve.com/snap")
        page.get_by_role("button", name="Next").click()

        incident_page.wait_until_loaded()
        incident_page.fill_address("570 church street Cremorne VIC")
        incident_page.take_screenshot("After fill incident location")
        incident_page.click_next()

        print("Incident Location page test completed.")
        browser.close()

if __name__ == "__main__":
    run()