"""Constants for the Sarkor integration."""

DOMAIN = "sarkor"

CONF_BASE_URL = "base_url"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_LANG = "lang"
CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_BASE_URL = "https://cabinet.sarkor.uz/api/v1/jrpc/v1"
DEFAULT_LANG = "ru"
DEFAULT_UPDATE_INTERVAL_HOURS = 12

# AppKey from your existing configuration (includes/packages/kommunal/askui.yaml).
APP_KEY = "405bcecee3e307ad36b3f8945117a9a2d43a256bd9d5616defa5c852547580b6"

PLATFORMS: list[str] = ["sensor"]
