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

import logging
import os
from collections.abc import Mapping
from typing import Any

import hnap.soapclient
import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import format_mac

from .const import CONF_PLATFORMS, DEFAULT_USERNAME, DOMAIN
from .device import UnsupportedDeviceType, create_device

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_HOST, default=os.environ.get("HASS_HNAP_DEVICE_HOST", "")
        ): str,
        vol.Required(
            CONF_USERNAME,
            default=os.environ.get("HASS_HNAP_DEVICE_USERNAME", DEFAULT_USERNAME),
        ): str,
        vol.Required(
            CONF_PASSWORD, default=os.environ.get("HASS_HNAP_DEVICE_PASSWORD", "")
        ): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the
    user.
    """

    def create_configured_device():
        client = hnap.soapclient.SoapClient(
            hostname=data[CONF_HOST],
            password=data[CONF_PASSWORD],
            username=data[CONF_USERNAME],
        )
        info = client.device_info()
        return create_device(client, info), info

    try:
        device, info = await hass.async_add_executor_job(create_configured_device)

    except requests.exceptions.ConnectionError as e:
        raise CannotConnect() from e

    except hnap.AuthenticationError as e:
        raise InvalidAuth() from e

    except UnsupportedDeviceType as e:
        raise InvalidDeviceType(str(e)) from e

    platforms = [Platform.BINARY_SENSOR]
    if isinstance(device, hnap.Camera):
        platforms.append(Platform.CAMERA)
    if isinstance(device, hnap.Siren):
        platforms.append(Platform.SIREN)

    return {
        CONF_NAME: info["ModelName"],
        "mac": format_mac(info["DeviceMacId"]),
        CONF_HOST: data[CONF_HOST],
        CONF_PASSWORD: data[CONF_PASSWORD],
        CONF_USERNAME: data[CONF_USERNAME],
        CONF_PLATFORMS: platforms,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HNAP device."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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
            await self.async_set_unique_id(info.pop("mac"))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=info.pop(CONF_NAME), data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(
                    self.hass, {**entry.data, CONF_PASSWORD: user_input[CONF_PASSWORD]}
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_PASSWORD: info[CONF_PASSWORD]}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidDeviceType(HomeAssistantError):
    pass
