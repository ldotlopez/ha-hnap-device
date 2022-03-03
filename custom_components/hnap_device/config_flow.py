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


"""Config flow for HNAP device integration."""
from __future__ import annotations

import functools
from typing import Any

import hnap.soapclient
import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from . import _LOGGER
from .const import (
    CONF_PLATFORMS,
    DOMAIN,
    PLATFORM_CAMERA,
    PLATFORM_BINARY_SENSOR,
    PLATFORM_SIREN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("username", default="admin"): str,
        vol.Required("password"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the
    user.
    """

    fn = functools.partial(
        hnap.DeviceFactory,
        hostname=data[CONF_HOST],
        password=data[CONF_PASSWORD],
        username=data[CONF_USERNAME],
    )
    try:
        device = await hass.async_add_executor_job(fn)

    except requests.exceptions.ConnectionError as e:
        raise CannotConnect() from e

    except hnap.AuthenticationError as e:
        raise InvalidAuth() from e

    platforms = []
    if isinstance(device, hnap.Camera):
        # 'Optical Recognition', 'Environmental Sensor', 'Camera']
        platforms.append(PLATFORM_CAMERA)
    if isinstance(device, hnap.Motion):
        platforms.append(PLATFORM_BINARY_SENSOR)
    if isinstance(device, hnap.Siren):
        platforms.append(PLATFORM_SIREN)

    if not platforms:
        raise InvalidDeviceType(str(device.__class__))

    info = await hass.async_add_executor_job(device.client.device_info)
    return {
        CONF_NAME: info["ModelName"],
        CONF_HOST: data[CONF_HOST],
        CONF_PASSWORD: data[CONF_PASSWORD],
        CONF_USERNAME: data[CONF_USERNAME],
        CONF_PLATFORMS: platforms,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for HNAP device."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except InvalidDeviceType:
            errors["base"] = "invalid_device_type"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["name"], data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

    pass


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

    pass


class InvalidDeviceType(HomeAssistantError):
    pass
