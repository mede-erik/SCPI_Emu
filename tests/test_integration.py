"""Test di integrazione TCP per il server SCPI"""
import sys
import os
import asyncio
import socket

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scpiemu import server


async def test_server_integration():
    """Test che avvia il server e invia comandi"""
    HOST = '127.0.0.1'
    PORT = 5555  # porta di test
    
    # Avvia server in background
    server_task = asyncio.create_task(server.main(HOST, PORT))
    
    # Aspetta che il server sia pronto
    await asyncio.sleep(0.5)
    
    # Testa comandi
    commands = [
        ('*IDN?', 'SCPI_Emu'),
        ('MEAS:VOLT?', None),  # deve essere un numero
        ('SYST:ERR?', '0,No error'),
    ]
    
    for cmd, expected in commands:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        
        # Invia comando
        writer.write((cmd + '\n').encode())
        await writer.drain()
        
        # Leggi risposta
        response = await reader.readline()
        resp_str = response.decode().strip()
        
        print(f"{cmd:20s} -> {resp_str}")
        
        # Verifica
        if expected:
            assert expected in resp_str, f"Expected '{expected}' in '{resp_str}'"
        
        writer.close()
        await writer.wait_closed()
    
    # Chiudi server
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
    
    print("\n✅ Tutti i test di integrazione passati!")


if __name__ == '__main__':
    asyncio.run(test_server_integration())
