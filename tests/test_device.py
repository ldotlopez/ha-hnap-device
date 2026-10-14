"""Tests for async HNAP device construction and coordinator polling."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import hnap
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.hnap_device.config_flow import (
    CannotConnect,
    InvalidDeviceType,
    validate_input,
)
from custom_components.hnap_device.const import CONF_PLATFORMS
from custom_components.hnap_device.coordinator import (
    HNapCoordinator,
    _async_close_connection_middleware,
)
from custom_components.hnap_device.device import async_create_device


class TestAsyncDeviceFactory(unittest.IsolatedAsyncioTestCase):
    async def test_uses_home_assistant_shared_aiohttp_session(self):
        hass = Mock()
        client = Mock()
        device = Mock()
        config = hnap.DeviceConfig(
            hostname="device.local",
            password="secret",
            username="admin",
        )

        with (
            patch(
                "custom_components.hnap_device.device.async_get_clientsession",
                return_value=client,
            ) as get_client,
            patch(
                "custom_components.hnap_device.device.hnap.DeviceFactory",
                new_callable=AsyncMock,
                return_value=device,
            ) as factory,
        ):
            result = await async_create_device(
                hass,
                {
                    CONF_HOST: "device.local",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "secret",
                },
            )

        self.assertIs(result, device)
        get_client.assert_called_once_with(hass)
        factory.assert_awaited_once_with(config=config, http_client=client)

    async def test_device_close_does_not_close_injected_aiohttp_session(self):
        client = Mock()
        device = hnap.Camera(
            hnap.DeviceConfig(
                hostname="device.local",
                password="secret",
                username="admin",
            ),
            http_client=client,
        )

        await device.close()

        client.close.assert_not_called()

    async def test_validate_input_uses_device_type_and_closes_device(self):
        device = Mock()
        device.device_type = hnap.DeviceType.SIREN
        device.get_info = AsyncMock(
            return_value={
                "ModelName": "Device",
                "DeviceMacId": "00:11:22:33:44:55",
            }
        )
        device.close = AsyncMock()
        data = {
            CONF_HOST: "device.local",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret",
        }

        with patch(
            "custom_components.hnap_device.config_flow.async_create_device",
            new_callable=AsyncMock,
            return_value=device,
        ):
            result = await validate_input(Mock(), data)

        self.assertEqual(
            result[CONF_PLATFORMS],
            [Platform.BINARY_SENSOR, Platform.SIREN],
        )
        self.assertEqual(result[CONF_HOST], data[CONF_HOST])
        device.get_info.assert_awaited_once_with()
        device.close.assert_awaited_once_with()

    async def test_validate_input_maps_factory_type_error(self):
        with patch(
            "custom_components.hnap_device.config_flow.async_create_device",
            new_callable=AsyncMock,
            side_effect=TypeError("Unsupported device module types"),
        ):
            with self.assertRaises(InvalidDeviceType):
                await validate_input(
                    Mock(),
                    {
                        CONF_HOST: "device.local",
                        CONF_USERNAME: "admin",
                        CONF_PASSWORD: "secret",
                    },
                )

    async def test_validate_input_maps_aiohttp_errors(self):
        with patch(
            "custom_components.hnap_device.config_flow.async_create_device",
            new_callable=AsyncMock,
            side_effect=aiohttp.ClientError("device unavailable"),
        ):
            with self.assertRaises(CannotConnect):
                await validate_input(
                    Mock(),
                    {
                        CONF_HOST: "device.local",
                        CONF_USERNAME: "admin",
                        CONF_PASSWORD: "secret",
                    },
                )


class TestCoordinatorPolling(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.coordinator = object.__new__(HNapCoordinator)
        self.coordinator.device = object.__new__(hnap.Siren)
        self.coordinator.device.device_type = hnap.DeviceType.SIREN
        self.coordinator.connected = False
        self.coordinator._connection_issue_created = False

    async def test_awaits_device_poll(self):
        self.coordinator.device.is_playing = AsyncMock(return_value=True)

        result = await self.coordinator._async_update_data()

        self.assertEqual(result, {"siren": True})
        self.coordinator.device.is_playing.assert_awaited_once_with()
        self.assertTrue(self.coordinator.connected)

    async def test_recreates_device_and_retries_poll_after_transport_failure(self):
        self.coordinator.device.is_playing = AsyncMock(
            side_effect=aiohttp.ClientError("device unavailable")
        )
        self.coordinator.hass = Mock()
        self.coordinator.entry = SimpleNamespace(entry_id="entry", data={})
        self.coordinator._recovery_http_client = None
        session = Mock()
        replacement = object.__new__(hnap.Siren)
        replacement.device_type = hnap.DeviceType.SIREN
        replacement.is_playing = AsyncMock(return_value=True)

        with (
            patch(
                "custom_components.hnap_device.coordinator.async_create_clientsession",
                return_value=session,
            ) as create_session,
            patch(
                "custom_components.hnap_device.coordinator.async_create_device",
                new_callable=AsyncMock,
                return_value=replacement,
            ) as create_device,
            patch(
                "custom_components.hnap_device.coordinator.async_create_issue"
            ) as create_issue,
        ):
            result = await self.coordinator._async_update_data()

        self.assertEqual(result, {"siren": True})
        self.assertIs(self.coordinator.device, replacement)
        self.assertTrue(self.coordinator.connected)
        create_session.assert_called_once_with(
            self.coordinator.hass,
            middlewares=(_async_close_connection_middleware,),
        )
        create_device.assert_awaited_once_with(
            self.coordinator.hass,
            self.coordinator.entry.data,
            http_client=session,
        )
        create_issue.assert_not_called()

    async def test_retries_recovery_device_discovery_after_transport_failure(self):
        self.coordinator.hass = Mock()
        self.coordinator.entry = SimpleNamespace(entry_id="entry", data={})
        self.coordinator._recovery_http_client = None
        session = Mock()
        replacement = object.__new__(hnap.Siren)
        with (
            patch(
                "custom_components.hnap_device.coordinator.async_create_clientsession",
                return_value=session,
            ),
            patch(
                "custom_components.hnap_device.coordinator.async_create_device",
                new_callable=AsyncMock,
                side_effect=[
                    aiohttp.ServerDisconnectedError(),
                    replacement,
                ],
            ) as create_device,
        ):
            await self.coordinator._async_replace_device()

        self.assertIs(self.coordinator.device, replacement)
        self.assertEqual(create_device.await_count, 2)
        session.detach.assert_not_called()

    async def test_recovery_middleware_disables_connection_reuse(self):
        request = SimpleNamespace(headers={})
        response = object()
        handler = AsyncMock(return_value=response)

        result = await _async_close_connection_middleware(request, handler)

        self.assertIs(result, response)
        self.assertEqual(request.headers["Connection"], "close")
        handler.assert_awaited_once_with(request)

    async def test_reports_connection_loss_when_recovery_retry_fails(self):
        self.coordinator.device.is_playing = AsyncMock(
            side_effect=aiohttp.ClientError("device unavailable")
        )
        self.coordinator.hass = Mock()
        self.coordinator.entry = SimpleNamespace(entry_id="entry", data={})
        self.coordinator._recovery_http_client = None
        session = Mock()
        replacement = object.__new__(hnap.Siren)
        replacement.device_type = hnap.DeviceType.SIREN
        replacement.is_playing = AsyncMock(
            side_effect=hnap.MethodCallError("still unavailable")
        )

        with (
            patch(
                "custom_components.hnap_device.coordinator.async_create_clientsession",
                return_value=session,
            ),
            patch(
                "custom_components.hnap_device.coordinator.async_create_device",
                new_callable=AsyncMock,
                return_value=replacement,
            ),
            patch(
                "custom_components.hnap_device.coordinator.async_create_issue"
            ) as create_issue,
            self.assertRaises(UpdateFailed),
        ):
            await self.coordinator._async_update_data()

        self.assertFalse(self.coordinator.connected)
        self.assertTrue(self.coordinator._connection_issue_created)
        self.assertIs(self.coordinator.device, replacement)
        create_issue.assert_called_once()

    async def test_detaches_recovery_session_on_close(self):
        session = Mock()
        self.coordinator._recovery_http_client = session

        await self.coordinator.async_close()

        session.detach.assert_called_once_with()
        self.assertIsNone(self.coordinator._recovery_http_client)


if __name__ == "__main__":
    unittest.main()
