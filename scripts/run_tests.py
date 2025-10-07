"""Semplice runner di test senza dipendenze esterne.
Esegue i test presenti in `tests/` che usano pytest-style asserts.
"""
import importlib.util
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from glob import glob

failed = 0

for path in glob(os.path.join(ROOT, 'tests', 'test_*.py')):
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"[OK] {name}")
    except Exception as e:
        failed += 1
        print(f"[FAIL] {name}")
        traceback.print_exc()

if failed:
    print(f"{failed} tests failed")
    sys.exit(1)
else:
    print("All tests passed")
