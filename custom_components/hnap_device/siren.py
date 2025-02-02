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

import hnap
import requests.exceptions
from homeassistant.components.siren import SirenEntity, SirenEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import (
    DEFAULT_SIREN_DURATION,
    DEFAULT_SIREN_TONE,
    DEFAULT_SIREN_VOLUME,
    DOMAIN,
)
from .entity import HNapEntity

SIREN_DOMAIN = "siren"
_LOGGER = logging.getLogger(__name__)


class HNAPSiren(HNapEntity, SirenEntity):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs, name="siren", domain=SIREN_DOMAIN)
        self._attr_is_on = False
        self._attr_supported_features = (
            SirenEntityFeature.TURN_ON
            | SirenEntityFeature.TURN_OFF
            | SirenEntityFeature.TONES
            | SirenEntityFeature.DURATION
            | SirenEntityFeature.VOLUME_SET
        )
        self._attr_available_tones = [
            x.name.lower().replace("_", "-") for x in hnap.SirenSound
        ]

    def update(self):
        try:
            if not self.available:
                self.device.authenticate(force=True)
            self._attr_is_on = self.device.is_playing()
            self._attr_available = True

        except requests.exceptions.ConnectionError as e:
            _LOGGER.error(e)
            self._attr_is_on = None
            self._attr_available = False

    def turn_on(
        self,
        volume_level: float = DEFAULT_SIREN_VOLUME,
        duration: int = DEFAULT_SIREN_DURATION,
        tone: str = DEFAULT_SIREN_TONE,
        **kwargs,
    ) -> None:
        self.device.play(
            sound=hnap.SirenSound.fromstring(tone),
            volume=int(volume_level * 100),
            duration=duration,
        )

    def turn_off(self, **kwargs) -> None:
        self.device.stop()
        self.update()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # noqa DiscoveryInfoType | None
):
    device = hass.data[DOMAIN][config_entry.entry_id]
    device, device_info = hass.data[DOMAIN][config_entry.entry_id]

    add_entities(
        [
            HNAPSiren(
                unique_id=f"{config_entry.entry_id}-{Platform.SIREN}",
                device_info=device_info,
                device=device,
                # FIXME: upgrade config version
                auto_reboot=config_entry.options.get(CONF_AUTO_REBOOT, False),
            )
        ],
        update_before_add=True,
    )
