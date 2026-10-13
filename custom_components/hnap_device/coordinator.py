"""Data coordinator for HNAP device integration."""

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import hnap
import requests.exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class HNapData:
    device: Any
    device_info: dict[str, str]
    coordinator: "HNapCoordinator"


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
        self.device = device
        self._failed = False

    def _poll(self) -> dict[str, bool]:
        if self._failed:
            self.device.authenticate(force=True)
        data: dict[str, bool] = {}
        if isinstance(self.device, hnap.Siren):
            data["siren"] = bool(self.device.is_playing())
        if isinstance(self.device, hnap.Motion):
            data["motion"] = bool(self.device.is_active())
        return data

    async def _async_update_data(self) -> dict[str, bool]:
        try:
            result = await self.hass.async_add_executor_job(self._poll)
        except (
            hnap.soapclient.MethodCallError,
            requests.exceptions.RequestException,
        ) as err:
            self._failed = True
            raise UpdateFailed(err) from err
        self._failed = False
        return result
