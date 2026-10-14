#
# Copyright (C) 2021 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

from typing import Any

import aiohttp
import hnap
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import service
from homeassistant.helpers.issue_registry import async_delete_issue
from homeassistant.helpers.typing import ConfigType

from .const import CONF_PLATFORMS, DOMAIN, ISSUE_CONNECTION_LOST
from .coordinator import HNapConfigEntry, HNapCoordinator, HNapData
from .device import async_create_device

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async def _handle(call: ServiceCall) -> dict[str, list[Any]] | None:
        return await handle_service_call(hass, call)

    hass.services.async_register(
        DOMAIN, "call", _handle, supports_response=SupportsResponse.OPTIONAL
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: HNapConfigEntry) -> bool:
    try:
        device = await async_create_device(hass, entry.data)
    except hnap.AuthenticationError as err:
        raise ConfigEntryAuthFailed(err) from err
    except (aiohttp.ClientError, hnap.MethodCallError, OSError, TimeoutError) as err:
        raise ConfigEntryNotReady(err) from err

    coordinator = None
    try:
        device_info = await device.get_info()
        coordinator = HNapCoordinator(hass, entry, device)
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = HNapData(device_info=device_info, coordinator=coordinator)
        await hass.config_entries.async_forward_entry_setups(
            entry, _entry_platforms(entry)
        )
    except BaseException:
        if coordinator is not None:
            await coordinator.async_close()
        await device.close()
        entry.runtime_data = None
        raise

    return True


async def async_unload_entry(hass: HomeAssistant, entry: HNapConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(
        entry, _entry_platforms(entry)
    )
    if unloaded:
        async_delete_issue(
            hass,
            DOMAIN,
            f"{ISSUE_CONNECTION_LOST}_{entry.entry_id}",
        )
        await entry.runtime_data.coordinator.async_close()
        await entry.runtime_data.device.close()
    return unloaded


def _entry_platforms(entry: HNapConfigEntry) -> list[Platform]:
    """Include the diagnostic connection entity for existing entries."""
    return list(dict.fromkeys([*entry.data[CONF_PLATFORMS], Platform.BINARY_SENSOR]))


async def handle_service_call(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, list[Any]] | None:
    config_ids = await service.async_extract_config_entry_ids(call)
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in config_ids and entry.runtime_data is not None
    ]
    if not entries:
        raise ServiceValidationError("No matching HNAP device targeted")

    results = []
    for entry in entries:
        result = await entry.runtime_data.device.call(
            call.data["method"],
            **call.data.get("parameters", {}),
        )
        if call.return_response:
            results.append(result)

    if call.return_response:
        return {"results": results}
    return None
