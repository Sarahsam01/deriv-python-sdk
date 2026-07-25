from deriv_sdk.config import SDKConfig

config = SDKConfig()

print("App ID       :", config.app_id)
print("Environment  :", config.environment)
print("Demo         :", config.is_demo)
print("Live         :", config.is_live)
print("WebSocket URL:", config.websocket_url)

config.validate()

print("Configuration is valid.")
