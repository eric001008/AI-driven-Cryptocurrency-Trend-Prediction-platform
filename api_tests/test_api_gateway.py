import pytest
import requests
import uuid


BASE_URL = "http://localhost:5000/api"
# The registration process communicates directly with login_service to get the verification code
LOGIN_SERVICE_URL = "http://localhost:5001/api"



@pytest.fixture(scope="module")
def registered_user():
    """
    This is a fixture that runs once before all tests start.
    Its purpose is to automatically complete the two-step registration process,
    including email verification, and return a brand new, temporary user
    credential that can be used for login.
    """
    print("\n--- [Fixture] Automatically registering a temporary user for testing ---")

    # 1. Prepare new, random user information
    suffix = uuid.uuid4().hex[:8]
    user_data = {
        "email": f"test_user_{suffix}@example.com",
        "password": "A_Complex_Password_123!",
        "username": f"test_user_{suffix}"
    }

    # --- Registration Step 1: Get verification code from the "backdoor" ---
    send_code_url = f"{LOGIN_SERVICE_URL}/send-code"
    send_code_resp = requests.post(send_code_url, json={"email": user_data["email"]})
    assert send_code_resp.status_code == 200, "Failed to request verification code (please confirm login_service has test mode enabled)"
    verification_code = send_code_resp.json()["verification_code"]

    # --- Registration Step 2: Complete registration using the verification code ---
    register_url = f"{LOGIN_SERVICE_URL}/register"
    register_data = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": user_data["password"],
        "plan": "Free",
        "code": verification_code
    }
    register_resp = requests.post(register_url, json=register_data)
    assert register_resp.status_code == 201, f"Registration with verification code failed, response: {register_resp.text}"

    print(f"--- [Fixture] Temporary user {user_data['email']} registered successfully ---")

    yield user_data

    print("\n--- [Fixture] Test finished ---")


@pytest.fixture(scope="module")
def auth_token(registered_user):
    """
    This fixture depends on the registered_user fixture above.
    It will log in with the newly created user and return a valid token.
    """
    print("--- [Fixture] Logging in with temporary user to get Token ---")
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }
    response = requests.post(login_url, json=login_data)
    assert response.status_code == 200, "Failed to log in with the auto-registered user"
    return response.json()["token"]



class TestAuthenticationAndProfile:
    """A group of tests to verify registration, login, and user profile related APIs"""

    def test_get_profile_with_valid_token(self, auth_token):
        """Test accessing profile with a valid, auto-acquired token"""
        profile_url = f"{BASE_URL}/user/profile"
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(profile_url, headers=headers)
        assert response.status_code == 200
        assert "username" in response.json()

    def test_get_profile_with_no_token(self):
        """Test that accessing profile without a token is rejected"""
        profile_url = f"{BASE_URL}/user/profile"
        response = requests.get(profile_url)
        assert response.status_code == 401

    def test_login_wrong_credentials(self):
        """Test that logging in with wrong credentials is rejected"""
        url = f"{BASE_URL}/auth/login"
        bad_credentials = {"email": "notexist@example.com", "password": "wrongpwd"}
        response = requests.post(url, json=bad_credentials)
        assert response.status_code == 401

    def test_update_user_preferences(self, auth_token):
        """
        Test if a logged-in user can successfully update their followed currency list.
        """
        preferences_url = f"{BASE_URL}/user/preferences"
        headers = {"Authorization": f"Bearer {auth_token}"}
        preferences_data = {
            "symbols": ["BTC", "ETH", "DOGE"]
        }
        response = requests.post(preferences_url, json=preferences_data, headers=headers)

        assert response.status_code == 200
        # --- The core change is here vvv ---
        # Modify the Chinese assertion to match the English response from the backend
        assert "User preferences updated successfully" in response.json()["message"]
        # --- The core change is here ^^^ ---


class TestDataEndpoints:
    """A group of tests to verify data query related APIs"""

    def test_get_coin_data_unknown_symbol(self):
        """Test that querying a non-existent currency returns normally instead of crashing"""
        url = f"{BASE_URL}/data/coin_data?symbol=UNKNOWN_SYMBOL_XYZ"
        response = requests.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "UNKNOWN_SYMBOL_XYZ"
        assert "trend" in data  # Ensure the basic structure exists

    @pytest.mark.parametrize("symbol", ["BTC", "ETH"])
    def test_get_coin_data_known_symbols(self, symbol):
        """Test that querying a known currency returns data normally"""
        url = f"{BASE_URL}/data/coin_data?symbol={symbol}"
        response = requests.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == symbol
        assert isinstance(data["price_trend"], list)