# SCPI_Emu

SCPI (Standard Commands for Programmable Instruments) emulator with instrument library support.

## ⚠️ Disclaimer

This project was developed **exclusively for testing purposes** of the [Open-Lab-Automation](https://github.com/mede-erik/Open-Lab-Automation) software. The emulator is designed to simulate SCPI instruments in a development and testing environment, **NOT for use in production applications or contexts that may involve risks to people or property**.

**The author assumes no responsibility** for direct, indirect, incidental, special, or consequential damages arising from the use or inability to use this software, including but not limited to damage to devices, data loss, business interruption, or any other commercial damage or loss.

**Development Note:** Most of the code in this project was generated with the assistance of GitHub Copilot, an AI-powered programming tool.

## Features

- **Asynchronous TCP server** based on `asyncio`
- **Instrument library** from JSON file (`instruments_lib.json`)
- **Automatic simulation** of real SCPI instruments
- **14+ supported instruments**: Power Supplies (Keysight, TDK-Lambda, Rohde & Schwarz, OWON), Oscilloscopes (Rigol, Tektronix), Dataloggers, Electronic Loads
- **Multi-channel state management** with simulated voltage/current values
- **Built-in logging** of all received commands and responses
- Extensible SCPI parser
- Unit and integration tests

## Installation

Clone the repository and install dependencies (optional for pytest):

```zsh
git clone <repo-url>
cd SCPI_Emu
pip install -r requirements.txt  # optional, only for pytest
```

## Usage

### Starting the server

### Starting the server

**Method 1: Launcher script**

```zsh
python3 bin/scpiemu
```

**Method 2: Python module**

```zsh
python3 -m scpiemu.server
```

**Method 3: Direct executable**

```zsh
chmod +x bin/scpiemu
./bin/scpiemu
```

### Options

```zsh
python3 bin/scpiemu --help

# List available instruments
python3 bin/scpiemu --list-instruments

# Simulate Keysight E36312A (default)
python3 bin/scpiemu --instrument PSU_Keysight_E36312A

# Simulate Rigol DS1054Z Oscilloscope
python3 bin/scpiemu --instrument OSC_Rigol_DS1054Z --port 5555

# Simulate TDK-Lambda GEN80-19 Power Supply
python3 bin/scpiemu --instrument PSU_TDK_GEN80_19

# Use environment variables
SCPI_INSTRUMENT=PSU_OWON_ODP3033 python3 bin/scpiemu
```

### Test client

**With netcat:**

```zsh
# Send single command
printf "*IDN?\n" | nc 127.0.0.1 5025

# Interactive session
nc 127.0.0.1 5025
```

**With Python:**

```python
import socket

def send_scpi(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 5025))
        s.sendall((cmd + '\n').encode())
        return s.recv(1024).decode().strip()

print(send_scpi('*IDN?'))  # SCPI_Emu,Model1,Serial0001,1.0
```

**Included client script:**

```zsh
python3 test_client.py
```

## Logging

The server automatically prints all activity to the terminal with clear visual indicators:

**Console output example:**

```
✅ Loaded instrument: Keysight E36312A
🚀 SCPI emulator listening on ('127.0.0.1', 5025)
📥 Connection from ('127.0.0.1', 54321)
📨 Received: *IDN?
📤 Response: Keysight Technologies,E36312A,SN001,1.0
📨 Received: VOLT 5.0
📤 Response: 
📨 Received: MEAS:VOLT? CH1
📤 Response: 5.0012
📤 Connection closed ('127.0.0.1', 54321)
```

The output shows:
- ✅ **Instrument loaded** - Confirms which instrument is being simulated
- 🚀 **Server started** - Shows the listening address and port
- 📥 **New connection** - Client IP and port when connecting
- 📨 **Received command** - Every SCPI command received from clients
- 📤 **Response sent** - The response returned to the client
- 📤 **Connection closed** - When a client disconnects

This real-time output helps with:
- Debugging SCPI command sequences
- Understanding client-server interactions
- Monitoring instrument simulator behavior
- Troubleshooting communication issues

## Supported Instruments

The emulator includes a library of **14+ real instruments** defined in `instruments_lib.json`:


### Power Supplies

- **Keysight E36300 Series**: E36312A (3 channels), E36311A (2 channels)
- **TDK-Lambda GEN Series**: GEN80-19, GEN80-30, GEN100-15
- **Rohde & Schwarz HPM Series**: HPM4040 (4 channels)
- **OWON**: SPE6103, ODP3033 (3 channels)

### Oscilloscopes

- **Rigol DS1000Z Series**: DS1054Z (4ch, 50MHz), DS1104Z Plus (4ch, 100MHz)
- **Tektronix MSO Series**: MSO54 (4ch, 500MHz), MSO58 (8ch, 1GHz)

### Dataloggers

- **Keysight 34972A**: Data Acquisition Unit

### Electronic Loads

- **Chroma 6330A**: DC Electronic Load Mainframe

For each instrument, the simulator:

- Manages channel state (voltage, current, output on/off)
- Responds to IEEE 488.2 standard commands (*IDN?, *RST, *CLS, etc.)
- Supports model-specific commands (MEAS:VOLT?, CURR, OUTP, etc.)
- Simulates realistic measurement values with small variations

## Common SCPI Commands

### IEEE 488.2 Standard

| Command | Description | Response |
|---------|-------------|----------|
| `*IDN?` | Identification | `<Manufacturer>,<Model>,<Serial>,<Version>` |
| `*RST` | Reset instrument | - |
| `*CLS` | Clear status | - |
| `SYST:ERR?` | Error query | `0,No error` |

### Power Supply (example Keysight E36312A)

| Command | Description | Example |
|---------|-------------|---------|
| `VOLT 3.3` | Set voltage | - |
| `CURR 1.5` | Set current | - |
| `OUTP ON` | Enable output | - |
| `OUTP OFF` | Disable output | - |
| `MEAS:VOLT? CH1` | Read voltage channel 1 | `3.3010` |
| `MEAS:CURR? CH1` | Read current channel 1 | `1.4998` |
| `MEAS:POW? CH1` | Read power channel 1 | `4.9507` |
| `INST:SEL CH2` | Select channel 2 | - |

## Supported SCPI Commands

| Command | Description | Example Response |
|---------|-------------|------------------|
| `*IDN?` | Instrument identification | `SCPI_Emu,Model1,Serial0001,1.0` |
| `MEAS:VOLT?` | Simulated voltage measurement | `3.1415` (random value 0-5V) |
| `SYST:ERR?` | System error query | `0,No error` |
| `SYST:EXIT` | Close connection | `Bye` |

## Extending Commands

### Method 1: Add instrument to library

Edit `instruments_lib.json` to add a new model or series:

```json
{
  "instrument_library": {
    "power_supplies_series": [
      {
        "series_id": "My_Custom_Series",
        "series_name": "My Custom Power Supply",
        "common_scpi_commands": {
          "identification_query": "*IDN?",
          "set_voltage": "VOLT {value}",
          "read_voltage": "MEAS:VOLT?"
        },
        "models": [
          {
            "id": "PSU_MyCustom_Model1",
            "name": "My Custom PSU",
            "manufacturer": "My Company",
            "model": "Model1",
            "capabilities": {
              "number_of_channels": 1,
              "channels": [
                {
                  "channel_id": "CH1",
                  "label": "Main Output",
                  "voltage_output": {"min": 0.0, "max": 30.0, "units": "V"},
                  "current_output": {"min": 0.0, "max": 5.0, "units": "A"}
                }
              ]
            },
            "scpi_commands": {}
          }
        ]
      }
    ]
  }
}
```

Then start with:

```zsh
python3 bin/scpiemu --instrument PSU_MyCustom_Model1
```

### Method 2: Add commands to parser (legacy)

Add new commands in `src/scpiemu/parser.py`:

```python
from scpiemu.parser import register

@register("CONF:VOLT")
def configure_voltage(params):
    # params contains arguments after the command
    return "OK"

@register("MEAS:CURR")
def measure_current(params):
    import random
    return f"{random.uniform(0, 1):.4f}"
```

## Tests

**Run all tests:**

```zsh
# With pytest (if installed)
pytest -v

# Without external dependencies
python3 scripts/run_tests.py
```

**Run integration tests:**

```zsh
python3 tests/test_integration.py
```

**Single test:**

```zsh
python3 tests/test_parser.py
```

## Project Structure

```text
SCPI_Emu/
├── bin/
│   └── scpiemu              # Launcher script
├── src/
│   └── scpiemu/
│       ├── __init__.py
│       ├── server.py        # Async TCP server
│       └── parser.py        # Parser and command registry
├── tests/
│   ├── test_parser.py       # Parser tests
│   ├── test_command_handler.py  # Handler tests
│   └── test_integration.py # TCP integration tests
├── scripts/
│   └── run_tests.py         # Test runner without pytest
├── test_client.py           # Example client
├── requirements.txt
└── README.md
```

## Troubleshooting

**Port already in use:**

```zsh
# Use a different port
python3 bin/scpiemu --port 5026
```

**ModuleNotFoundError:**

Files already include automatic path setup. If you encounter issues:

```zsh
# Export PYTHONPATH manually
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
python3 -m scpiemu.server
```

**Binding error on 172.0.0.1:**

Check environment variables:

```zsh
unset SCPI_HOST
python3 bin/scpiemu
```

## Project Information

- **Purpose**: Testing for [Open-Lab-Automation](https://github.com/mede-erik/Open-Lab-Automation) software
- **Recommended environment**: Development and testing only
- **Development**: Code generated with GitHub Copilot assistance
- **Author**: [@mede-erik](https://github.com/mede-erik)

## License

MIT License - see LICENSE file

**DISCLAIMER**: This software is provided "as is", without warranty of any kind, express or implied. Use of this software is at your own risk.

