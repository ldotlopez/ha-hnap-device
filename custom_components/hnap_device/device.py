"""Async HNAP device construction."""

from typing import Any

import aiohttp
import hnap
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


async def async_create_device(
    hass: HomeAssistant,
    data: dict[str, Any],
    *,
    http_client: aiohttp.ClientSession | None = None,
) -> hnap.Device:
    """Create and discover a device using Home Assistant's aiohttp session."""
    config = hnap.DeviceConfig(
        hostname=data[CONF_HOST],
        password=data[CONF_PASSWORD],
        username=data[CONF_USERNAME],
    )
    return await hnap.DeviceFactory(
        config=config,
        http_client=(
            http_client if http_client is not None else async_get_clientsession(hass)
        ),
    )
