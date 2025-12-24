import aiohttp
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_CITY,
    CONF_STATE,
    CONF_COUNTRY,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

API_URL = "https://api.airvisual.com/v2/city"

class IQAirCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.city = entry.data[CONF_CITY]
        self.state = entry.data[CONF_STATE]
        self.country = entry.data[CONF_COUNTRY]

        super().__init__(
            hass,
            _LOGGER,
            name=f"IQAir {self.city}",
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
            always_update=True,   # ✅ CỰC KỲ QUAN TRỌNG
        )

    async def _async_update_data(self):
        params = {
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "key": self.api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params=params, timeout=20) as resp:
                    if resp.status == 429:
                        raise UpdateFailed("IQAir rate limit exceeded (429)")
                    resp.raise_for_status()
                    result = await resp.json()

            return result["data"]

        except Exception as err:
            raise UpdateFailed(f"IQAir API error: {err}")