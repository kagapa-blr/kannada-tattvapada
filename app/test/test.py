import requests
import json

BASE_URL = "http://127.0.0.1:5000"

GENERATE_TOKEN_URL = f"{BASE_URL}/generate-token"
ADMIN_OVERVIEW_URL = f"{BASE_URL}/admin/overview"

login_payload = {
    "username": "",
    "password": ""
}

headers = {
    "Content-Type": "application/json"
}

try:
    print("Generating token...")

    login_response = requests.post(
        GENERATE_TOKEN_URL,
        headers=headers,
        json=login_payload
    )

    print("Login Status Code:", login_response.status_code)

    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        exit()

    login_data = login_response.json()

    print("Login Response:")
    print(json.dumps(login_data, indent=4))

    # ✅ Correct key
    token = login_data.get("access_token")

    if not token:
        print("Token not found in response")
        exit()

    print("\nToken generated successfully")

    # -------------------------
    # Call Admin API
    # -------------------------
    print("\nCalling /admin/overview...")

    admin_headers = {
        "Authorization": f"Bearer {token}"
    }

    admin_response = requests.get(
        ADMIN_OVERVIEW_URL,
        headers=admin_headers
    )

    print("Admin API Status Code:", admin_response.status_code)
    print("Admin API Response:")
    print(json.dumps(admin_response.json(), indent=4))

except requests.exceptions.RequestException as e:
    print("Request failed:", str(e))
