from playwright.sync_api import Page

class VerificationCodePage:
    def __init__(self, page: Page):
        self.page = page
        self.code_inputs = page.locator(".code-input-container input")
        self.error_message = page.locator(".code-error-tips")
        self.error_icon = page.locator(".code-error-tips img[src='/images/4codeError.svg']")
        self.title = page.locator("text=Verify your email address")
        self.instruction_text = page.locator("text=Please enter the 4-digit code sent to")
        self.expiry_text = page.locator("text=This code expires in 60 minutes.")
        self.resend_link = page.locator("text=Resend")
        self.change_email_link = page.locator("text=Change email address")
        self.too_many_attempts_message = page.locator("text=Too Many Attempts")
        self.too_many_attempts_detail = page.locator(
            "text=You’ve entered the code incorrectly too many times. For your security, the session has timed out."
        )
        self.start_new_report_button = page.get_by_role("button", name="Start a new report")

    def wait_until_loaded(self):
        self.page.wait_for_load_state("networkidle")
        self.title.wait_for(state="visible", timeout=10000)
        assert self.title.is_visible(), "Verify email screen not loaded"

    def verify_instruction_text(self, expected_email: str):
        """验证提示文字中包含正确的邮箱地址，并且过期提示显示"""
        self.instruction_text.wait_for(state="visible", timeout=5000)
        text = self.instruction_text.inner_text()
        assert expected_email in text, f"提示文字中未包含预期邮箱 {expected_email}"
        self.expiry_text.wait_for(state="visible", timeout=5000)
        assert self.expiry_text.is_visible(), "过期时间提示未显示"

    def click_resend(self):
        """点击‘Resend’链接"""
        self.resend_link.wait_for(state="visible", timeout=5000)
        self.resend_link.click()

    def click_change_email(self):
        """点击‘Change email address’链接"""
        self.change_email_link.wait_for(state="visible", timeout=5000)
        self.change_email_link.click()

    def enter_code(self, code: str):
        """输入验证码（正确或错误）"""
        for i in range(len(code)):
            input_field = self.code_inputs.nth(i)
            input_field.click()
            input_field.fill(code[i])

    def enter_incorrect_code_and_check_error(self):
        """输入错误验证码并检查错误提示和图标"""
        count = self.code_inputs.count()
        self.enter_code("0" * count)
        
        self.error_message.wait_for(state="visible", timeout=5000)
        actual_error = self.error_message.inner_text()
        print(f"实际错误提示是: {actual_error}")

        # 使用包含断言代替完全匹配
        assert "Invalid code" in actual_error, f"错误提示不包含 'Invalid code'，实际为: {actual_error}"
        assert "please try again" in actual_error, f"错误提示不包含 'please try again'，实际为: {actual_error}"
        
        assert self.error_icon.is_visible(), "错误图标未显示"
        print("错误提示和图标都正确显示")

    def enter_correct_code(self, correct_code: str):
        # fill out the correct verification code
        self.enter_code(correct_code)

    def wait_until_too_many_attempts(self):
        """wait the "Too Many Attempts module"""
        self.too_many_attempts_message.wait_for(state="visible", timeout=5000)
        self.too_many_attempts_detail.wait_for(state="visible", timeout=5000)
        assert self.too_many_attempts_message.is_visible(), "'Too Many Attempts'提示未显示"
        assert self.too_many_attempts_detail.is_visible(), "详细超时提示未显示"

    def click_start_new_report(self):
        """点击‘Start a new report’按钮重新开始"""
        self.start_new_report_button.wait_for(state="visible", timeout=5000)
        assert self.start_new_report_button.is_enabled(), "‘Start a new report’按钮不可用"
        self.start_new_report_button.click()