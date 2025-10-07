"""Instrument state simulator with dynamic SCPI command generation.

Simulates the internal state of a SCPI instrument and automatically generates
responses to commands based on the JSON definition.
"""
import re
import random
from typing import Dict, Any, Optional, List

try:
    from .instrument_loader import InstrumentModel, InstrumentLibrary
except ImportError:
    from instrument_loader import InstrumentModel, InstrumentLibrary


class ChannelState:
    """State of an instrument channel."""
    
    def __init__(self, channel_id: str, voltage_range: tuple, current_range: tuple):
        self.channel_id = channel_id
        self.voltage_range = voltage_range  # (min, max)
        self.current_range = current_range  # (min, max)
        
        self.voltage_set = 0.0
        self.current_set = 0.0
        self.output_enabled = False
        
        # Measured values (simulated with small variation)
        self.voltage_measured = 0.0
        self.current_measured = 0.0
    
    def set_voltage(self, value: float):
        """Set voltage (clamped to range)."""
        self.voltage_set = max(self.voltage_range[0], min(value, self.voltage_range[1]))
        if self.output_enabled:
            # Simulate small measurement variation
            self.voltage_measured = self.voltage_set + random.uniform(-0.01, 0.01)
    
    def set_current(self, value: float):
        """Set current (clamped to range)."""
        self.current_set = max(self.current_range[0], min(value, self.current_range[1]))
        if self.output_enabled:
            self.current_measured = self.current_set + random.uniform(-0.001, 0.001)
    
    def enable_output(self, enabled: bool):
        """Enable/disable output."""
        self.output_enabled = enabled
        if enabled:
            self.voltage_measured = self.voltage_set
            self.current_measured = self.current_set
        else:
            self.voltage_measured = 0.0
            self.current_measured = 0.0


class InstrumentSimulator:
    """Simulates a complete SCPI instrument."""
    
    def __init__(self, instrument_model: InstrumentModel):
        self.model = instrument_model
        self.channels: Dict[str, ChannelState] = {}
        self.selected_channel: Optional[str] = None
        self.error_queue: List[str] = []
        
        self._init_channels()
    
    def _init_channels(self):
        """Initialize instrument channels."""
        for ch in self.model.get_channels():
            v_range = (0.0, 100.0)  # default
            i_range = (0.0, 10.0)   # default
            
            if ch.voltage_output:
                v_range = (ch.voltage_output.get('min', 0.0), ch.voltage_output.get('max', 100.0))
            if ch.current_output:
                i_range = (ch.current_output.get('min', 0.0), ch.current_output.get('max', 10.0))
            
            self.channels[ch.channel_id] = ChannelState(ch.channel_id, v_range, i_range)
        
        # Select first channel as default
        if self.channels:
            self.selected_channel = list(self.channels.keys())[0]
    
    def get_channel(self, channel_id: Optional[str] = None) -> Optional[ChannelState]:
        """Returns a channel (uses selected if not specified)."""
        if channel_id is None:
            channel_id = self.selected_channel
        return self.channels.get(channel_id) if channel_id else None
    
    def process_command(self, raw_command: str, params: Optional[str] = None) -> str:
        """Processes a SCPI command and returns the response."""
        # Search for command in defined commands
        all_commands = self.model.get_all_commands()
        
        for cmd_name, cmd_template in all_commands.items():
            # Check if raw command matches the template
            response = self._match_and_execute(raw_command, params, cmd_name, cmd_template)
            if response is not None:
                return response
        
        # Debug: show available commands if not found
        return f"ERR: Unknown command '{raw_command}'"
    
    def _match_and_execute(self, raw_cmd: str, params: Optional[str], 
                          cmd_name: str, cmd_template: str) -> Optional[str]:
        """Verify match and execute the command."""
        # Normalize command and template
        cmd_upper = raw_cmd.upper().strip()
        template_upper = cmd_template.upper().strip()
        
        # Remove placeholders for base comparison
        template_base = re.sub(r'\{[^}]+\}', '', template_upper).strip()
        template_base = template_base.replace('  ', ' ')
        
        # Extract base part of command (without numbers/values)
        cmd_base = re.sub(r'[\d.]+', '', cmd_upper).strip()
        cmd_base = cmd_base.replace('  ', ' ')
        
        # Flexible matching - check if template base appears in command
        # Or if command contains template structure
        if template_base.replace(' ', '') not in cmd_base.replace(' ', ''):
            return None
        
        # Extract parameters from placeholders
        cmd_params = self._extract_params(raw_cmd, cmd_template, params)
        
        # Execute action based on command name
        return self._execute_action(cmd_name, cmd_params)
    
    def _extract_params(self, raw_cmd: str, template: str, extra_params: Optional[str]) -> Dict[str, str]:
        """Extracts parameters from template placeholders."""
        params = {}
        
        # Find placeholders in template
        placeholder_pattern = r'\{([^}]+)\}'
        placeholders = re.findall(placeholder_pattern, template)
        
        # Extract all numeric values from command
        numbers = re.findall(r'[\d.]+', raw_cmd)
        
        # Search for specific patterns
        # Channel number: CH1, CH2, OUT1, etc.
        ch_match = re.search(r'CH(\d+)|OUT(\d+)', raw_cmd, re.IGNORECASE)
        if ch_match:
            ch_num = ch_match.group(1) or ch_match.group(2)
            params['channel_number'] = ch_num
        
        # Value parameter (from extra params or numbers in command)
        if extra_params:
            val_match = re.search(r'([\d.]+)', extra_params)
            if val_match:
                params['value'] = val_match.group(1)
            params['extra'] = extra_params
        elif numbers:
            # If there's no channel_number, the first number is the value
            if 'channel_number' not in params and numbers:
                params['value'] = numbers[0]
        
        return params
    
    def _execute_action(self, cmd_name: str, params: Dict[str, str]) -> str:
        """Executes the command action and returns the response."""
        # Common IEEE 488.2 commands
        if cmd_name == 'identification_query':
            return f"{self.model.manufacturer},{self.model.model},SN001,1.0"
        
        if cmd_name == 'reset':
            for ch in self.channels.values():
                ch.set_voltage(0.0)
                ch.set_current(0.0)
                ch.enable_output(False)
            return ""
        
        if cmd_name == 'clear_status':
            self.error_queue.clear()
            return ""
        
        if cmd_name == 'error_query':
            if self.error_queue:
                return self.error_queue.pop(0)
            return "0,No error"
        
        # Channel management
        if cmd_name == 'select_channel':
            ch_num = params.get('channel_number', '1')
            ch_id = f"CH{ch_num}" if 'CH' not in str(ch_num) else str(ch_num)
            if ch_id in self.channels:
                self.selected_channel = ch_id
            return ""
        
        # Set commands
        if cmd_name == 'set_voltage':
            value = float(params.get('value', params.get('extra', '0.0')))
            ch = self.get_channel()
            if ch:
                ch.set_voltage(value)
            return ""
        
        if cmd_name == 'set_current':
            value = float(params.get('value', params.get('extra', '0.0')))
            ch = self.get_channel()
            if ch:
                ch.set_current(value)
            return ""
        
        # Query commands
        if cmd_name == 'read_voltage':
            ch_num = params.get('channel_number')
            if ch_num:
                ch_id = f"CH{ch_num}"
                ch = self.get_channel(ch_id)
            else:
                ch = self.get_channel()
            
            result = "0.0000"
            if ch and ch.output_enabled:
                result = f"{ch.voltage_measured:.4f}"
            elif ch:
                result = f"{ch.voltage_set:.4f}"
            return result
        
        if cmd_name == 'read_current':
            ch_num = params.get('channel_number')
            if ch_num:
                ch_id = f"CH{ch_num}"
                ch = self.get_channel(ch_id)
            else:
                ch = self.get_channel()
            
            result = "0.0000"
            if ch and ch.output_enabled:
                result = f"{ch.current_measured:.4f}"
            elif ch:
                result = f"{ch.current_set:.4f}"
            return result
        
        if cmd_name == 'read_power':
            ch = self.get_channel()
            if ch:
                power = ch.voltage_measured * ch.current_measured
                return f"{power:.4f}"
            return "0.0000"
        
        # Output control
        if cmd_name in ('output_on', 'output_on_channels'):
            ch = self.get_channel()
            if ch:
                ch.enable_output(True)
            return ""
        
        if cmd_name in ('output_off', 'output_off_channels'):
            ch = self.get_channel()
            if ch:
                ch.enable_output(False)
            return ""
        
        if cmd_name in ('output_state_query', 'output_state_query_channels'):
            ch = self.get_channel()
            if ch:
                return "1" if ch.output_enabled else "0"
            return "0"
        
        # Default: command recognized but not implemented
        return "OK"


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    # Test with Keysight E36312A
    lib = InstrumentLibrary()
    instrument = lib.get_instrument('PSU_Keysight_E36312A')
    
    if instrument:
        sim = InstrumentSimulator(instrument)
        print(f"\n=== Testing {instrument.name} ===\n")
        
        # Debug: show some loaded commands
        all_cmds = instrument.get_all_commands()
        print("Loaded commands (sample):")
        for cmd_name, cmd_template in list(all_cmds.items())[:10]:
            print(f"  {cmd_name:30s} -> {cmd_template}")
        print()
        
        # Test commands
        test_commands = [
            ('*IDN?', None),
            ('VOLT', '3.3'),
            ('CURR', '1.5'),
            ('OUTP', 'ON'),
            ('MEAS:VOLT?', 'CH1'),
            ('MEAS:CURR?', 'CH1'),
            ('MEAS:POW?', 'CH1'),
            ('OUTP?', None),
            ('SYST:ERR?', None),
        ]
        
        for cmd, params in test_commands:
            resp = sim.process_command(cmd, params)
            cmd_full = f"{cmd} {params}" if params else cmd
            print(f"{cmd_full:25s} -> {resp}")

