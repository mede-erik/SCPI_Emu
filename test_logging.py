#!/usr/bin/env python3
"""Test script to demonstrate logging functionality"""
import socket
import time

HOST = '127.0.0.1'
PORT = 5026

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


def test_logging():
    """Test sequence to verify logging functionality"""
    print("="*60)
    print("Testing SCPI Logging Functionality")
    print("="*60)
    print("\nCheck server terminal for log output!")
    print("-"*60)
    
    # Test commands
    commands = [
        '*IDN?',
        'VOLT 5.0',
        'CURR 2.0',
        'OUTP ON',
        'MEAS:VOLT? CH1',
        'MEAS:CURR? CH1',
        'MEAS:POW? CH1',
        'SYST:ERR?',
    ]
    
    for cmd in commands:
        print(f"Sending: {cmd}")
        resp = send_command(cmd)
        print(f"  Response: {resp}")
        time.sleep(0.3)  # Small delay to see logs clearly
    
    print("\n" + "="*60)
    print("Test completed! Check server logs above.")
    print("="*60)


if __name__ == '__main__':
    test_logging()
