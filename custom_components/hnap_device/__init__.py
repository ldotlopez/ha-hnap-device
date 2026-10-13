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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


import functools
import logging

import hnap
import requests.exceptions
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import service
from homeassistant.helpers.typing import ConfigType

from .const import CONF_PLATFORMS, DOMAIN
from .coordinator import HNapConfigEntry, HNapCoordinator, HNapData

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async def _handle(call: ServiceCall) -> None:
        await handle_service_call(hass, call)

    hass.services.async_register(DOMAIN, "call", _handle)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: HNapConfigEntry) -> bool:
    def get_device():
        client = hnap.soapclient.SoapClient(
            hostname=entry.data[CONF_HOST],
            password=entry.data[CONF_PASSWORD],
            username=entry.data[CONF_USERNAME],
        )
        device = hnap.DeviceFactory(client=client)
        return device, device.client.device_info()

    try:
        device, device_info = await hass.async_add_executor_job(get_device)
    except hnap.AuthenticationError as err:
        raise ConfigEntryAuthFailed(err) from err
    except (requests.exceptions.RequestException, OSError) as err:
        raise ConfigEntryNotReady(err) from err

    coordinator = HNapCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = HNapData(
        device=device, device_info=device_info, coordinator=coordinator
    )

    await hass.config_entries.async_forward_entry_setups(
        entry, entry.data[CONF_PLATFORMS]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: HNapConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(
        entry, entry.data[CONF_PLATFORMS]
    )


async def handle_service_call(hass: HomeAssistant, call: ServiceCall) -> None:
    config_ids = await service.async_extract_config_entry_ids(call)
    entries = [
        e
        for e in hass.config_entries.async_entries(DOMAIN)
        if e.entry_id in config_ids and e.runtime_data is not None
    ]
    if not entries:
        raise ServiceValidationError("No matching HNAP device targeted")

    for entry in entries:
        await hass.async_add_executor_job(
            functools.partial(
                entry.runtime_data.device.call,
                call.data["method"],
                **call.data.get("parameters", {}),
            )
        )
