"""API client for Sarkor cabinet JSON-RPC."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

_LOGGER = logging.getLogger(__name__)


class SarkorApiError(Exception):
    """Raised when the Sarkor API returns an error or invalid response."""


@dataclass(slots=True)
class SarkorAccountBaseInfo:
    abon_price: float | None
    saldo: float | None
    next_abon_time: str | None
    # Full API payload parts for exposing as sensor attributes.
    account_base_info: dict[str, Any]
    limits: list[dict[str, Any]]
    speeds: list[dict[str, Any]]


class SarkorApiClient:
    def __init__(
        self,
        session: ClientSession,
        *,
        base_url: str,
        username: str,
        password: str,
        app_key: str,
        lang: str,
    ) -> None:
        self._session = session
        self._base_url = base_url
        self._username = username
        self._password = password
        self._app_key = app_key
        self._lang = lang
        self._token: str | None = None

    async def async_login(self) -> str:
        payload = {
            "jsonrpc": "2.0",
            "method": "Login",
            "params": {
                "login": self._username,
                "password": self._password,
                "AppKey": self._app_key,
                "Lang": self._lang,
            },
        }
        data = await self._async_call(payload, extra_headers={"Content-Type": "application/json"})
        try:
            token = data["result"]["Token"]
        except (KeyError, TypeError) as exc:
            raise SarkorApiError(f"Unexpected login response: {data}") from exc
        if not token or not isinstance(token, str):
            raise SarkorApiError(f"Invalid token in login response: {data}")
        self._token = token
        return token

    async def async_base_data(self) -> dict[str, Any]:
        if not self._token:
            await self.async_login()

        payload = {"jsonrpc": "2.0", "method": "BaseData", "params": {}}
        headers = {
            "Content-Type": "application/json",
            # Matches your working rest_command (Cookie: TOKEN=...).
            "Cookie": f"TOKEN={self._token}",
        }
        try:
            return await self._async_call(payload, extra_headers=headers)
        except SarkorApiError:
            # Token might be expired; retry once with a fresh login.
            _LOGGER.debug("BaseData failed, retrying after re-login", exc_info=True)
            self._token = None
            await self.async_login()
            headers["Cookie"] = f"TOKEN={self._token}"
            return await self._async_call(payload, extra_headers=headers)

    async def async_account_base_info(self) -> SarkorAccountBaseInfo:
        data = await self.async_base_data()
        try:
            result = data["result"]
            info = result["accountBaseInfo"]
        except (KeyError, TypeError) as exc:
            raise SarkorApiError(f"Unexpected BaseData response: {data}") from exc

        def _to_float(value: Any) -> float | None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        limits = result.get("limits")
        if not isinstance(limits, list):
            limits = []
        speeds = result.get("speeds")
        if not isinstance(speeds, list):
            speeds = []

        return SarkorAccountBaseInfo(
            abon_price=_to_float(info.get("abonPrice")),
            saldo=_to_float(info.get("saldo")),
            next_abon_time=info.get("nextAbonTime"),
            account_base_info=info if isinstance(info, dict) else {},
            limits=[x for x in limits if isinstance(x, dict)],
            speeds=[x for x in speeds if isinstance(x, dict)],
        )

    async def _async_call(self, payload: dict[str, Any], *, extra_headers: dict[str, str]) -> dict[str, Any]:
        try:
            async with self._session.post(self._base_url, json=payload, headers=extra_headers) as resp:
                raw = await resp.text()
                if resp.status >= 400:
                    raise SarkorApiError(f"HTTP {resp.status}: {raw}")
                try:
                    data = await resp.json(content_type=None)
                except Exception as exc:  # noqa: BLE001
                    raise SarkorApiError(f"Invalid JSON response: {raw}") from exc
        except (ClientError, TimeoutError) as exc:
            raise SarkorApiError(f"Request failed: {exc}") from exc

        # JSON-RPC error object.
        if isinstance(data, dict) and data.get("error"):
            raise SarkorApiError(f"JSON-RPC error: {data['error']}")
        if not isinstance(data, dict):
            raise SarkorApiError(f"Unexpected response type: {type(data)}")
        return data
