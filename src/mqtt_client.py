import paho.mqtt.client as mqtt
import json
import time
import random
import argparse
from datetime import datetime

# Configurações MQTT
MQTT_BROKER = "broker.hivemq.com"  # Broker público gratuito
MQTT_PORT = 1883
MQTT_TOPIC_SENSORES = "irrigacao/sensores"
MQTT_TOPIC_COMANDOS = "irrigacao/comandos"
MQTT_TOPIC_STATUS = "irrigacao/status"
MQTT_CLIENT_ID = f"irrigacao_client_{random.randint(0, 1000)}"

# Limites para tomada de decisão
LIMITE_UMIDADE_BAIXA = 30.0
LIMITE_UMIDADE_ALTA = 70.0
PH_IDEAL_MIN = 5.5
PH_IDEAL_MAX = 7.0

# Variáveis globais
dados_sensores = {
    "umidade": 50.0,
    "ph": 6.5,
    "fosforo": True,
    "potassio": True,
    "timestamp": ""
}

status_sistema = {
    "irrigacao_ativa": False,
    "condicao_critica": False,
    "modo_manual": False,
    "ultima_atualizacao": ""
}

# Callbacks MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT com código: {rc}")
    # Inscreve-se no tópico de comandos
    client.subscribe(MQTT_TOPIC_COMANDOS)
    print(f"Inscrito no tópico: {MQTT_TOPIC_COMANDOS}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Mensagem recebida no tópico {msg.topic}: {payload}")
        
        if msg.topic == MQTT_TOPIC_COMANDOS:
            processar_comando(client, payload)
    except json.JSONDecodeError:
        print(f"Erro ao decodificar mensagem JSON: {msg.payload}")
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

def processar_comando(client, comando):
    global status_sistema
    
    if "acao" in comando:
        if comando["acao"] == "ligar_irrigacao":
            status_sistema["irrigacao_ativa"] = True
            status_sistema["modo_manual"] = True
            print("Comando: Irrigação LIGADA manualmente")
        
        elif comando["acao"] == "desligar_irrigacao":
            status_sistema["irrigacao_ativa"] = False
            status_sistema["modo_manual"] = True
            print("Comando: Irrigação DESLIGADA manualmente")
        
        elif comando["acao"] == "modo_automatico":
            status_sistema["modo_manual"] = False
            print("Comando: Modo automático ativado")
            # Recalcula o status com base nos sensores
            avaliar_condicoes()
        
        # Atualiza o timestamp
        status_sistema["ultima_atualizacao"] = datetime.now().isoformat()
        
        # Publica o novo status
        publicar_status(client)

def avaliar_condicoes():
    global dados_sensores, status_sistema
    
    # Verifica condições críticas
    condicao_critica = False
    necessita_irrigacao = False
    
    # Verifica se a umidade está baixa
    if dados_sensores["umidade"] < LIMITE_UMIDADE_BAIXA:
        necessita_irrigacao = True
    
    # Verifica condições críticas
    if dados_sensores["umidade"] > LIMITE_UMIDADE_ALTA:
        condicao_critica = True
    
    if dados_sensores["ph"] < PH_IDEAL_MIN or dados_sensores["ph"] > PH_IDEAL_MAX:
        condicao_critica = True
    
    if not dados_sensores["fosforo"] or not dados_sensores["potassio"]:
        condicao_critica = True
    
    # Atualiza o status do sistema
    status_sistema["condicao_critica"] = condicao_critica
    
    # Só ativa a irrigação se não estiver em modo manual
    if not status_sistema["modo_manual"]:
        status_sistema["irrigacao_ativa"] = necessita_irrigacao and not condicao_critica

def simular_leitura_sensores():
    global dados_sensores
    
    # Gera valores aleatórios para simular os sensores
    dados_sensores["umidade"] = round(random.uniform(20.0, 80.0), 1)
    dados_sensores["ph"] = round(random.uniform(4.0, 8.0), 1)
    dados_sensores["fosforo"] = random.random() > 0.3  # 70% de chance de estar adequado
    dados_sensores["potassio"] = random.random() > 0.3  # 70% de chance de estar adequado
    dados_sensores["timestamp"] = datetime.now().isoformat()
    
    print("\n--- Leitura dos Sensores ---")
    print(f"Umidade: {dados_sensores['umidade']}%")
    print(f"pH: {dados_sensores['ph']}")
    print(f"Fósforo: {'Adequado' if dados_sensores['fosforo'] else 'Baixo'}")
    print(f"Potássio: {'Adequado' if dados_sensores['potassio'] else 'Baixo'}")

def publicar_sensores(client):
    # Publica os dados dos sensores no tópico MQTT
    payload = json.dumps(dados_sensores)
    client.publish(MQTT_TOPIC_SENSORES, payload)
    print(f"Dados dos sensores publicados em {MQTT_TOPIC_SENSORES}")

def publicar_status(client):
    # Publica o status do sistema no tópico MQTT
    payload = json.dumps(status_sistema)
    client.publish(MQTT_TOPIC_STATUS, payload)
    print(f"Status do sistema publicado em {MQTT_TOPIC_STATUS}")

def main():
    parser = argparse.ArgumentParser(description='Cliente MQTT para o Sistema de Irrigação Inteligente')
    parser.add_argument('--broker', default=MQTT_BROKER, help='Endereço do broker MQTT')
    parser.add_argument('--port', type=int, default=MQTT_PORT, help='Porta do broker MQTT')
    parser.add_argument('--intervalo', type=int, default=10, help='Intervalo entre leituras (segundos)')
    
    args = parser.parse_args()
    
    # Configura o cliente MQTT
    client = mqtt.Client(MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Conecta ao broker MQTT
        print(f"Conectando ao broker MQTT em {args.broker}:{args.port}...")
        client.connect(args.broker, args.port, 60)
        
        # Inicia o loop MQTT em uma thread separada
        client.loop_start()
        
        print(f"Cliente MQTT iniciado. Pressione Ctrl+C para encerrar.")
        print(f"Intervalo entre leituras: {args.intervalo} segundos")
        
        # Loop principal
        while True:
            # Simula a leitura dos sensores
            simular_leitura_sensores()
            
            # Avalia as condições e toma decisões (se não estiver em modo manual)
            avaliar_condicoes()
            
            # Publica os dados dos sensores
            publicar_sensores(client)
            
            # Publica o status do sistema
            status_sistema["ultima_atualizacao"] = datetime.now().isoformat()
            publicar_status(client)
            
            # Exibe o status atual
            print("\n--- Status do Sistema ---")
            print(f"Irrigação: {'ATIVA' if status_sistema['irrigacao_ativa'] else 'DESATIVADA'}")
            print(f"Condição Crítica: {'SIM' if status_sistema['condicao_critica'] else 'NÃO'}")
            print(f"Modo: {'MANUAL' if status_sistema['modo_manual'] else 'AUTOMÁTICO'}")
            
            # Aguarda o próximo ciclo
            time.sleep(args.intervalo)
            
    except KeyboardInterrupt:
        print("\nEncerrando o cliente MQTT...")
    finally:
        # Encerra a conexão MQTT
        client.loop_stop()
        client.disconnect()
        print("Cliente MQTT encerrado.")

if __name__ == "__main__":
    main()