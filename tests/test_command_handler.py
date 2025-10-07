import sys
import os

# Add src to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scpiemu.server import handle_command


def test_idn_contains_name():
    resp = handle_command('*IDN?')
    assert 'SCPI_Emu' in resp


def test_measure_voltage_is_number():
    resp = handle_command('MEAS:VOLT?')
    # deve essere convertibile in float
    float(resp)


def test_unknown_command_returns_err():
    assert handle_command('FOO') == 'ERR'
