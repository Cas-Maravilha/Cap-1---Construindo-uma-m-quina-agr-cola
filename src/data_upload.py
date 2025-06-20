import os
import shutil
import argparse
import subprocess

def check_esptool():
    """Verifica se o esptool está instalado"""
    try:
        subprocess.run(['esptool.py', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def check_platformio():
    """Verifica se o PlatformIO está instalado"""
    try:
        subprocess.run(['pio', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def create_data_dir():
    """Cria a estrutura de diretórios para os arquivos de dados"""
    # Cria o diretório data se não existir
    data_dir = os.path.join('..', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"Diretório '{data_dir}' criado com sucesso.")
    else:
        print(f"Diretório '{data_dir}' já existe.")

def copy_web_files():
    """Copia os arquivos web para o diretório data"""
    web_files = [
        os.path.join('..', 'web', 'index.html'),
        os.path.join('..', 'web', 'styles.css'),
        os.path.join('..', 'web', 'script.js')
    ]
    
    dest_dir = os.path.join('..', 'data')

    for source_path in web_files:
        if os.path.exists(source_path):
            dest_file_path = os.path.join(dest_dir, os.path.basename(source_path))
            shutil.copy(source_path, dest_file_path)
            print(f"Arquivo '{os.path.basename(source_path)}' copiado para '{dest_dir}'.")
        else:
            print(f"ERRO: Arquivo '{source_path}' não encontrado.")

def upload_spiffs():
    """Faz o upload dos arquivos para o sistema de arquivos SPIFFS do ESP32"""
    if check_platformio():
        print("Usando PlatformIO para fazer o upload dos arquivos SPIFFS...")
        result = subprocess.run(['pio', 'run', '--target', 'uploadfs'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        if result.returncode == 0:
            print("Upload SPIFFS concluído com sucesso!")
        else:
            print("Erro ao fazer o upload SPIFFS:")
            print(result.stderr)
    else:
        print("PlatformIO não encontrado. Verifique se está instalado corretamente.")
        print("Você pode instalar o PlatformIO com: pip install platformio")

def main():
    parser = argparse.ArgumentParser(description='Ferramenta para preparar e fazer upload de arquivos web para o ESP32')
    parser.add_argument('--copy-only', action='store_true', help='Apenas copia os arquivos para o diretório data, sem fazer upload')
    
    args = parser.parse_args()
    
    print("=== Ferramenta de Upload de Arquivos Web para ESP32 ===")
    
    # Cria o diretório data
    create_data_dir()
    
    # Copia os arquivos web
    copy_web_files()
    
    # Faz o upload se não for apenas para copiar
    if not args.copy_only:
        upload_spiffs()
    
    print("Processo concluído!")

if __name__ == "__main__":
    main()