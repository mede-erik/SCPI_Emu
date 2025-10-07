#!/usr/bin/env python3
"""Simple SCPI client for testing instrument emulator"""
import socket
import sys

HOST = '127.0.0.1'
PORT = 5025


def send_command(cmd: str) -> str:
    """Send a command and return the response"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((HOST, PORT))
            s.sendall((cmd + '\n').encode())
            response = s.recv(1024).decode().strip()
            return response
    except Exception as e:
        return f"ERROR: {e}"


def test_power_supply():
    """Test sequence for a power supply instrument"""
    print("="*60)
    print("Testing SCPI Power Supply Emulator")
    print("="*60)
    
    # Test commands
    commands = [
        ('*IDN?', 'Get instrument identification'),
        ('*RST', 'Reset instrument'),
        ('VOLT 5.0', 'Set voltage to 5.0V'),
        ('CURR 2.0', 'Set current limit to 2.0A'),
        ('OUTP ON', 'Enable output'),
        ('MEAS:VOLT? CH1', 'Measure voltage on channel 1'),
        ('MEAS:CURR? CH1', 'Measure current on channel 1'),
        ('MEAS:POW? CH1', 'Measure power on channel 1'),
        ('OUTP?', 'Query output state'),
        ('OUTP OFF', 'Disable output'),
        ('SYST:ERR?', 'Check for errors'),
    ]
    
    print(f"\nConnecting to {HOST}:{PORT}...")
    print(f"{'Command':<20s} {'Description':<30s} {'Response':<20s}")
    print("-"*60)
    
    for cmd, description in commands:
        try:
            resp = send_command(cmd)
            print(f"{cmd:<20s} {description:<30s} {resp:<20s}")
        except Exception as e:
            print(f"{cmd:<20s} {description:<30s} ERROR: {e}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    # Override host/port if provided
    if len(sys.argv) >= 2:
        HOST = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            PORT = int(sys.argv[2])
        except ValueError:
            pass
    
    test_power_supply()
