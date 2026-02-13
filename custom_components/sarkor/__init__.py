"""The Sarkor integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SarkorApiClient
from .const import (
    APP_KEY,
    CONF_BASE_URL,
    CONF_PASSWORD,
    CONF_UPDATE_INTERVAL_HOURS,
    CONF_USERNAME,
    DEFAULT_BASE_URL,
    DEFAULT_LANG,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import SarkorDataUpdateCoordinator


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    lang = (hass.config.language or "").split("-", 1)[0].lower() or DEFAULT_LANG
    update_hours = entry.options.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS)
    try:
        update_hours_int = int(update_hours)
    except (TypeError, ValueError):
        update_hours_int = DEFAULT_UPDATE_INTERVAL_HOURS
    if update_hours_int < 1:
        update_hours_int = 1
    api = SarkorApiClient(
        session,
        base_url=entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        app_key=APP_KEY,
        lang=lang,
    )
    coordinator = SarkorDataUpdateCoordinator(hass, api, update_interval=timedelta(hours=update_hours_int))
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
