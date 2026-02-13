"""Sensors for Sarkor integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import SarkorDataUpdateCoordinator


@dataclass(frozen=True, slots=True, kw_only=True)
class SarkorSensorEntityDescription(SensorEntityDescription):
    # Base SensorEntityDescription has many defaulted fields; make our extra
    # field keyword-only to avoid "non-default follows default" init issues.
    value_fn: Callable[[Any], Any]


SENSORS: Final[list[SarkorSensorEntityDescription]] = [
    SarkorSensorEntityDescription(
        key="tariff",
        name="ASKUI Размер тарифа",
        native_unit_of_measurement="UZS",
        device_class=SensorDeviceClass.MONETARY,
        value_fn=lambda data: data.abon_price,
    ),
    SarkorSensorEntityDescription(
        key="saldo_out",
        name="Предоплата",
        native_unit_of_measurement="UZS",
        device_class=SensorDeviceClass.MONETARY,
        value_fn=lambda data: data.saldo,
    ),
    SarkorSensorEntityDescription(
        key="next_debit_ts",
        name="Следующее списание",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: dt_util.parse_datetime(data.next_abon_time) if data.next_abon_time else None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SarkorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SarkorSensor(coordinator, entry, desc) for desc in SENSORS])


class SarkorSensor(CoordinatorEntity[SarkorDataUpdateCoordinator], SensorEntity):
    entity_description: SarkorSensorEntityDescription

    def __init__(
        self,
        coordinator: SarkorDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SarkorSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name="Sarkor Cabinet",
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Sarkor Telecom",
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose full BaseData details on the balance sensor."""
        data = self.coordinator.data
        if data is None:
            return None

        if self.entity_description.key != "saldo_out":
            return None

        attrs: dict[str, Any] = dict(data.account_base_info or {})
        # Include arrays from BaseData response.
        attrs["limits"] = data.limits
        attrs["speeds"] = data.speeds
        return attrs
