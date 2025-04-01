#!/usr/bin/env python
"""Script di gestione per il progetto Django."""
import os
import sys

def main():
    """Punto di ingresso per i comandi di gestione Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_explorer.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django non è installato. Attiva l'ambiente virtuale e installa le dipendenze."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
