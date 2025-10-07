#!/usr/bin/env python3
"""Example of programmatic usage of the SCPI simulator"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scpiemu.instrument_loader import InstrumentLibrary
from scpiemu.instrument_simulator import InstrumentSimulator


def demo_power_supply():
    """Demo: Simulate a Keysight E36312A power supply"""
    print("\n" + "="*70)
    print("DEMO: Keysight E36312A Power Supply (3 channels)")
    print("="*70 + "\n")
    
    # Load instrument from library
    lib = InstrumentLibrary()
    instrument = lib.get_instrument('PSU_Keysight_E36312A')
    
    if not instrument:
        print("Error: Instrument not found!")
        return
    
    # Create simulator
    sim = InstrumentSimulator(instrument)
    
    print(f"Loaded instrument: {instrument.name}")
    print(f"Manufacturer: {instrument.manufacturer}")
    print(f"Available channels: {len(sim.channels)}\n")
    
    # Command sequence
    test_sequence = [
        ("*IDN?", None, "Identification"),
        ("VOLT", "3.3", "Set CH1 to 3.3V"),
        ("CURR", "1.5", "Set current limit 1.5A"),
        ("OUTP", "ON", "Enable CH1 output"),
        ("MEAS:VOLT?", "CH1", "Measure CH1 voltage"),
        ("MEAS:CURR?", "CH1", "Measure CH1 current"),
        ("MEAS:POW?", "CH1", "Measure CH1 power"),
        ("INST:SEL", "CH2", "Select channel 2"),
        ("VOLT", "12.0", "Set CH2 to 12V"),
        ("CURR", "0.5", "Set limit 0.5A"),
        ("MEAS:VOLT?", "CH2", "Measure CH2 voltage"),
        ("OUTP?", None, "Query output state"),
        ("*RST", None, "Reset instrument"),
        ("SYST:ERR?", None, "Check errors"),
    ]
    
    print(f"{'Command':<25s} {'Parameters':<15s} {'Response':<30s}")
    print("-"*70)
    
    for cmd, params, description in test_sequence:
        response = sim.process_command(cmd, params)
        param_str = params if params else "-"
        print(f"{cmd:<25s} {param_str:<15s} {response:<30s}")
    
    print("\n" + "="*70)
    print("Demo completed!")
    print("="*70 + "\n")


def demo_oscilloscope():
    """Demo: Simulate a Rigol DS1054Z oscilloscope"""
    print("\n" + "="*70)
    print("DEMO: Rigol DS1054Z Oscilloscope (4 channels, 50MHz)")
    print("="*70 + "\n")
    
    lib = InstrumentLibrary()
    instrument = lib.get_instrument('OSC_Rigol_DS1054Z')
    
    if not instrument:
        print("Error: Instrument not found!")
        return
    
    sim = InstrumentSimulator(instrument)
    
    print(f"Instrument: {instrument.name}")
    print(f"Bandwidth: {instrument.capabilities.get('bandwidth_mhz', 'N/A')} MHz")
    print(f"Channels: {instrument.capabilities.get('number_of_channels', 'N/A')}\n")
    
    test_sequence = [
        ("*IDN?", None),
        ("*RST", None),
        (":AUToscale", None),
        (":CHANnel1:SCALe", "1.0"),
        (":CHANnel1:SCALe?", None),
        (":TIMebase:SCALe", "0.001"),
        (":TIMebase:SCALe?", None),
        ("SYST:ERR?", None),
    ]
    
    print(f"{'Command':<30s} {'Response':<40s}")
    print("-"*70)
    
    for cmd, params in test_sequence:
        response = sim.process_command(cmd, params)
        print(f"{cmd + (' ' + params if params else ''):<30s} {response:<40s}")
    
    print("\n" + "="*70 + "\n")


def list_all_instruments():
    """List all available instruments"""
    print("\n" + "="*70)
    print("AVAILABLE INSTRUMENTS IN LIBRARY")
    print("="*70 + "\n")
    
    lib = InstrumentLibrary()
    
    for category in lib.list_categories():
        cat_name = category.replace('_', ' ').title()
        print(f"\n📁 {cat_name}")
        
        models = lib.list_models(category)
        for model in models:
            print(f"  • [{model['id']}]")
            print(f"    {model['name']} - {model['manufacturer']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    # Show available instruments
    list_all_instruments()
    
    # Demo power supply
    demo_power_supply()
    
    # Demo oscilloscope
    demo_oscilloscope()
    
    print("\nℹ️  To use the simulator over network:")
    print("   python3 bin/scpiemu --instrument PSU_Keysight_E36312A")
    print("   python3 test_client.py\n")
