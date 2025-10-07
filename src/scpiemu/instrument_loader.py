"""Instrument library loader and management.

Carica il file instruments_lib.json e fornisce API per accedere
alle definizioni degli strumenti SCPI.
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Channel:
    """Rappresenta un canale di uno strumento."""
    channel_id: str
    label: str
    voltage_output: Optional[Dict[str, Any]] = None
    current_output: Optional[Dict[str, Any]] = None


@dataclass
class InstrumentModel:
    """Rappresenta un modello di strumento."""
    id: str
    name: str
    manufacturer: str
    model: str
    capabilities: Dict[str, Any]
    scpi_commands: Dict[str, str]
    common_scpi_commands: Dict[str, str]
    
    def get_all_commands(self) -> Dict[str, str]:
        """Unisce comandi comuni e specifici del modello."""
        commands = {}
        commands.update(self.common_scpi_commands)
        commands.update(self.scpi_commands)
        return commands
    
    def get_channels(self) -> List[Channel]:
        """Restituisce la lista dei canali dello strumento."""
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
    """Gestisce la libreria degli strumenti SCPI."""
    
    def __init__(self, library_path: Optional[str] = None):
        """Inizializza e carica la libreria."""
        if library_path is None:
            # Default: cerca instruments_lib.json nella root del progetto
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            library_path = os.path.join(root, 'instruments_lib.json')
        
        self.library_path = library_path
        self.data = {}
        self._load_library()
    
    def _load_library(self):
        """Carica il file JSON della libreria."""
        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load instrument library: {e}")
    
    def list_categories(self) -> List[str]:
        """Restituisce le categorie disponibili (power_supplies_series, oscilloscopes_series, ecc.)."""
        if 'instrument_library' not in self.data:
            return []
        return list(self.data['instrument_library'].keys())
    
    def list_series(self, category: str) -> List[Dict[str, str]]:
        """Restituisce le serie disponibili in una categoria."""
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
        """Restituisce i modelli disponibili in una categoria/serie."""
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
        """Restituisce un InstrumentModel dato il suo ID."""
        if 'instrument_library' not in self.data:
            return None
        
        # Cerca in tutte le categorie e serie
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
        """Restituisce tutti gli strumenti disponibili nella libreria."""
        instruments = []
        for category in self.list_categories():
            instruments.extend(self.list_models(category))
        return instruments


def print_instruments_menu():
    """Stampa un menu interattivo degli strumenti disponibili."""
    lib = InstrumentLibrary()
    
    print("\n=== SCPI Instrument Library ===\n")
    
    categories = lib.list_categories()
    for cat in categories:
        # Formatta il nome della categoria
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
    
    # Test: stampa menu strumenti
    print_instruments_menu()
