# SCPI_Emu

Emulatore SCPI (Standard Commands for Programmable Instruments) con supporto per libreria di strumenti.

## Caratteristiche

- **Server TCP asincrono** basato su `asyncio`
- **Libreria strumenti** da file JSON (`instruments_lib.json`)
- **Simulazione automatica** di strumenti SCPI reali
- **14+ strumenti supportati**: Power Supplies (Keysight, TDK-Lambda, Rohde & Schwarz, OWON), Oscilloscopi (Rigol, Tektronix), Datalogger, Electronic Loads
- **Gestione stato multicanale** con valori di tensione/corrente simulati
- Parser SCPI estendibile
- Test unitari e di integrazione

## Installazione

Clona il repository e installa le dipendenze (opzionale per pytest):

```zsh
git clone <repo-url>
cd SCPI_Emu
pip install -r requirements.txt  # opzionale, solo per pytest
```

## Utilizzo

### Avviare il server

**Metodo 1: Script launcher**

```zsh
python3 bin/scpiemu
```

**Metodo 2: Modulo Python**

```zsh
python3 -m scpiemu.server
```

**Metodo 3: Eseguibile diretto**

```zsh
chmod +x bin/scpiemu
./bin/scpiemu
```

### Opzioni

```zsh
python3 bin/scpiemu --help

# Lista strumenti disponibili
python3 bin/scpiemu --list-instruments

# Simula Keysight E36312A (default)
python3 bin/scpiemu --instrument PSU_Keysight_E36312A

# Simula Rigol DS1054Z Oscilloscopio
python3 bin/scpiemu --instrument OSC_Rigol_DS1054Z --port 5555

# Simula TDK-Lambda GEN80-19 Power Supply
python3 bin/scpiemu --instrument PSU_TDK_GEN80_19

# Usa variabili d'ambiente
SCPI_INSTRUMENT=PSU_OWON_ODP3033 python3 bin/scpiemu
```

### Client di test

**Con netcat:**

```zsh
# Invia singolo comando
printf "*IDN?\n" | nc 127.0.0.1 5025

# Sessione interattiva
nc 127.0.0.1 5025
```

**Con Python:**

```python
import socket

def send_scpi(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 5025))
        s.sendall((cmd + '\n').encode())
        return s.recv(1024).decode().strip()

print(send_scpi('*IDN?'))  # SCPI_Emu,Model1,Serial0001,1.0
```

**Script client incluso:**

```zsh
python3 test_client.py
```

## Strumenti Supportati

L'emulatore include una libreria di **14+ strumenti reali** definiti in `instruments_lib.json`:

### Power Supplies
- **Keysight E36300 Series**: E36312A (3 canali), E36311A (2 canali)
- **TDK-Lambda GEN Series**: GEN80-19, GEN80-30, GEN100-15
- **Rohde & Schwarz HPM Series**: HPM4040 (4 canali)
- **OWON**: SPE6103, ODP3033 (3 canali)

### Oscilloscopi
- **Rigol DS1000Z Series**: DS1054Z (4ch, 50MHz), DS1104Z Plus (4ch, 100MHz)
- **Tektronix MSO Series**: MSO54 (4ch, 500MHz), MSO58 (8ch, 1GHz)

### Dataloggers
- **Keysight 34972A**: Data Acquisition Unit

### Electronic Loads
- **Chroma 6330A**: DC Electronic Load Mainframe

Per ogni strumento, il simulatore:
- Gestisce lo stato dei canali (tensione, corrente, output on/off)
- Risponde ai comandi IEEE 488.2 standard (*IDN?, *RST, *CLS, ecc.)
- Supporta comandi specifici del modello (MEAS:VOLT?, CURR, OUTP, ecc.)
- Simula valori di misura realistici con piccole variazioni

## Comandi SCPI Comuni

### IEEE 488.2 Standard

| Comando | Descrizione | Risposta |
|---------|-------------|----------|
| `*IDN?` | Identificazione | `<Manufacturer>,<Model>,<Serial>,<Version>` |
| `*RST` | Reset strumento | - |
| `*CLS` | Clear status | - |
| `SYST:ERR?` | Query errore | `0,No error` |

### Power Supply (esempio Keysight E36312A)

| Comando | Descrizione | Esempio |
|---------|-------------|---------|
| `VOLT 3.3` | Imposta tensione | - |
| `CURR 1.5` | Imposta corrente | - |
| `OUTP ON` | Abilita output | - |
| `OUTP OFF` | Disabilita output | - |
| `MEAS:VOLT? CH1` | Leggi tensione canale 1 | `3.3010` |
| `MEAS:CURR? CH1` | Leggi corrente canale 1 | `1.4998` |
| `MEAS:POW? CH1` | Leggi potenza canale 1 | `4.9507` |
| `INST:SEL CH2` | Seleziona canale 2 | - |

## Comandi SCPI supportati

| Comando | Descrizione | Esempio risposta |
|---------|-------------|------------------|
| `*IDN?` | Identificazione strumento | `SCPI_Emu,Model1,Serial0001,1.0` |
| `MEAS:VOLT?` | Misura tensione simulata | `3.1415` (valore casuale 0-5V) |
| `SYST:ERR?` | Query errore sistema | `0,No error` |
| `SYST:EXIT` | Chiude connessione | `Bye` |

## Estendere i comandi

### Metodo 1: Aggiungi strumento alla libreria

Modifica `instruments_lib.json` per aggiungere un nuovo modello o serie:

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

Poi avvia con:

```zsh
python3 bin/scpiemu --instrument PSU_MyCustom_Model1
```

### Metodo 2: Aggiungi comandi al parser (legacy)

Aggiungi nuovi comandi in `src/scpiemu/parser.py`:

```python
from scpiemu.parser import register

@register("CONF:VOLT")
def configure_voltage(params):
    # params contiene gli argomenti dopo il comando
    return "OK"

@register("MEAS:CURR")
def measure_current(params):
    import random
    return f"{random.uniform(0, 1):.4f}"
```

## Test

**Esegui tutti i test:**

```zsh
# Con pytest (se installato)
pytest -v

# Senza dipendenze esterne
python3 scripts/run_tests.py
```

**Esegui test di integrazione:**

```zsh
python3 tests/test_integration.py
```

**Test singolo:**

```zsh
python3 tests/test_parser.py
```

## Struttura progetto

```
SCPI_Emu/
├── bin/
│   └── scpiemu              # Script launcher
├── src/
│   └── scpiemu/
│       ├── __init__.py
│       ├── server.py        # Server TCP asincrono
│       └── parser.py        # Parser e registry comandi
├── tests/
│   ├── test_parser.py       # Test parser
│   ├── test_command_handler.py  # Test handler
│   └── test_integration.py # Test integrazione TCP
├── scripts/
│   └── run_tests.py         # Runner test senza pytest
├── test_client.py           # Client di esempio
├── requirements.txt
└── README.md
```

## Troubleshooting

**Porta già in uso:**

```zsh
# Usa una porta diversa
python3 bin/scpiemu --port 5026
```

**ModuleNotFoundError:**

I file includono già il path setup automatico. Se riscontri problemi:

```zsh
# Esporta PYTHONPATH manualmente
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
python3 -m scpiemu.server
```

**Errore di binding su 172.0.0.1:**

Verifica variabili d'ambiente:

```zsh
unset SCPI_HOST
python3 bin/scpiemu
```

## Licenza

MIT License - vedi file LICENSE

