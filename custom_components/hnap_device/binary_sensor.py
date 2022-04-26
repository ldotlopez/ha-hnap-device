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

"""Binary sensor for HNAP device integration."""

from typing import Optional

import requests.exceptions
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from . import _LOGGER
from .const import DOMAIN, PLATFORM_BINARY_SENSOR
from .hnap_entity import HNapEntity

PLATFORM = PLATFORM_BINARY_SENSOR


class HNAPMotion(HNapEntity, BinarySensorEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr_device_class = DEVICE_CLASS_MOTION

    def update(self):
        try:
            self._attr_is_on = self.device.is_active()

        except requests.exceptions.ConnectionError as e:
            _LOGGER.error(e)
            self._attr_is_on = None
            self.hnap_update_failure()

        else:
            self.hnap_update_success()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,  # noqa DiscoveryInfoType | None
):
    device = hass.data[DOMAIN][PLATFORM][config_entry.entry_id]
    device_info = await hass.async_add_executor_job(device.client.device_info)

    add_entities(
        [
            HNAPMotion(
                unique_id=config_entry.entry_id,
                device_info=device_info,
                device=device,
            )
        ],
        update_before_add=True,
    )
