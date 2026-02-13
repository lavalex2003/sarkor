"""Config flow for Sarkor integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SarkorApiClient, SarkorApiError
from .const import (
    APP_KEY,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_BASE_URL,
    DEFAULT_LANG,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        # Use plain numeric input (not a slider). We'll clamp/validate in code.
        vol.Optional(CONF_UPDATE_INTERVAL_HOURS, default=DEFAULT_UPDATE_INTERVAL_HOURS): vol.Coerce(int),
    }
)


def _lang_from_hass(hass: HomeAssistant) -> str:
    # hass.config.language can be like "ru" or "ru-RU". API in your examples
    # uses "ru", so normalize to the primary language.
    lang = (hass.config.language or "").split("-", 1)[0].lower()
    return lang or DEFAULT_LANG


async def _async_validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    session = async_get_clientsession(hass)
    api = SarkorApiClient(
        session,
        base_url=DEFAULT_BASE_URL,
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        app_key=APP_KEY,
        lang=_lang_from_hass(hass),
    )
    await api.async_login()


class SarkorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS) < 1:
                errors[CONF_UPDATE_INTERVAL_HOURS] = "invalid"
            try:
                if not errors:
                    await _async_validate_input(self.hass, user_input)
            except SarkorApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during validation")
                errors["base"] = "unknown"
            else:
                # Allow multiple accounts; use username as unique_id.
                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()
                # Store only credentials; url/lang are derived from HA defaults.
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                    options={
                        CONF_UPDATE_INTERVAL_HOURS: max(
                            1,
                            int(
                                user_input.get(
                                    CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
                                )
                            ),
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return SarkorOptionsFlow(config_entry)


class SarkorOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            if user_input.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS) < 1:
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Optional(
                                CONF_UPDATE_INTERVAL_HOURS,
                                default=self._entry.options.get(
                                    CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
                                ),
                            ): vol.Coerce(int),
                        }
                    ),
                    errors={CONF_UPDATE_INTERVAL_HOURS: "invalid"},
                )
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL_HOURS,
                    default=self._entry.options.get(
                        CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
                    ),
                ): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
