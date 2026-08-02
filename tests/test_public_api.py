from deriv_sdk import DerivClient, SDKConfig, __version__


def test_root_public_api_exports_client_config_and_version():
    config = SDKConfig(app_id="1089", api_token="")
    client = DerivClient(app_id="ignored", config=config)

    assert client.config is config
    assert __version__ == "1.0.0rc1"
