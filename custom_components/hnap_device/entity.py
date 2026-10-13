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


from typing import Any

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, format_mac
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HNapCoordinator


class HNapEntity(CoordinatorEntity[HNapCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HNapCoordinator,
        *,
        unique_id: str,
        device_info: dict[str, str],
        device: Any,
        name: str | None = None,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={("mac", device_info["DeviceMacId"])},
            connections={
                (CONNECTION_NETWORK_MAC, format_mac(device_info["DeviceMacId"]))
            },
            manufacturer=device_info["VendorName"],
            model=device_info["ModelName"],
            name=device_info["DeviceName"],
        )
        self.device = device
