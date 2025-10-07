#!/bin/bash
# Script to demonstrate the logging functionality

echo "=========================================="
echo "SCPI Server Logging Demo"
echo "=========================================="
echo ""
echo "Starting server with logging enabled..."
echo ""

cd /home/mede/Documenti/Github/SCPI_Emu

# Start server in background and capture output
python3 bin/scpiemu --instrument PSU_Keysight_E36312A --port 5026 2>&1 | tee server_log.txt &
SERVER_PID=$!

# Wait for server to start
sleep 2

echo "Server started (PID: $SERVER_PID)"
echo "Sending test commands..."
echo ""

# Send some test commands
{
    sleep 1
    echo "*IDN?"
    sleep 0.5
    echo "VOLT 5.0"
    sleep 0.5
    echo "CURR 2.0"
    sleep 0.5
    echo "MEAS:VOLT? CH1"
    sleep 0.5
    echo "MEAS:CURR? CH1"
    sleep 0.5
    echo "SYST:ERR?"
    sleep 0.5
} | nc 127.0.0.1 5026 &

# Wait a bit for commands to complete
sleep 5

# Stop server
kill $SERVER_PID 2>/dev/null

# Wait for server to stop
sleep 1

echo ""
echo "=========================================="
echo "Server Log Output:"
echo "=========================================="
cat server_log.txt
echo ""
echo "=========================================="
echo "Log file saved to: server_log.txt"
echo "=========================================="
