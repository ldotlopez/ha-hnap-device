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


import logging

from hnap import Device as HNapDevice
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_registry import slugify

_LOGGER = logging.getLogger(__name__)


class HNapEntity(Entity):
    def __init__(
        self,
        *args,
        domain: str,
        unique_id: str,
        device_info: dict[str, str],
        device: HNapDevice,
        name: str,
        auto_reboot=True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._attr_unique_id = unique_id

        part = slugify(name)
        self._attr_entity_id = f"{domain}.{part}"

        self._attr_device_info = DeviceInfo(
            identifiers={
                ("mac", device_info["DeviceMacId"]),
            },
            manufacturer=device_info["VendorName"],
            model=device_info["ModelName"],
            name=device_info["DeviceName"],
        )

        self._attr_name = name.capitalize()
        self._attr_has_entity_name = True

        self._attr_entity_registry_visible_default = True
        self._attr_entity_registry_enabled_default = True

        self.device = device
