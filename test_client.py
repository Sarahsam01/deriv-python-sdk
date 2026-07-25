from deriv_sdk import DerivClient

client = DerivClient()

print(client)
print("SDK Version :", client.version)
print("Connected   :", client.connected)
print("Authorized  :", client.authorized)
