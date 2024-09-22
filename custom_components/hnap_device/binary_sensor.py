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

import hnap
import requests.exceptions
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import CONF_AUTO_REBOOT, DOMAIN, PLATFORM_BINARY_SENSOR
from .entity import HNapEntity

PLATFORM = PLATFORM_BINARY_SENSOR
SENSOR_DOMAIN = "sensor"
_LOGGER = logging.getLogger(__name__)


class HNAPMotion(HNapEntity, BinarySensorEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, domain=SENSOR_DOMAIN)
        self._attr_device_class = BinarySensorDeviceClass.MOTION

    def update(self):
        try:
            self._attr_is_on = self.device.is_active()
            self.hnap_update_success()

        except (
            hnap.soapclient.MethodCallError,
            requests.exceptions.ConnectionError,
        ) as e:
            _LOGGER.error(e)
            self._attr_is_on = None
            self.hnap_update_failure()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # noqa DiscoveryInfoType | None
):
    device, device_info = hass.data[DOMAIN][config_entry.entry_id]

    add_entities(
        [
            HNAPMotion(
                unique_id=f"{config_entry.entry_id}-{PLATFORM}",
                device_info=device_info,
                device=device,
                name=f"{device_info['ModelName']} motion",
                auto_reboot=config_entry.options.get(CONF_AUTO_REBOOT, True),
            )
        ],
        update_before_add=True,
    )
