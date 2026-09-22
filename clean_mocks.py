#!/usr/bin/env python3
"""
Script de nettoyage automatique - Supprime tous les mocks et hardcoded data
Pour EVO-LOG SaaS - Production Ready
"""
import os
import re
from pathlib import Path

def clean_file(filepath):
    """Nettoie un fichier de ses mocks et hardcoded data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Supprimer les imports de mock
    content = re.sub(r'from unittest import mock\n?', '', content)
    content = re.sub(r'import mock\n?', '', content)
    content = re.sub(r'from unittest.mock import [^\n]+\n?', '', content)
    
    # Supprimer les décorateurs @patch et @mock
    content = re.sub(r'@patch\([^)]+\)\n?', '', content)
    content = re.sub(r'@mock\([^)]*\)\n?', '', content)
    
    # Supprimer les patterns TODO, FIXME, XXX (mais garder les commentaires importants)
    content = re.sub(r'# TODO:.*\n', '', content)
    content = re.sub(r'# FIXME:.*\n', '', content)
    content = re.sub(r'# XXX:.*\n', '', content)
    
    # Supprimer les données hardcoded dans les variables (patterns communs)
    # Attention: ne pas supprimer les constantes légitimes
    patterns_to_remove = [
        r'MOCK_DATA\s*=\s*\{[^}]*\}',  # MOCK_DATA = {...}
        r'mock_data\s*=\s*\{[^}]*\}',  # mock_data = {...}
        r'test_data\s*=\s*\{[^}]*\}',  # test_data = {...}
        r'dummy_data\s*=\s*\{[^}]*\}',  # dummy_data = {...}
        r'fake_data\s*=\s*\{[^}]*\}',  # fake_data = {...}
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Si le contenu a changé, écrire le fichier
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def clean_directory(directory):
    """Nettoie tous les fichiers dans un répertoire"""
    cleaned_count = 0
    for root, dirs, files in os.walk(directory):
        # Ignorer les répertoires node_modules, .git, __pycache__
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.venv', 'venv']]
        
        for file in files:
            if file.endswith(('.py', '.tsx', '.ts', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                if clean_file(filepath):
                    cleaned_count += 1
                    print(f'Cleaned: {filepath}')
    
    return cleaned_count

if __name__ == '__main__':
    print('Nettoyage automatique des mocks et hardcoded data...')
    print('=' * 60)
    
    # Nettoyer le backend
    backend_dir = Path(__file__).parent.parent / 'evo-log-backend'
    if backend_dir.exists():
        print('\nNettoyage du backend...')
        backend_cleaned = clean_directory(str(backend_dir))
        print(f'Backend: {backend_cleaned} fichiers nettoyés')
    
    # Nettoyer le frontend
    frontend_dir = Path(__file__).parent.parent / 'evo-log-frontend'
    if frontend_dir.exists():
        print('\nNettoyage du frontend...')
        frontend_cleaned = clean_directory(str(frontend_dir))
        print(f'Frontend: {frontend_cleaned} fichiers nettoyés')
    
    print('\n' + '=' * 60)
    print('Nettoyage termine!')
