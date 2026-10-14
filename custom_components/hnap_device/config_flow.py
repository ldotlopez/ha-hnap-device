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
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

"""Config flow for HNAP device."""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from typing import Any

import aiohttp
import hnap
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
from .device import async_create_device

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
    """Validate credentials and return the discovered device's config-entry data."""
    device = None
    try:
        device = await async_create_device(hass, data)
        info = await device.get_info()
    except hnap.AuthenticationError as err:
        raise InvalidAuth() from err
    except (aiohttp.ClientError, hnap.MethodCallError, OSError, TimeoutError) as err:
        raise CannotConnect() from err
    except TypeError as err:
        raise InvalidDeviceType() from err
    finally:
        if device is not None:
            await device.close()

    platforms = [Platform.BINARY_SENSOR]
    if device.device_type == hnap.DeviceType.CAMERA:
        platforms.append(Platform.CAMERA)
    if device.device_type == hnap.DeviceType.SIREN:
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
        except Exception:
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
        """Start reauthentication for an existing entry."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate and save replacement credentials."""
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
            except Exception:
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
    """Error to indicate the device type is unsupported."""
