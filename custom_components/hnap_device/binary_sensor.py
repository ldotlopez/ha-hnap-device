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

import hnap
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import HNapConfigEntry
from .entity import HNapEntity


class HNAPMotion(HNapEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOTION

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("motion")


class HNAPConnection(HNapEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "connection"

    @property
    def available(self) -> bool:
        """Remain available so connection failures are visible."""
        return True

    @property
    def is_on(self) -> bool:
        return self.coordinator.connected


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HNapConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = config_entry.runtime_data
    entities: list[HNapEntity] = [
        HNAPConnection(
            data.coordinator,
            unique_id=f"{config_entry.entry_id}-connection",
            device_info=data.device_info,
        )
    ]
    if data.device.device_type == hnap.DeviceType.MOTION:
        entities.append(
            HNAPMotion(
                data.coordinator,
                unique_id=f"{config_entry.entry_id}-{Platform.BINARY_SENSOR}",
                device_info=data.device_info,
            )
        )
    async_add_entities(entities)
