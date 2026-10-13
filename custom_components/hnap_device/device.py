"""HNAP device construction helpers."""

from collections.abc import Mapping
from typing import Any

import hnap


class UnsupportedDeviceType(TypeError):
    """Raised when an HNAP device does not expose a supported module type."""


def device_class_from_info(info: Mapping[str, Any]) -> type[hnap.Device]:
    """Select the supported device subclass from already-fetched device info."""
    module_types = info.get("ModuleTypes", [])
    if isinstance(module_types, str):
        module_types = [module_types]
    if not isinstance(module_types, (list, tuple)):
        raise UnsupportedDeviceType(module_types)

    if "Audio Renderer" in module_types:
        device_class = hnap.Siren
    elif "Camera" in module_types:
        device_class = hnap.Camera
    elif "Motion Sensor" in module_types:
        device_class = hnap.Motion
    else:
        raise UnsupportedDeviceType(module_types)

    return device_class


def create_device(client: hnap.SoapClient, info: Mapping[str, Any]) -> hnap.Device:
    """Create a device using already-fetched device info."""
    return device_class_from_info(info)(client=client)
