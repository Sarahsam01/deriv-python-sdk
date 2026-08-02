from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

load_dotenv()

from deriv_sdk.auth.service import AuthService  # noqa: E402
from deriv_sdk.config import SDKConfig  # noqa: E402
from deriv_sdk.market.responses import ActiveSymbolsResponse  # noqa: E402
from deriv_sdk.transport.websocket import WebSocketClient  # noqa: E402


class DiagnosticWebSocketClient(WebSocketClient):
    async def request_raw(
        self,
        message: dict[str, Any],
        *,
        expected: str,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        req_id = await self._allocate_req_id()
        request = dict(message)
        request["req_id"] = req_id
        future = self._registry.register(req_id)

        try:
            await self.send(request)
            response = await asyncio.wait_for(future, timeout=timeout)
        finally:
            self._registry.unregister(req_id)

        msg_type = response.get("msg_type")
        if msg_type != expected:
            raise RuntimeError(
                "Unexpected response type. "
                f"Expected '{expected}', received '{msg_type}'."
            )

        return response


VARIANTS: tuple[tuple[str, dict[str, Any]], ...] = (
    ("A", {"active_symbols": "brief"}),
    ("B", {"active_symbols": "brief", "product_type": "basic"}),
    ("C", {"active_symbols": "full", "product_type": "basic"}),
    (
        "D",
        {
            "active_symbols": "brief",
            "product_type": "basic",
            "landing_company_short": "svg",
        },
    ),
    (
        "E",
        {
            "active_symbols": "full",
            "product_type": "basic",
            "landing_company_short": "svg",
        },
    ),
)


def _app_id() -> str:
    value = os.getenv("DERIV_APP_ID", "").strip()
    if not value:
        raise RuntimeError("DERIV_APP_ID is required.")
    return value


def _api_token() -> str | None:
    value = os.getenv("DERIV_API_TOKEN", "").strip()
    return value or None


def _account_label(authorize_response: dict[str, Any] | None) -> str:
    if authorize_response is None:
        return "unauthenticated"

    authorize = authorize_response.get("authorize")
    if not isinstance(authorize, dict):
        return "authenticated_unknown"

    login_id = str(authorize.get("loginid", ""))
    if login_id.upper().startswith("VRTC"):
        return "authenticated_virtual"
    return "authenticated_real"


def _summarize(
    *,
    mode: str,
    variant: str,
    payload: dict[str, Any],
    response: dict[str, Any],
) -> dict[str, Any]:
    raw_symbols = response.get("active_symbols", [])
    raw_count = len(raw_symbols) if isinstance(raw_symbols, list) else None

    parse_error = None
    parsed_count = None
    try:
        parsed = ActiveSymbolsResponse.model_validate(response)
        parsed_count = parsed.count
    except Exception as exc:  # noqa: BLE001 - diagnostics must report parser failures.
        parse_error = f"{exc.__class__.__name__}: {exc}"

    error = response.get("error")
    error_code = None
    error_message = None
    if isinstance(error, dict):
        error_code = error.get("code")
        error_message = error.get("message")

    return {
        "mode": mode,
        "variant": variant,
        "payload": payload,
        "echo_req": response.get("echo_req"),
        "msg_type": response.get("msg_type"),
        "top_level_keys": sorted(response.keys()),
        "raw_active_symbols_count": raw_count,
        "parsed_active_symbols_count": parsed_count,
        "parse_error": parse_error,
        "error_code": error_code,
        "error_message": error_message,
    }


async def _authorize(
    client: DiagnosticWebSocketClient,
    token: str | None,
) -> dict[str, Any] | None:
    if token is None:
        return None

    auth = AuthService(client)
    return await auth.authorize(token)


async def _run_mode(
    *,
    app_id: str,
    api_token: str | None,
) -> None:
    client = DiagnosticWebSocketClient(SDKConfig(app_id=app_id))
    authorize_response = None

    try:
        await client.connect()
        authorize_response = await _authorize(client, api_token)
        mode = _account_label(authorize_response)

        for variant, payload in VARIANTS:
            response = await client.request_raw(
                payload,
                expected="active_symbols",
                timeout=20.0,
            )
            print(
                json.dumps(
                    _summarize(
                        mode=mode,
                        variant=variant,
                        payload=payload,
                        response=response,
                    ),
                    sort_keys=True,
                )
            )
    finally:
        await client.close()


async def main() -> None:
    app_id = _app_id()
    token = _api_token()

    await _run_mode(app_id=app_id, api_token=None)
    if token is not None:
        await _run_mode(app_id=app_id, api_token=token)


if __name__ == "__main__":
    asyncio.run(main())
