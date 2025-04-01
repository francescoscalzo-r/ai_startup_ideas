import os
import json
import random
from django.core.management.base import BaseCommand
from ideas.models import Idea, Quadrante, Settore, TecnologiaAI, User

import html

def clean_encoding(text):
    """Rimuove caratteri errati causati da encoding sbagliato."""
    if not isinstance(text, str):
        return text
    return (text
        .replace('â€“', '–')
        .replace('â€”', '—')
        .replace('â€˜', '‘')
        .replace('â€™', '’')
        .replace('â€œ', '“')
        .replace('â€', '”')
        .replace('Ã¨', 'è')
        .replace('Ã©', 'é')
        .replace('Ã', 'à')
        .replace('Â', '')
        .replace('Ê', 'É')
        .replace('ç', 'ç')
        .replace('€', '€')
        .replace('\u2019', "’")
        .strip()
    )

class Command(BaseCommand):
    help = 'Importa le idee dai file di analisi'

    def handle(self, *args, **options):
        self.stdout.write('Importazione delle idee in corso...')

        # Cancella tutte le idee precedenti
        Idea.objects.all().delete()

        # Crea i quadranti se non esistono
        quadranti = {
            'automazione_pratico': Quadrante.objects.get_or_create(asse_x='automazione', asse_y='pratico', defaults={'nome': 'Automazione / Pratico'})[0],
            'creazione_pratico': Quadrante.objects.get_or_create(asse_x='creazione', asse_y='pratico', defaults={'nome': 'Creazione / Pratico'})[0],
            'creazione_sperimentale': Quadrante.objects.get_or_create(asse_x='creazione', asse_y='sperimentale', defaults={'nome': 'Creazione / Sperimentale'})[0],
            'automazione_sperimentale': Quadrante.objects.get_or_create(asse_x='automazione', asse_y='sperimentale', defaults={'nome': 'Automazione / Sperimentale'})[0]
        }

        # Trova un superuser (non assume che si chiami "admin")
        admin_user = User.objects.filter(is_superuser=True).first()

        base_dir = '/analysis'

        file_map = {
            'automazione_pratico': os.path.join(base_dir, 'quadrante1_automazione_pratico.md'),
            'creazione_pratico': os.path.join(base_dir, 'quadrante2_creazione_pratico.md'),
            'creazione_sperimentale': os.path.join(base_dir, 'quadrante3_creazione_sperimentale.md'),
            'automazione_sperimentale': os.path.join(base_dir, 'quadrante4_automazione_sperimentale.md'),
            'nuove_idee': os.path.join(base_dir, 'nuove_idee_complementari.md')
        }

        total_ideas = 0

        def parse_idea(text, quadrante_key, is_originale=True):
            lines = text.strip().split('\n')
            nome = clean_encoding(lines[0].replace('## ', '').strip())

            idea_data = {
                'nome': nome,
                'descrizione': '',
                'problema_risolto': '',
                'target': '',
                'unique_value_proposition': '',
                'modello_revenue': '',
                'tempo_mvp': '',
                'fattibilita_tecnica': 3,
                'potenziale_monetizzazione': 3,
                'competitivita_mercato': 3,
                'impatto_utente': 3,
                'settori': [],
                'tecnologie': []
            }

            current_field = None
            for line in lines[1:]:
                line = clean_encoding(line.strip())
                if not line:
                    continue

                if line.startswith('- **Nome e descrizione sintetica**:'):
                    current_field = 'descrizione'
                    idea_data[current_field] = clean_encoding(line.split(':', 1)[1].strip())
                elif line.startswith('- **Problema specifico che risolve**:'):
                    current_field = 'problema_risolto'
                    idea_data[current_field] = clean_encoding(line.split(':', 1)[1].strip())
                elif line.startswith('- **Target**:'):
                    target_text = clean_encoding(line.split(':', 1)[1].strip())
                    if 'B2B/B2C' in target_text:
                        idea_data['target'] = 'B2B/B2C'
                    elif 'B2B' in target_text:
                        idea_data['target'] = 'B2B'
                    elif 'B2C' in target_text:
                        idea_data['target'] = 'B2C'
                elif line.startswith('- **Unique Value Proposition**:'):
                    current_field = 'unique_value_proposition'
                    idea_data[current_field] = clean_encoding(line.split(':', 1)[1].strip())
                elif line.startswith('- **Settore/nicchia di riferimento**:'):
                    settori_text = clean_encoding(line.split(':', 1)[1].strip())
                    settori_list = [clean_encoding(s.strip()) for s in settori_text.split(',')]
                    idea_data['settori'] = settori_list
                elif line.startswith('- **Tecnologie AI coinvolte**:'):
                    tech_text = clean_encoding(line.split(':', 1)[1].strip())
                    tech_list = [clean_encoding(t.strip()) for t in tech_text.split(',')]
                    idea_data['tecnologie'] = tech_list
                elif line.startswith('- **Modello di revenue**:'):
                    current_field = 'modello_revenue'
                    idea_data[current_field] = clean_encoding(line.split(':', 1)[1].strip())
                elif line.startswith('- **Tempo stimato per realizzare un MVP**:'):
                    idea_data['tempo_mvp'] = clean_encoding(line.split(':', 1)[1].strip())
                elif line.startswith('  - Fattibilità tecnica:'):
                    idea_data['fattibilita_tecnica'] = int(line.split(':', 1)[1].strip().split('/')[0])
                elif line.startswith('  - Potenziale di monetizzazione:'):
                    idea_data['potenziale_monetizzazione'] = int(line.split(':', 1)[1].strip().split('/')[0])
                elif line.startswith('  - Competitività del mercato:'):
                    idea_data['competitivita_mercato'] = int(line.split(':', 1)[1].strip().split('/')[0])
                elif line.startswith('  - Impatto per l\'utente finale:'):
                    idea_data['impatto_utente'] = int(line.split(':', 1)[1].strip().split('/')[0])
                elif current_field and not line.startswith('- **'):
                    idea_data[current_field] += ' ' + clean_encoding(line)

            idea = Idea(
                nome=idea_data['nome'],
                descrizione=idea_data['descrizione'],
                problema_risolto=idea_data['problema_risolto'],
                target=idea_data['target'],
                unique_value_proposition=idea_data['unique_value_proposition'],
                modello_revenue=idea_data['modello_revenue'],
                tempo_mvp=idea_data['tempo_mvp'],
                fattibilita_tecnica=idea_data['fattibilita_tecnica'],
                potenziale_monetizzazione=idea_data['potenziale_monetizzazione'],
                competitivita_mercato=idea_data['competitivita_mercato'],
                impatto_utente=idea_data['impatto_utente'],
                quadrante=quadranti[quadrante_key],
                creatore=admin_user,
                is_originale=is_originale
            )
            idea.save()

            for settore_nome in idea_data['settori']:
                settore, _ = Settore.objects.get_or_create(nome=settore_nome)
                idea.settori.add(settore)

            for tech_nome in idea_data['tecnologie']:
                tech, _ = TecnologiaAI.objects.get_or_create(nome=tech_nome)
                idea.tecnologie.add(tech)

            return idea

        for quadrante_key, file_path in file_map.items():
            if not os.path.exists(file_path):
                self.stdout.write(f'File non trovato: {file_path}')
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if quadrante_key == 'nuove_idee':
                sections = content.split('## Quadrante:')
                for section in sections[1:]:
                    quadrante_text = section.split('\n', 1)[0].strip()
                    ideas_text = section.split('\n', 1)[1].strip()

                    if 'Automazione e Orchestrazione / Pratico' in quadrante_text:
                        current_quadrante = 'automazione_pratico'
                    elif 'Creazione e Interazione / Pratico' in quadrante_text:
                        current_quadrante = 'creazione_pratico'
                    elif 'Creazione e Interazione / Sperimentale' in quadrante_text:
                        current_quadrante = 'creazione_sperimentale'
                    elif 'Automazione e Orchestrazione / Sperimentale' in quadrante_text:
                        current_quadrante = 'automazione_sperimentale'
                    else:
                        self.stdout.write(f'Quadrante non riconosciuto: {quadrante_text}')
                        continue

                    idea_blocks = ideas_text.split('\n### ')
                    for i, block in enumerate(idea_blocks):
                        if i == 0 and not block.startswith('###'):
                            continue
                        if i > 0:
                            block = '### ' + block
                        try:
                            idea = parse_idea(block, current_quadrante, is_originale=False)
                            total_ideas += 1
                            self.stdout.write(f'Importata idea: {idea.nome}')
                        except Exception as e:
                            self.stdout.write(f'Errore nell\'importazione dell\'idea: {e}')
            else:
                idea_blocks = content.split('\n## ')
                for i, block in enumerate(idea_blocks):
                    if i == 0 and not block.startswith('##'):
                        continue
                    if i > 0:
                        block = '## ' + block
                    try:
                        idea = parse_idea(block, quadrante_key)
                        total_ideas += 1
                        self.stdout.write(f'Importata idea: {idea.nome}')
                    except Exception as e:
                        self.stdout.write(f'Errore nell\'importazione dell\'idea: {e}')

        self.stdout.write(self.style.SUCCESS(f'Importazione completata! {total_ideas} idee importate.'))
