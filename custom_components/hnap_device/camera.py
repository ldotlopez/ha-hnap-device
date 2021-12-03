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

from homeassistant.components.camera import (
    SUPPORT_STREAM,
    Camera,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from typing import Optional
from . import _LOGGER
from .const import DOMAIN, PLATFORM_CAMERA

from .hnap_entity import HNapEntity

PLATFORM = PLATFORM_CAMERA


class HNAPCamera(HNapEntity, Camera):
    def __init__(self, info, api, unique_id):
        super().__init__(info, api, unique_id)

        self._attr_supported_features = SUPPORT_STREAM

    async def stream_source(self) -> Optional[str]:
        return self._api.stream_url


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: Optional[
        DiscoveryInfoType
    ] = None,  # noqa DiscoveryInfoType | None
):
    api = hass.data[DOMAIN][PLATFORM][config_entry.entry_id]

    _LOGGER.error("camera support is not implemented yet")
    return

    add_entities(
        [
            HNAPCamera(
                info=config_entry.data,
                api=api,
                unique_id=config_entry.entry_id,
            )
        ],
        update_before_add=True,
    )
