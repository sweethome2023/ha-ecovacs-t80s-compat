"""Compatibility patch that teaches deebot-client about DEEBOT T80S (yaj2zg).

The official Ecovacs integration is used unchanged. HA 2026.10.x ships
deebot-client 18.6.0, which has no hardware profile for class "yaj2zg".
The upstream profile for yaj2zg is equivalent to the T80s Pro (9jc32i)
profile, so we register that profile under the yaj2zg class and reload the
existing Ecovacs config entry.
"""

from __future__ import annotations

import asyncio
import importlib
import logging
import sys
import types

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_SOURCE_CLASS = "9jc32i"  # DEEBOT T80s Pro, same T80S generation protocol
_TARGET_CLASS = "yaj2zg"  # DEEBOT T80S
_PATCHED = False


def _patch_deebot_client() -> bool:
    """Register the T80s Pro capability profile for the T80S class."""
    global _PATCHED
    if _PATCHED:
        return True

    try:
        from deebot_client import hardware
    except Exception:  # noqa: BLE001
        _LOGGER.exception("deebot-client is not importable")
        return False

    try:
        source = importlib.import_module(f"deebot_client.hardware.{_SOURCE_CLASS}")
        device_info = source.get_device_info()
    except Exception:  # noqa: BLE001
        _LOGGER.exception(
            "Could not load deebot-client hardware profile %s", _SOURCE_CLASS
        )
        return False

    # 1) Populate the runtime cache used by get_static_device_info().
    try:
        hardware._DEVICES[_TARGET_CLASS] = device_info  # type: ignore[attr-defined]
        hardware._NOT_FOUND.discard(_TARGET_CLASS)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Could not populate deebot-client hardware cache")
        return False

    # 2) Also provide an importable module, in case something imports it
    #    directly instead of going through the cache.
    module_name = f"deebot_client.hardware.{_TARGET_CLASS}"
    if module_name not in sys.modules:
        module = types.ModuleType(module_name)
        module.__doc__ = "DEEBOT T80S capabilities (T80s Pro profile)"
        module.get_device_info = source.get_device_info
        module.__package__ = "deebot_client.hardware"
        sys.modules[module_name] = module

    _PATCHED = True
    _LOGGER.info(
        "Registered deebot-client hardware profile %s for %s",
        _SOURCE_CLASS,
        _TARGET_CLASS,
    )
    return True


async def _reload_ecovacs(hass: HomeAssistant) -> None:
    """Reload the existing Ecovacs entry so it recreates the T80S device."""
    await asyncio.sleep(3)
    for entry in hass.config_entries.async_entries("ecovacs"):
        if entry.state is not ConfigEntryState.LOADED:
            continue
        _LOGGER.info("Reloading Ecovacs entry %s after T80S patch", entry.entry_id)
        try:
            await hass.config_entries.async_reload(entry.entry_id)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not reload Ecovacs entry %s", entry.entry_id)


def _schedule_reload(hass: HomeAssistant) -> None:
    """Reload once, after startup has completed."""
    if hass.data.get(DOMAIN, {}).get("reload_scheduled"):
        return
    hass.data.setdefault(DOMAIN, {})["reload_scheduled"] = True

    if hass.is_running:
        hass.async_create_task(_reload_ecovacs(hass))
        return

    async def _on_started(_event) -> None:
        hass.async_create_task(_reload_ecovacs(hass))

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_started)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Patch early, as soon as this integration is loaded."""
    _patch_deebot_client()
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the compatibility entry."""
    if not _patch_deebot_client():
        return False

    hass.data.setdefault(DOMAIN, {})["entry_id"] = entry.entry_id
    _schedule_reload(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the compatibility entry (the patch itself stays in memory)."""
    hass.data.get(DOMAIN, {}).pop("entry_id", None)
    return True
