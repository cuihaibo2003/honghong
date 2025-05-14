import requests
from dotenv import load_dotenv
import os
import logging

# Config log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

load_dotenv()

PORTAL_API_URL = "https://portal-api-dev.snapsendsolve.com"
AUTHORITY_ID = 777  # authority id

# 配置用户名和密码
USERNAME = os.getenv("PORTAL_USERNAME")
PASSWORD = os.getenv("PORTAL_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("Missing credentials: Please configure PORTAL_USERNAME and PORTAL_PASSWORD in the .env file.")

def _login_and_get_token() -> str:
    url = f"{PORTAL_API_URL}/auth/login"
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    response = requests.post(url, json=payload)
    logger.debug(f"Login Response Status: {response.status_code}")
    logger.debug(f"Login Response Text: {response.text}")

    response.raise_for_status()

    data = response.json()
    access_token = data.get("accessToken")
    if not access_token:
        raise ValueError("Login failed: no accessToken returned")
    
    return access_token

def clear_authority_cache(authority_id: int, token: str) -> None:
    url = f"{PORTAL_API_URL}/authorities/{authority_id}/cache"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        logger.info(f"[OK] Cache cleared for authority {authority_id}.")
    except requests.RequestException as e:
        logger.error(f"[FAIL] Failed to clear cache for authority {authority_id}: {e}")
        raise

def set_email_verification(enabled: bool):
    token = _login_and_get_token()
    url = f"{PORTAL_API_URL}/authorities/{AUTHORITY_ID}"
    payload = {"isReportRequireVerification": enabled}
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"[OK] Email verification is {'enabled' if enabled else 'disabled'}.")
    except requests.RequestException as e:
        logger.error(f"[FAIL] Error: {e}")
        raise
    clear_authority_cache(AUTHORITY_ID, token)

# Test code
if __name__ == "__main__":
    try:
        set_email_verification(True)
    except Exception as e:
        logger.error(f"[Test Failed] {e}")
