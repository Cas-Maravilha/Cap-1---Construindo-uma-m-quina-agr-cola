import os
import shutil
import sys

# Arquivos de origem
source_files = [
    'db_manager_expandido.py',
    'db_manager_expandido_part2.py',
    'db_manager_expandido_part3.py',
    'db_manager_expandido_part4.py',
    'db_manager_expandido_part5.py',
    'db_manager_expandido_part6.py',
    'db_manager_expandido_part7.py'
]

# Arquivo de destino
target_file = 'db_manager_expandido_completo.py'

# Verifica se os arquivos de origem existem
missing_files = [f for f in source_files if not os.path.exists(f)]
if missing_files:
    print(f"Erro: Os seguintes arquivos não foram encontrados: {', '.join(missing_files)}")
    sys.exit(1)

# Combina os arquivos
with open(target_file, 'w', encoding='utf-8') as outfile:
    # Processa o primeiro arquivo completamente
    with open(source_files[0], 'r', encoding='utf-8') as infile:
        outfile.write(infile.read())
    
    # Para os arquivos restantes, pega apenas o conteúdo (sem a definição da classe)
    for file_name in source_files[1:]:
        with open(file_name, 'r', encoding='utf-8') as infile:
            content = infile.read()
            outfile.write('\n')
            outfile.write(content)

print(f"Arquivos combinados com sucesso em {target_file}")