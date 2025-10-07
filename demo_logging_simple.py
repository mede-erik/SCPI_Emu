#!/usr/bin/env python3
"""
Simple demonstration of server logging functionality.
Run this script to see the server logs in action.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import socket
import time
from scpiemu.server import main as server_main, init_simulator

def send_command(port: int, cmd: str) -> str:
    """Send a command and return the response"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect(('127.0.0.1', port))
            s.sendall((cmd + '\n').encode())
            return s.recv(1024).decode().strip()
    except Exception as e:
        return f"ERROR: {e}"


async def run_client_tests(port: int):
    """Run client test commands after a delay"""
    await asyncio.sleep(2)  # Wait for server to start
    
    print("\n" + "="*70)
    print("CLIENT: Sending test commands")
    print("="*70 + "\n")
    
    commands = [
        '*IDN?',
        'VOLT 3.3',
        'CURR 1.5',
        'MEAS:VOLT? CH1',
        'MEAS:CURR? CH1',
        'SYST:ERR?',
    ]
    
    for cmd in commands:
        resp = await asyncio.to_thread(send_command, port, cmd)
        print(f"CLIENT: Sent '{cmd}' -> Response: '{resp}'")
        await asyncio.sleep(0.5)
    
    print("\n" + "="*70 + "\n")


async def run_demo():
    """Run the demo with server and client"""
    import logging
    
    port = 5030
    
    # Configure logging BEFORE anything else
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    
    print("\n" + "="*70)
    print("SCPI SERVER LOGGING DEMONSTRATION")
    print("="*70)
    print("\nStarting server with logging enabled...")
    print("Watch for log messages showing:")
    print("  - Received commands from client")
    print("  - Responses sent to client")
    print("  - Connection events")
    print("="*70 + "\n")
    
    # Initialize simulator
    init_simulator('PSU_Keysight_E36312A')
    
    # Create tasks for server and client
    server_task = asyncio.create_task(server_main('127.0.0.1', port))
    client_task = asyncio.create_task(run_client_tests(port))
    
    # Wait for client to finish
    await client_task
    
    # Cancel server
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
    
    print("\n" + "="*70)
    print("DEMO COMPLETED")
    print("="*70)
    print("\nYou should have seen log messages like:")
    print("  [timestamp] Connection from ('127.0.0.1', port)")
    print("  [timestamp] Received from ('127.0.0.1', port): *IDN?")
    print("  [timestamp] Response to ('127.0.0.1', port): Keysight...")
    print("  [timestamp] Closed connection ('127.0.0.1', port)")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nDemo interrupted")
