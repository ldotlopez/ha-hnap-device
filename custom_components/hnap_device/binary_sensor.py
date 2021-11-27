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

import hnap
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_MOTION,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import DOMAIN, PLATFORM_BINARY_SENSOR
PLATFORM = PLATFORM_BINARY_SENSOR


class HNAPMotion(BinarySensorEntity):
    def __init__(self, info, api, unique_id):
        # homeassistant.helpers.entity.Entity
        self._attr_unique_id = unique_id

        # homeassistant.helpers.entity.DeviceInfo
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, self.unique_id),
                ("mac", api.info["DeviceMacId"]),
            },
            "manufacturer": api.info["VendorName"],
            "model": api.info["ModelName"],
            "name": api.info["DeviceName"],
        }
        self._attr_name = self._attr_device_info["name"]
        self._attr_device_class = DEVICE_CLASS_MOTION

        self._api = api

    def update(self):
        self._attr_is_on = self._api.is_active()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: Optional[
        DiscoveryInfoType
    ] = None,  # noqa DiscoveryInfoType | None
):
    add_entities(
        [
            HNAPMotion(
                info=config_entry.data,
                api=hass.data[DOMAIN][PLATFORM][config_entry.entry_id],
                unique_id=config_entry.entry_id,
            )
        ],
        update_before_add=True,
    )
