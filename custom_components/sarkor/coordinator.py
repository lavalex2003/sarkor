"""Coordinator for Sarkor integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SarkorApiClient, SarkorApiError, SarkorAccountBaseInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SarkorDataUpdateCoordinator(DataUpdateCoordinator[SarkorAccountBaseInfo]):
    def __init__(self, hass: HomeAssistant, api: SarkorApiClient, *, update_interval: timedelta) -> None:
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> SarkorAccountBaseInfo:
        try:
            return await self.api.async_account_base_info()
        except SarkorApiError as exc:
            raise UpdateFailed(str(exc)) from exc
