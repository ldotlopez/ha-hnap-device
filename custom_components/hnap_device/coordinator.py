"""Data coordinator for HNAP device integration."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import timedelta

import aiohttp
import hnap
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, ISSUE_CONNECTION_LOST
from .device import async_create_device

_LOGGER = logging.getLogger(__name__)
_CONNECTION_ERRORS = (
    hnap.MethodCallError,
    hnap.AuthenticationError,
    aiohttp.ClientError,
    OSError,
    TimeoutError,
)


async def _async_close_connection_middleware(
    request: aiohttp.ClientRequest,
    handler: Callable[[aiohttp.ClientRequest], Awaitable[aiohttp.ClientResponse]],
) -> aiohttp.ClientResponse:
    """Avoid reusing persistent connections for recovery requests."""
    request.headers["Connection"] = "close"
    return await handler(request)


@dataclass
class HNapData:
    device_info: dict[str, str]
    coordinator: "HNapCoordinator"

    @property
    def device(self) -> hnap.Device:
        """Return the current device."""
        return self.coordinator.device


type HNapConfigEntry = ConfigEntry[HNapData]


class HNapCoordinator(DataUpdateCoordinator[dict[str, bool]]):
    config_entry: HNapConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: HNapConfigEntry, device: hnap.Device
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
        self.connected = False
        self._connection_issue_created = False
        self._recovery_http_client: aiohttp.ClientSession | None = None

    async def _async_update_data(self) -> dict[str, bool]:
        try:
            data = await self._async_poll_device()
        except _CONNECTION_ERRORS as err:
            _LOGGER.debug(
                "HNAP poll failed (%s); replacing the device and retrying once", err
            )
            try:
                await self._async_replace_device()
                data = await self._async_poll_device()
            except _CONNECTION_ERRORS as retry_err:
                self._async_mark_connection_lost(retry_err)
                raise UpdateFailed(retry_err) from retry_err
            _LOGGER.debug("HNAP device recovered after replacing the device")

        if self._connection_issue_created:
            _LOGGER.info("Connection to HNAP device restored")
            async_delete_issue(
                self.hass,
                DOMAIN,
                f"{ISSUE_CONNECTION_LOST}_{self.entry.entry_id}",
            )
            self._connection_issue_created = False
        self.connected = True
        return data

    async def _async_poll_device(self) -> dict[str, bool]:
        data: dict[str, bool] = {}
        if self.device.device_type == hnap.DeviceType.SIREN:
            data["siren"] = bool(await self.device.is_playing())
        if self.device.device_type == hnap.DeviceType.MOTION:
            data["motion"] = bool(await self.device.is_active())
        return data

    async def _async_replace_device(self) -> None:
        """Use a fresh session that does not reuse HNAP connections."""
        http_client = async_create_clientsession(
            self.hass  # , middlewares=(_async_close_connection_middleware,)
        )
        for attempt in range(2):
            try:
                device = await async_create_device(
                    self.hass, self.entry.data, http_client=http_client
                )
            except _CONNECTION_ERRORS:
                if attempt == 1:
                    http_client.detach()
                    raise
                _LOGGER.debug(
                    "HNAP discovery failed on recovery session; retrying once"
                )
            except BaseException:
                http_client.detach()
                raise
            else:
                break

        previous_http_client = self._recovery_http_client
        self.device = device
        self._recovery_http_client = http_client
        if previous_http_client is not None:
            previous_http_client.detach()

    def _async_mark_connection_lost(self, err: Exception) -> None:
        if self.connected:
            _LOGGER.warning("Lost connection to HNAP device: %s", err)
        else:
            _LOGGER.debug("HNAP device remains unavailable: %s", err)
        self.connected = False
        self._connection_issue_created = True
        async_create_issue(
            self.hass,
            DOMAIN,
            f"{ISSUE_CONNECTION_LOST}_{self.entry.entry_id}",
            is_fixable=False,
            is_persistent=True,
            severity=IssueSeverity.WARNING,
            translation_key=ISSUE_CONNECTION_LOST,
        )

    async def async_close(self) -> None:
        """Detach any recovery session from Home Assistant's shared connector."""
        if self._recovery_http_client is not None:
            self._recovery_http_client.detach()
            self._recovery_http_client = None
