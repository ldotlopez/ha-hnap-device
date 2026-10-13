# Copilot instructions

## Project overview

This repository is a Home Assistant custom integration for locally polled HNAP devices. The integration code lives in `custom_components/hnap_device`; `hnap` is the protocol client dependency declared in `manifest.json`.

The config flow in `config_flow.py` creates devices and validates credentials in Home Assistant's executor, identifies devices by MAC address, and records the supported platforms in the config entry. `__init__.py` creates the device and `HNapCoordinator`, stores shared objects in `entry.runtime_data`, then forwards setup to those platforms. The coordinator polls every 30 seconds; entities in `binary_sensor.py` and `siren.py` read its data, and blocking device operations must run in the executor. `entity.py` centralizes shared entity and device-registry metadata.

The config flow currently recognizes cameras, but `camera.py` is only a placeholder and does not add an entity. The README lists motion sensors and sirens as the implemented platforms.

The integration also registers a device-targeted `hnap_device.call` service in `__init__.py`; keep its behavior and UI description in sync with `services.yaml`.

## Development commands

Use Python 3.13.2 or later; `.python-version` pins 3.13.2. `uv sync` installs the project’s development dependency group, including Home Assistant and pre-commit.

- Run configured lint/format and file checks: `uv run pre-commit run --all-files`
- Run hooks on changed files: `uv run pre-commit run --files custom_components/hnap_device/<file>`
- Run an individual hook on changed files, for example: `uv run pre-commit run black --files custom_components/hnap_device/<file>` (also available: `isort`, `pyupgrade`, `check-json`, and other hooks in `.pre-commit-config.yaml`)

There is no tracked test suite or build command. CI runs Home Assistant `hassfest` and HACS validation; CodeQL performs Python analysis.

## Repository conventions

- Keep Home Assistant's async event loop non-blocking: run synchronous `hnap` client calls through `hass.async_add_executor_job`.
- Share device/session state through typed `HNapConfigEntry.runtime_data`; have entities consume coordinator data rather than independently polling.
- When adding a device capability, update the config-flow platform detection and add the corresponding platform setup/entity implementation. Keep platform and entity identity consistent with existing entry-ID/platform unique IDs.
- Keep user-facing config-flow text in `strings.json` and translated files under `translations/`; keep service fields and targeting documented in `services.yaml`.
- The integration manifest controls its external `hnap` dependency and Home Assistant integration metadata; update its version consistently with the project/release version when preparing a release.
- Do not sign commits or add attribution trailers: do not enable or request GPG/SSH commit signing, add `Signed-off-by` or `Co-authored-by` trailers, or use `--signoff`.
