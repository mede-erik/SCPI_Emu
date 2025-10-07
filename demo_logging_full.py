#!/usr/bin/env python3
"""
Demo script that shows server logging in action.
This script starts the server and client in the same process to demonstrate logging.
"""
import subprocess
import time
import socket
import sys

def run_demo():
    print("="*70)
    print("SCPI SERVER LOGGING DEMO")
    print("="*70)
    print()
    
    # Start server in a subprocess
    print("Starting SCPI server on port 5028...")
    server_process = subprocess.Popen(
        [sys.executable, '-u', 'bin/scpiemu', '--instrument', 'PSU_Keysight_E36312A', '--port', '5028'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for server to start
    time.sleep(2)
    
    print("Server started! Sending test commands...\n")
    print("-"*70)
    
    # Test commands
    commands = [
        '*IDN?',
        'VOLT 3.3',
        'CURR 1.5',
        'MEAS:VOLT? CH1',
        'MEAS:CURR? CH1',
        'SYST:ERR?',
    ]
    
    for cmd in commands:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect(('127.0.0.1', 5028))
                s.sendall((cmd + '\n').encode())
                response = s.recv(1024).decode().strip()
                
                print(f"Sent:     {cmd}")
                print(f"Response: {response}")
                
                # Read server output
                time.sleep(0.2)
                while True:
                    line = server_process.stdout.readline()
                    if not line:
                        break
                    print(f"[SERVER LOG] {line.rstrip()}")
                    if 'Response to' in line:
                        break
                
                print()
                
        except Exception as e:
            print(f"Error: {e}\n")
        
        time.sleep(0.3)
    
    print("-"*70)
    print("\nStopping server...")
    server_process.terminate()
    server_process.wait(timeout=3)
    
    print("\n" + "="*70)
    print("DEMO COMPLETED")
    print("="*70)
    print("\nThe server logged:")
    print("  - Each received command with client address")
    print("  - Each response sent back to the client")
    print("  - Connection and disconnection events")


if __name__ == '__main__':
    run_demo()
