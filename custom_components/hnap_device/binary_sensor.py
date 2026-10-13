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

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import HNapConfigEntry
from .entity import HNapEntity


class HNAPMotion(HNapEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOTION

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("motion")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HNapConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = config_entry.runtime_data
    async_add_entities(
        [
            HNAPMotion(
                data.coordinator,
                unique_id=f"{config_entry.entry_id}-{Platform.BINARY_SENSOR}",
                device_info=data.device_info,
                device=data.device,
            )
        ]
    )
