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


from typing import Optional

import dchs220
from homeassistant.components.siren import (
    SUPPORT_DURATION,
    SUPPORT_TONES,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_SET,
    SirenEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from . import _LOGGER
from .const import DEFAULT_NAME, DOMAIN


class DLinkSiren(SirenEntity):
    def __init__(self, name, api, unique_id):
        # homeassistant.helpers.entity.Entity
        self._attr_unique_id = unique_id
        self._attr_name = name

        # homeassistant.helpers.entity.DeviceInfo
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "D-Link",
            "model": "D-220",
            "name": self._attr_name,
        }

        # homeassistant.components.siren.Siren
        self._attr_is_on = False
        self._attr_supported_features = (
            SUPPORT_TURN_ON
            | SUPPORT_TURN_OFF
            | SUPPORT_TONES
            | SUPPORT_DURATION
            | SUPPORT_VOLUME_SET
        )
        self._attr_available_tones = {
            x.name.lower().replace("_", "-"): x.value for x in dchs220.Sound
        }

        # dlink_siren.Siren
        self._api = api

    def update(self):
        self._attr_is_on = self._api.is_playing()

    def turn_on(self, volume_level=0.5, duration=5, tone="beep") -> None:
        _LOGGER.debug("Turning siren ON")
        self._api.play(
            sound=dchs220.Sound.fromstring(tone),
            volume=int(volume_level * 100),
            duration=duration,
        )

    def turn_off(self) -> None:
        _LOGGER.debug("Turning siren OFF")
        self._api.stop()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: Optional[
        DiscoveryInfoType
    ] = None,  # noqa DiscoveryInfoType | None
):
    # config_enty.as_dict()
    # {
    #     "data": {
    #         "host": "127.0.0.1",
    #         "password": "123456",
    #         "username": "admin",
    #     },
    #     "disabled_by": None,
    #     "domain": "dlink_siren",
    #     "entry_id": "0123456789abcdef0123456789abcdef",
    #     "options": {},
    #     "pref_disable_new_entities": False,
    #     "pref_disable_polling": False,
    #     "source": "user",
    #     "name": "D-Link siren",
    #     "unique_id": None,
    #     "version": 1,
    # }

    add_entities(
        [
            DLinkSiren(
                name=config_entry.data.get("name", DEFAULT_NAME),
                api=hass.data[DOMAIN][config_entry.entry_id],
                unique_id=config_entry.entry_id,
            )
        ],
        update_before_add=True,
    )
