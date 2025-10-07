"""Instrument library loader and management.

Loads the instruments_lib.json file and provides API to access
SCPI instrument definitions.
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Channel:
    """Represents an instrument channel."""
    channel_id: str
    label: str
    voltage_output: Optional[Dict[str, Any]] = None
    current_output: Optional[Dict[str, Any]] = None


@dataclass
class InstrumentModel:
    """Represents an instrument model."""
    id: str
    name: str
    manufacturer: str
    model: str
    capabilities: Dict[str, Any]
    scpi_commands: Dict[str, str]
    common_scpi_commands: Dict[str, str]
    
    def get_all_commands(self) -> Dict[str, str]:
        """Merges common and model-specific commands."""
        commands = {}
        commands.update(self.common_scpi_commands)
        commands.update(self.scpi_commands)
        return commands
    
    def get_channels(self) -> List[Channel]:
        """Returns the list of instrument channels."""
        channels = []
        if 'channels' in self.capabilities:
            for ch in self.capabilities['channels']:
                channels.append(Channel(
                    channel_id=ch.get('channel_id', ''),
                    label=ch.get('label', ''),
                    voltage_output=ch.get('voltage_output'),
                    current_output=ch.get('current_output')
                ))
        return channels


class InstrumentLibrary:
    """Manages the SCPI instrument library."""
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize and load the library."""
        if library_path is None:
            # Default: search for instruments_lib.json in project root
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            library_path = os.path.join(root, 'instruments_lib.json')
        
        self.library_path = library_path
        self.data = {}
        self._load_library()
    
    def _load_library(self):
        """Load the library JSON file."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load instrument library: {e}")
    
    def list_categories(self) -> List[str]:
        """Returns available categories (power_supplies_series, oscilloscopes_series, etc.)."""
        if 'instrument_library' not in self.data:
            return []
        return list(self.data['instrument_library'].keys())
    
    def list_series(self, category: str) -> List[Dict[str, str]]:
        """Returns available series in a category."""
        series_list = []
        if 'instrument_library' not in self.data:
            return series_list
        
        category_data = self.data['instrument_library'].get(category, [])
        for series in category_data:
            series_list.append({
                'series_id': series.get('series_id', ''),
                'series_name': series.get('series_name', '')
            })
        return series_list
    
    def list_models(self, category: str, series_id: Optional[str] = None) -> List[Dict[str, str]]:
        """Returns available models in a category/series."""
        models_list = []
        if 'instrument_library' not in self.data:
            return models_list
        
        category_data = self.data['instrument_library'].get(category, [])
        for series in category_data:
            if series_id and series.get('series_id') != series_id:
                continue
            
            for model in series.get('models', []):
                models_list.append({
                    'id': model.get('id', ''),
                    'name': model.get('name', ''),
                    'manufacturer': model.get('manufacturer', ''),
                    'model': model.get('model', ''),
                    'series_name': series.get('series_name', '')
                })
        return models_list
    
    def get_instrument(self, instrument_id: str) -> Optional[InstrumentModel]:
        """Returns an InstrumentModel given its ID."""
        if 'instrument_library' not in self.data:
            return None
        
        # Search in all categories and series
        for category_name, category_data in self.data['instrument_library'].items():
            for series in category_data:
                common_commands = series.get('common_scpi_commands', {})
                
                for model in series.get('models', []):
                    if model.get('id') == instrument_id:
                        return InstrumentModel(
                            id=model.get('id', ''),
                            name=model.get('name', ''),
                            manufacturer=model.get('manufacturer', ''),
                            model=model.get('model', ''),
                            capabilities=model.get('capabilities', {}),
                            scpi_commands=model.get('scpi_commands', {}),
                            common_scpi_commands=common_commands
                        )
        return None
    
    def list_all_instruments(self) -> List[Dict[str, str]]:
        """Returns all available instruments in the library."""
        instruments = []
        for category in self.list_categories():
            instruments.extend(self.list_models(category))
        return instruments


def print_instruments_menu():
    """Prints an interactive menu of available instruments."""
    lib = InstrumentLibrary()
    
    print("\n=== SCPI Instrument Library ===\n")
    
    categories = lib.list_categories()
    for cat in categories:
        # Format category name
        cat_name = cat.replace('_', ' ').title()
        print(f"\n📁 {cat_name}")
        
        models = lib.list_models(cat)
        for i, model in enumerate(models, 1):
            print(f"  {i}. [{model['id']}] {model['name']}")
            print(f"     Manufacturer: {model['manufacturer']}")
            print(f"     Series: {model['series_name']}")
    
    print("\n" + "="*40)


if __name__ == '__main__':
    import sys
    # Add src to path for standalone execution
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    # Test: print instruments menu
    print_instruments_menu()
