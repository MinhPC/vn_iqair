import voluptuous as vol
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_CITY,
    CONF_STATE,
    CONF_COUNTRY,
)

class VNIQAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_create_entry(
                title=f"{user_input[CONF_CITY]}, {user_input[CONF_COUNTRY]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_CITY): str,
            vol.Required(CONF_STATE): str,
            vol.Required(CONF_COUNTRY): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)