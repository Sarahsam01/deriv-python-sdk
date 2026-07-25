from deriv_sdk.auth.models import AuthorizeResponse

sample = {
    "echo_req": {
        "authorize": "TOKEN"
    },
    "msg_type": "authorize",
    "authorize": {
        "loginid": "VRTC11003424",
        "currency": "USD",
        "balance": 39.20,
        "email": "user@example.com",
        "fullname": "Demo User",
        "is_virtual": True
    }
}

response = AuthorizeResponse.model_validate(sample)

print("Login ID :", response.authorize.loginid)
print("Currency :", response.authorize.currency)
print("Balance  :", response.authorize.balance)
print("Email    :", response.authorize.email)
print("Virtual  :", response.authorize.is_virtual)