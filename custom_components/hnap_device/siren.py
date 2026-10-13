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

import functools
from typing import Any, ClassVar

import hnap
from homeassistant.components.siren import (
    ATTR_DURATION,
    ATTR_TONE,
    ATTR_VOLUME_LEVEL,
    SirenEntity,
    SirenEntityFeature,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DEFAULT_SIREN_DURATION, DEFAULT_SIREN_TONE, DEFAULT_SIREN_VOLUME
from .coordinator import HNapConfigEntry
from .entity import HNapEntity


class HNAPSiren(HNapEntity, SirenEntity):
    _attr_supported_features = (
        SirenEntityFeature.TURN_ON
        | SirenEntityFeature.TURN_OFF
        | SirenEntityFeature.TONES
        | SirenEntityFeature.DURATION
        | SirenEntityFeature.VOLUME_SET
    )
    _attr_available_tones: ClassVar[list[str]] = [x.name.lower().replace("_", "-") for x in hnap.SirenSound]

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("siren")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            functools.partial(
                self.device.play,
                sound=hnap.SirenSound.fromstring(
                    kwargs.get(ATTR_TONE, DEFAULT_SIREN_TONE)
                ),
                volume=int(kwargs.get(ATTR_VOLUME_LEVEL, DEFAULT_SIREN_VOLUME) * 100),
                duration=kwargs.get(ATTR_DURATION, DEFAULT_SIREN_DURATION),
            )
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self.device.stop)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HNapConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = config_entry.runtime_data
    async_add_entities(
        [
            HNAPSiren(
                data.coordinator,
                unique_id=f"{config_entry.entry_id}-{Platform.SIREN}",
                device_info=data.device_info,
                device=data.device,
            )
        ]
    )
