import os
import re

# Rename tables in conteneur_cycle.py
files_to_fix = {
    'conteneur_cycle.py': {
        'empotage_depotage': 'empotage_depotage_cycle',
        'inspections_conteneur': 'inspections_conteneur_cycle'
    }
}

for filename, table_renames in files_to_fix.items():
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old_table, new_table in table_renames.items():
            content = content.replace(f'__tablename__ = "{old_table}"', f'__tablename__ = "{new_table}"')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'Fixed {filename}')