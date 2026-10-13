"""Tests for HNAP device selection and coordinator recovery."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import hnap
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from custom_components.hnap_device.coordinator import HNapCoordinator
from custom_components.hnap_device.device import (
    UnsupportedDeviceType,
    device_class_from_info,
)


class TestCreateDevice(unittest.TestCase):
    def test_selects_siren_before_other_matching_types(self):
        device_class = device_class_from_info(
            {"ModuleTypes": ["Camera", "Motion Sensor", "Audio Renderer"]}
        )

        self.assertIs(device_class, hnap.Siren)

    def test_selects_camera_before_motion(self):
        device_class = device_class_from_info(
            {"ModuleTypes": ["Motion Sensor", "Camera"]}
        )

        self.assertIs(device_class, hnap.Camera)

    def test_selects_motion(self):
        device_class = device_class_from_info({"ModuleTypes": ["Motion Sensor"]})

        self.assertIs(device_class, hnap.Motion)

    def test_accepts_a_single_module_type(self):
        device_class = device_class_from_info({"ModuleTypes": "Camera"})

        self.assertIs(device_class, hnap.Camera)

    def test_rejects_unsupported_module_types(self):
        with self.assertRaises(UnsupportedDeviceType):
            device_class_from_info({"ModuleTypes": ["Unknown"]})


class TestCoordinatorRecovery(unittest.TestCase):
    def test_recreates_original_device_type_without_discovery(self):
        class Device:
            def __init__(self, client):
                self.client = client

        old_device = Device(Mock())
        client = Mock()
        coordinator = object.__new__(HNapCoordinator)
        coordinator.device = old_device
        coordinator.device_class = type(old_device)
        coordinator.entry = SimpleNamespace(
            data={
                CONF_HOST: "host",
                CONF_PASSWORD: "password",
                CONF_USERNAME: "username",
            }
        )
        coordinator._reconnect_needed = True

        with patch(
            "custom_components.hnap_device.coordinator.hnap.soapclient.SoapClient",
            return_value=client,
        ) as client_factory:
            device, data = coordinator._poll()

        self.assertIsInstance(device, Device)
        self.assertIs(device.client, client)
        self.assertEqual(data, {})
        client_factory.assert_called_once()
        client.authenticate.assert_called_once_with(force=True)
        client.device_info.assert_not_called()


if __name__ == "__main__":
    unittest.main()
