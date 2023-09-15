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

import logging
from typing import Optional

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import DOMAIN, PLATFORM_CAMERA
from .entity import HNapEntity

_LOGGER = logging.getLogger(__name__)
PLATFORM = PLATFORM_CAMERA


class HNAPCamera(HNapEntity, Camera):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attr_supported_features = SUPPORT_STREAM

    async def stream_source(self) -> str | None:
        return self.device.stream_url


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # noqa DiscoveryInfoType | None
):
    _LOGGER.error("camera support is not implemented yet")
    return

    # api = hass.data[DOMAIN][config_entry.entry_id]
    # device_info = await hass.async_add_executor_job(device.client.device_info)
    #
    # add_entities(
    #     [
    #         HNAPCamera(
    #             unique_id=config_entry.entry_id,
    #             device_info=device_info,
    #             api=api,
    #         )
    #     ],
    #     update_before_add=True,
    # )
