from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # ✅ DÒNG BỊ THIẾU
)

from .const import DOMAIN

def pm25_from_aqi(aqi):
    pm25 = aqi * 0.6 - 2
    return round(max(pm25, 0), 1)


class IQAirBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, icon, unique_suffix):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = name
        self._attr_icon = icon
        self._attr_has_entity_name = True

        # ✅ UNIQUE ID – CỰC KỲ QUAN TRỌNG
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"IQAir – {self.coordinator.city}",
            manufacturer="IQAir",
            model="City Air Quality",
            entry_type="service",
        )


class IQAirAQISensor(IQAirBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "Chỉ số AQI",
            "mdi:air-filter",
            "aqi",
        )

    @property
    def native_value(self):
        return self.coordinator.data["current"]["pollution"].get("aqius")


class IQAirPM25Sensor(IQAirBaseSensor):
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    _attr_icon = "mdi:blur"

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "PM2.5 tại nhà",
            "mdi:blur",
            "pm25",
        )

    @property
    def native_value(self):
        pollution = self.coordinator.data.get("current", {}).get("pollution", {})
        aqi = pollution.get("aqius")

        if aqi is None:
            return None

        # Map AQI → PM2.5 gần đúng (EPA)
        if aqi <= 50:
            return round(aqi * 0.25, 1)
        elif aqi <= 100:
            return round((aqi - 50) * 0.5 + 12, 1)
        elif aqi <= 150:
            return round((aqi - 100) * 0.5 + 35, 1)
        else:
            return round((aqi - 150) * 1.0 + 55, 1)


class IQAirTemperatureSensor(IQAirBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "Nhiệt độ ngoài trời",
            "mdi:thermometer",
            "temperature",
        )

    @property
    def native_value(self):
        return self.coordinator.data["current"]["weather"].get("tp")


class IQAirHumiditySensor(IQAirBaseSensor):
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "Độ ẩm ngoài trời",
            "mdi:water-percent",
            "humidity",
        )

    @property
    def native_value(self):
        return self.coordinator.data["current"]["weather"].get("hu")


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        IQAirAQISensor(coordinator, entry),
        IQAirPM25Sensor(coordinator, entry),
        IQAirTemperatureSensor(coordinator, entry),
        IQAirHumiditySensor(coordinator, entry),
    ])
