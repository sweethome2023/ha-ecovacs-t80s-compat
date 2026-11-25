"""Config flow for the Ecovacs T80S compatibility integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class EcovacsT80sFixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create a single compatibility entry."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Ecovacs T80S 兼容层", data={})
