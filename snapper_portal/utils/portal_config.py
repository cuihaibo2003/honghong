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

# Config the user and passwork
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

def set_authority_config(field: str, enabled: bool):
    """
    General function to set any authority-related configuration (like email verification, duplicates, etc.)
    :param field: The field name (e.g., "isReportRequireVerification", "isDuplicatesAvailable")
    :param enabled: Boolean to enable or disable the feature
    """
    token = _login_and_get_token()
    url = f"{PORTAL_API_URL}/authorities/{AUTHORITY_ID}"
    payload = {field: enabled}
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"[OK] {field} is {'enabled' if enabled else 'disabled'}.")
    except requests.RequestException as e:
        logger.error(f"[FAIL] Error: {e}")
        raise
    clear_authority_cache(AUTHORITY_ID, token)
    
def get_authority_detail_field(field_name: str):
    """
    get the field value from the authority details api
    """
    token = _login_and_get_token()
    url = f"{PORTAL_API_URL}/authorities/detail/{AUTHORITY_ID}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if field_name not in data:
            logger.warning(f"[WARN] Field '{field_name}' not found in authority detail.")
            return None
        
        value = data[field_name]
        logger.info(f"[OK] Field '{field_name}' value: {value}")
        return value
    except requests.RequestException as e:
        logger.error(f"[FAIL] Failed to get authority detail: {e}")
        raise

def get_user_profile(token: str) -> dict:
    """
    Get the current user's profile from /users/profile
    :param token: Bearer access token
    :return: Dictionary of profile fields
    """
    url = f"{PORTAL_API_URL}/users/profile"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        profile_data = response.json()
        logger.info(f"[OK] Retrieved user profile: {profile_data}")
        return profile_data
    except requests.RequestException as e:
        logger.error(f"[FAIL] Failed to get user profile: {e}")
        raise


# Test code
if __name__ == "__main__":
    try:
        # Set email verification
        set_authority_config("isReportRequireVerification", True)
        
        # Set duplicates feature
        set_authority_config("isDuplicatesAvailable", False)
        value = get_authority_detail_field("isDuplicatesAvailable")
        assert value is False, "[FAIL] Expected isDuplicatesAvailable to be False"
        print("[PASS] isDuplicatesAvailable set to False correctly.")

        # Set duplicates feature
        set_authority_config("isDuplicatesAvailable", True)
        value = get_authority_detail_field("isDuplicatesAvailable")
        assert value is True, "[FAIL] Expected isDuplicatesAvailable to be True"
        print("[PASS] isDuplicatesAvailable set to True correctly.")
        
    
        

        
    except Exception as e:
        logger.error(f"[Test Failed] {e}")
