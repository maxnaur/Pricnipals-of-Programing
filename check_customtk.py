import sys, traceback
print('python:', sys.executable)
try:
    import customtkinter as ctk
    print('imported customtkinter, version', getattr(ctk, '__version__', 'unknown'))
    print('has CTkMessagebox?', hasattr(ctk, 'CTkMessagebox'))
except Exception as e:
    print('import error:', type(e).__name__, e)
    traceback.print_exc()

import importlib
print('importlib module file:', getattr(importlib, '__file__', 'built-in or namespace'))
print('importlib has util?', hasattr(importlib, 'util'))
if hasattr(importlib, 'util'):
    import importlib.util
    print('importlib.util OK')
