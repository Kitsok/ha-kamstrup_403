"""Test setup."""

import logging
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.kamstrup_403 import async_setup_entry
from custom_components.kamstrup_403.const import CONF_BAUDRATE, CONF_DEBUG, DOMAIN
from custom_components.kamstrup_403.coordinator import KamstrupUpdateCoordinator

from . import get_mock_config_entry, setup_integration, unload_integration


async def test_setup_and_unload_entry(hass: HomeAssistant) -> None:
    """Test entry setup and unload."""
    config_entry = await setup_integration(hass)

    # Check that the client is stored as runtime_data
    assert isinstance(config_entry.runtime_data, KamstrupUpdateCoordinator)

    await unload_integration(hass, config_entry)


async def test_setup_entry_exception(hass: HomeAssistant) -> None:
    """Test setup entry raises ConfigEntryNotReady on connection error."""
    # Create config entry but don't set it up through HA's system
    config_entry = get_mock_config_entry()
    config_entry.add_to_hass(hass)

    # Mock the Kamstrup class to raise an exception during instantiation
    with patch("custom_components.kamstrup_403.Kamstrup") as mock_kamstrup_class:
        mock_kamstrup_class.side_effect = Exception("Connection failed")

        # This should raise ConfigEntryNotReady due to connection error
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, config_entry)


async def test_setup_entry_no_port(hass: HomeAssistant) -> None:
    """Test setup entry raises ValueError on missing port."""
    # Create config entry but don't set it up through HA's system
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry",
        data={},
    )
    config_entry.add_to_hass(hass)

    # This should raise ValueError due to missing port
    with pytest.raises(ValueError):  # noqa: PT011
        await async_setup_entry(hass, config_entry)


async def test_async_reload_entry(hass: HomeAssistant) -> None:
    """Test reloading the entry."""
    config_entry = await setup_integration(hass)

    with patch("custom_components.kamstrup_403.async_reload_entry") as mock_reload_entry:
        assert len(mock_reload_entry.mock_calls) == 0
        hass.config_entries.async_update_entry(config_entry, options={"something": "else"})
        assert len(mock_reload_entry.mock_calls) == 1


async def test_setup_entry_enables_debug_logging(hass: HomeAssistant) -> None:
    """Test setup entry applies debug logger levels."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_debug",
        data={CONF_PORT: "/dev/ttyUSB0"},
        options={CONF_DEBUG: True},
    )
    config_entry.add_to_hass(hass)

    integration_logger = Mock()
    pykamstrup_logger = Mock()
    with patch("custom_components.kamstrup_403.logging.getLogger") as mock_get_logger:
        mock_get_logger.side_effect = [integration_logger, pykamstrup_logger]
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_get_logger.call_args_list == [
        call("custom_components.kamstrup_403"),
        call("custom_components.kamstrup_403.pykamstrup"),
    ]
    integration_logger.setLevel.assert_called_once_with(logging.DEBUG)
    pykamstrup_logger.setLevel.assert_called_once_with(logging.DEBUG)


async def test_setup_entry_uses_configured_baudrate(hass: HomeAssistant) -> None:
    """Test setup entry applies configured baudrate."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_baudrate",
        data={CONF_PORT: "/dev/ttyUSB0"},
        options={CONF_BAUDRATE: 2400},
    )
    config_entry.add_to_hass(hass)

    mock_client = AsyncMock()
    mock_client.get_values.return_value = {
        60: (1234.0, "GJ"),
        68: (5678.0, "m³"),
        80: (100.0, "kW"),
        99: (0, None),
        113: (1, None),
        1001: (12345678, None),
        1004: (12345.0, "h"),
    }

    with patch("custom_components.kamstrup_403.Kamstrup", return_value=mock_client) as mock_kamstrup:
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    mock_kamstrup.assert_called_once_with(
        url="/dev/ttyUSB0",
        baudrate=2400,
        timeout=1.0,
        serial_communication_logging=False,
    )
