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


"""Siren sensor for HNAP device integration."""

import logging
from typing import Optional

import hnap
import requests.exceptions
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

from .const import CONF_AUTO_REBOOT, DOMAIN, PLATFORM_SIREN
from .entity import HNapEntity

PLATFORM = PLATFORM_SIREN
SIREN_DOMAIN = "siren"
_LOGGER = logging.getLogger(__name__)


class HNAPSiren(HNapEntity, SirenEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, name="siren", domain=SIREN_DOMAIN)
        self._attr_is_on = False
        self._attr_supported_features = (
            SUPPORT_TURN_ON
            | SUPPORT_TURN_OFF
            | SUPPORT_TONES
            | SUPPORT_DURATION
            | SUPPORT_VOLUME_SET
        )
        self._attr_available_tones = [
            x.name.lower().replace("_", "-") for x in hnap.SirenSound
        ]

    def update(self):
        try:
            self._attr_is_on = self.device.is_playing()

        except requests.exceptions.ConnectionError as e:
            _LOGGER.error(e)
            self._attr_is_on = None
            self.hnap_update_failure()

        else:
            self.hnap_update_success()

    def turn_on(self, volume_level=1, duration=15, tone="police") -> None:
        self.device.play(
            sound=hnap.SirenSound.fromstring(tone),
            volume=int(volume_level * 100),
            duration=duration,
        )

    def turn_off(self) -> None:
        self.device.stop()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,  # noqa DiscoveryInfoType | None
):
    device = hass.data[DOMAIN][config_entry.entry_id]
    device, device_info = hass.data[DOMAIN][config_entry.entry_id]

    add_entities(
        [
            HNAPSiren(
                unique_id=f"{config_entry.entry_id}-{PLATFORM}",
                device_info=device_info,
                device=device,
                auto_reboot=config_entry.data[CONF_AUTO_REBOOT],
            )
        ],
        update_before_add=True,
    )
