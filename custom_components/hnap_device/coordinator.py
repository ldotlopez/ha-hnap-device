"""Data coordinator for HNAP device integration."""

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import hnap
import requests.exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, ISSUE_CONNECTION_LOST

_LOGGER = logging.getLogger(__name__)


@dataclass
class HNapData:
    device_info: dict[str, str]
    coordinator: "HNapCoordinator"

    @property
    def device(self) -> Any:
        """Return the current device client."""
        return self.coordinator.device


type HNapConfigEntry = ConfigEntry[HNapData]


class HNapCoordinator(DataUpdateCoordinator[dict[str, bool]]):
    config_entry: HNapConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: HNapConfigEntry, device: Any
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.entry = entry
        self.device = device
        self.device_class = type(device)
        self.connected = False
        self._reconnect_needed = False

    def _poll(self) -> tuple[Any, dict[str, bool]]:
        device = self.device
        if self._reconnect_needed:
            client = hnap.soapclient.SoapClient(
                hostname=self.entry.data[CONF_HOST],
                password=self.entry.data[CONF_PASSWORD],
                username=self.entry.data[CONF_USERNAME],
            )
            device = self.device_class(client=client)
            device.client.authenticate(force=True)

        data: dict[str, bool] = {}
        if isinstance(device, hnap.Siren):
            data["siren"] = bool(device.is_playing())
        if isinstance(device, hnap.Motion):
            data["motion"] = bool(device.is_active())
        return device, data

    async def _async_update_data(self) -> dict[str, bool]:
        try:
            device, result = await self.hass.async_add_executor_job(self._poll)
        except (
            hnap.soapclient.MethodCallError,
            hnap.AuthenticationError,
            requests.exceptions.RequestException,
            OSError,
            TimeoutError,
        ) as err:
            if self.connected:
                _LOGGER.warning("Lost connection to HNAP device; retrying: %s", err)
            self._reconnect_needed = True
            self.connected = False
            async_create_issue(
                self.hass,
                DOMAIN,
                f"{ISSUE_CONNECTION_LOST}_{self.entry.entry_id}",
                is_fixable=False,
                is_persistent=True,
                severity=IssueSeverity.WARNING,
                translation_key=ISSUE_CONNECTION_LOST,
            )
            raise UpdateFailed(err) from err

        self.device = device
        if self._reconnect_needed:
            _LOGGER.info("Connection to HNAP device restored")
            async_delete_issue(
                self.hass,
                DOMAIN,
                f"{ISSUE_CONNECTION_LOST}_{self.entry.entry_id}",
            )
        self._reconnect_needed = False
        self.connected = True
        return result
