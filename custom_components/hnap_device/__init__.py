# -*- coding: utf-8 -*-
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


"""The HNAP device integration."""
from __future__ import annotations

import functools
import logging

import hnap
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PLATFORM_BINARY_SENSOR,
    PLATFORM_SIREN,
    CONF_PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = [PLATFORM_BINARY_SENSOR, PLATFORM_SIREN]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HNAP device from a config entry."""

    hass.data[DOMAIN] = hass.data.get(DOMAIN, {})
    for platform in entry.data[CONF_PLATFORMS]:
        hass.data[DOMAIN][platform] = hass.data[DOMAIN].get(platform, {})

    # Store an API object for your platforms to access
    fn = functools.partial(
        hnap.DeviceFactory,
        hostname=entry.data[CONF_HOST],
        password=entry.data[CONF_PASSWORD],
        username=entry.data[CONF_USERNAME],
    )

    api = await hass.async_add_executor_job(fn)
    await hass.async_add_executor_job(api.authenticate)

    hass.data[DOMAIN][platform][entry.entry_id] = api

    # Setup platforms
    hass.config_entries.async_setup_platforms(
        entry, entry.data[CONF_PLATFORMS]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        for platform in entry.data[CONF_PLATFORMS]:
            hass.data[DOMAIN][platform].pop(entry.entry_id)

    return unload_ok
