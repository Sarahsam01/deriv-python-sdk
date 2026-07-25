from deriv_sdk.transport.messages import (
    ActiveSymbolsRequest,
    AuthorizeRequest,
    ForgetRequest,
    PingRequest,
    TickSubscribeRequest,
)

print(AuthorizeRequest("ABC123").to_dict())

print(ActiveSymbolsRequest().to_dict())

print(TickSubscribeRequest("1HZ25V").to_dict())

print(ForgetRequest("123456").to_dict())

print(PingRequest().to_dict())
