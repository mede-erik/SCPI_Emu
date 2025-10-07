import sys
import os

# Add src to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scpiemu import parser


def test_idn_direct():
    assert 'SCPI_Emu' in parser.handle('*IDN?')


def test_meas_volt_numeric():
    v = parser.handle('MEAS:VOLT?')
    float(v)


def test_unknown():
    assert parser.handle('FOOBAR') == 'ERR'
