import asyncio
import logging
import os

from . import parser
from .instrument_loader import InstrumentLibrary
from .instrument_simulator import InstrumentSimulator

DEFAULT_HOST = os.getenv("SCPI_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("SCPI_PORT", "5025"))

# Global simulator instance
_simulator = None
_instrument_id = None


def init_simulator(instrument_id: str):
    """Initialize the simulator with the specified instrument ID."""
    global _simulator, _instrument_id
    _instrument_id = instrument_id
    
    lib = InstrumentLibrary()
    instrument = lib.get_instrument(instrument_id)
    if instrument:
        _simulator = InstrumentSimulator(instrument)
        logging.info(f"Loaded instrument: {instrument.name}")
        print(f"✅ Loaded instrument: {instrument.name}")
        return True
    else:
        logging.error(f"Instrument '{instrument_id}' not found in library")
        print(f"❌ Error: Instrument '{instrument_id}' not found in library")
        return False


def get_simulator():
    """Get the simulator instance."""
    return _simulator


def handle_command(cmd: str) -> str:
    """Backward-compatible wrapper used by older tests: delegate to parser."""
    return parser.handle(cmd)


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    peer = writer.get_extra_info("peername")
    logging.info("Connection from %s", peer)
    print(f"📥 Connection from {peer}")
    
    # Get simulator
    sim = get_simulator()
    use_simulator = sim is not None
    
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            line = data.decode(errors="ignore").strip()
            logging.info("Received from %s: %s", peer, line)
            print(f"📨 Received: {line}")
            
            # Use simulator if available, otherwise fallback to parser
            if use_simulator:
                # Separate command and parameters
                parts = line.split(None, 1)
                cmd = parts[0] if parts else line
                params = parts[1] if len(parts) > 1 else None
                resp = sim.process_command(cmd, params)
            else:
                resp = parser.handle(line)
            
            # Log the response
            logging.info("Response to %s: %s", peer, resp)
            print(f"📤 Response: {resp}")
            
            # Ensure response ends with LF
            writer.write((resp + "\n").encode())
            await writer.drain()
            if line.upper() in ("SYST:EXIT", "EXIT", "SYSTEM:EXIT"):
                break
    except Exception:
        logging.exception("Error handling client %s", peer)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        logging.info("Closed connection %s", peer)
        print(f"📤 Connection closed {peer}")


async def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    server = await asyncio.start_server(handle_client, host, port)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    logging.info("SCPI emulator listening on %s", addrs)
    print(f"🚀 SCPI emulator listening on {addrs}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    import argparse

    default_instrument = os.getenv("SCPI_INSTRUMENT", "PSU_Keysight_E36312A")
    
    p = argparse.ArgumentParser(description="SCPI emulator (async TCP)")
    p.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind (default: {DEFAULT_HOST})")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind (default: {DEFAULT_PORT})")
    p.add_argument("--instrument", default=default_instrument, 
                   help=f"Instrument ID from library (default: {default_instrument})")
    p.add_argument("--list-instruments", action="store_true",
                   help="List available instruments and exit")
    args = p.parse_args()
    
    # List instruments if requested
    if args.list_instruments:
        from .instrument_loader import print_instruments_menu
        print_instruments_menu()
        import sys
        sys.exit(0)
    
    # Initialize simulator with chosen instrument
    init_simulator(args.instrument)
    
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\nshutting down")
