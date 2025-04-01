from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Crea i file __init__.py necessari per i comandi personalizzati'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        management_dir = os.path.join(base_dir, 'management')
        commands_dir = os.path.join(management_dir, 'commands')
        
        # Crea i file __init__.py
        open(os.path.join(management_dir, '__init__.py'), 'a').close()
        open(os.path.join(commands_dir, '__init__.py'), 'a').close()
        
        self.stdout.write(self.style.SUCCESS('File __init__.py creati con successo!'))
