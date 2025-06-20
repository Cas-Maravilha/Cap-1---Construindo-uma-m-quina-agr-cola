#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// Definição dos pinos do ESP32
#define PINO_SENSOR_FOSFORO 2    // Botão para simular sensor de fósforo
#define PINO_SENSOR_POTASSIO 4   // Botão para simular sensor de potássio
#define PINO_SENSOR_PH 34        // LDR para simular sensor de pH (pino analógico)
#define PINO_DHT 15              // Sensor DHT22 para umidade
#define PINO_RELE 5              // Relé para controlar a bomba d'água
#define PINO_LED_IRRIGACAO 18    // LED que indica irrigação ativa
#define PINO_LED_ALERTA 19       // LED que indica condições críticas

// Configuração do sensor DHT
#define DHTTYPE DHT22
DHT dht(PINO_DHT, DHTTYPE);

// Configuração do WiFi
const char* ssid = "SuaRedeWiFi";      // Nome da sua rede WiFi
const char* password = "SuaSenhaWiFi";  // Senha da sua rede WiFi

// Configuração do MQTT
const char* mqtt_server = "broker.hivemq.com";  // Broker público gratuito
const int mqtt_port = 1883;
const char* mqtt_client_id = "esp32_irrigacao";
const char* mqtt_topic_sensores = "irrigacao/sensores";
const char* mqtt_topic_comandos = "irrigacao/comandos";
const char* mqtt_topic_status = "irrigacao/status";

// Objetos WiFi e MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Variáveis para armazenar os valores dos sensores
bool nivelFosforo = false;       // false = baixo, true = adequado
bool nivelPotassio = false;      // false = baixo, true = adequado
int valorPH = 0;                 // Valor bruto do LDR
float phCalculado = 0.0;         // pH calculado (0-14)
float umidadeSolo = 0.0;         // Umidade do solo (%)

// Limites para tomada de decisão
const float LIMITE_UMIDADE_BAIXA = 30.0;  // Abaixo disso, solo seco
const float LIMITE_UMIDADE_ALTA = 70.0;   // Acima disso, solo muito úmido
const float PH_IDEAL_MIN = 5.5;           // pH mínimo ideal
const float PH_IDEAL_MAX = 7.0;           // pH máximo ideal

// Estado do sistema
bool irrigacaoAtiva = false;
bool condicaoCritica = false;
bool modoManual = false;

// Intervalo de leitura dos sensores (em milissegundos)
const unsigned long INTERVALO_LEITURA = 5000;
unsigned long ultimaLeitura = 0;

// Intervalo de reconexão MQTT (em milissegundos)
const unsigned long INTERVALO_RECONEXAO = 5000;
unsigned long ultimaTentativaReconexao = 0;

void setup() {
  // Inicializa a comunicação serial
  Serial.begin(115200);
  Serial.println("\nSistema de Irrigação Inteligente com ESP32 e MQTT");
  Serial.println("------------------------------------------------");
  
  // Configura os pinos
  pinMode(PINO_SENSOR_FOSFORO, INPUT_PULLUP);  // Botão com resistor pull-up interno
  pinMode(PINO_SENSOR_POTASSIO, INPUT_PULLUP); // Botão com resistor pull-up interno
  pinMode(PINO_SENSOR_PH, INPUT);              // LDR como entrada analógica
  pinMode(PINO_RELE, OUTPUT);                  // Relé como saída
  pinMode(PINO_LED_IRRIGACAO, OUTPUT);         // LED como saída
  pinMode(PINO_LED_ALERTA, OUTPUT);            // LED como saída
  
  // Inicializa o relé e LEDs desligados
  digitalWrite(PINO_RELE, LOW);
  digitalWrite(PINO_LED_IRRIGACAO, LOW);
  digitalWrite(PINO_LED_ALERTA, LOW);
  
  // Inicializa o sensor DHT
  dht.begin();
  
  // Conecta ao WiFi
  setupWiFi();
  
  // Configura o servidor MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  delay(2000); // Aguarda a estabilização dos sensores
}

void loop() {
  // Verifica a conexão WiFi e MQTT
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  
  // Verifica se é hora de fazer uma nova leitura
  unsigned long tempoAtual = millis();
  
  if (tempoAtual - ultimaLeitura >= INTERVALO_LEITURA) {
    ultimaLeitura = tempoAtual;
    
    // Leitura dos sensores
    lerSensores();
    
    // Exibe os valores no monitor serial
    exibirDados();
    
    // Publica os dados dos sensores via MQTT
    publicarDadosSensores();
    
    // Toma decisões com base nos dados dos sensores (apenas se não estiver em modo manual)
    if (!modoManual) {
      tomarDecisoes();
    }
    
    // Publica o status do sistema via MQTT
    publicarStatusSistema();
  }
}

void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando à rede WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  unsigned long tempoAtual = millis();
  
  // Limita as tentativas de reconexão
  if (tempoAtual - ultimaTentativaReconexao < INTERVALO_RECONEXAO) {
    return;
  }
  
  ultimaTentativaReconexao = tempoAtual;
  
  Serial.print("Tentando conexão MQTT...");
  
  // Tenta conectar
  if (client.connect(mqtt_client_id)) {
    Serial.println("conectado");
    
    // Inscreve-se no tópico de comandos
    client.subscribe(mqtt_topic_comandos);
    
    // Publica uma mensagem de status inicial
    publicarStatusSistema();
  } else {
    Serial.print("falhou, rc=");
    Serial.print(client.state());
    Serial.println(" tentando novamente em 5 segundos");
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensagem recebida [");
  Serial.print(topic);
  Serial.print("]: ");
  
  // Converte o payload para uma string
  String mensagem;
  for (int i = 0; i < length; i++) {
    mensagem += (char)payload[i];
  }
  Serial.println(mensagem);
  
  // Processa a mensagem se for do tópico de comandos
  if (String(topic) == mqtt_topic_comandos) {
    processarComando(mensagem);
  }
}

void processarComando(String mensagem) {
  // Cria um objeto JSON para analisar a mensagem
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, mensagem);
  
  // Verifica se houve erro na análise do JSON
  if (error) {
    Serial.print("Erro ao analisar JSON: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Verifica se o comando contém a ação
  if (!doc.containsKey("acao")) {
    Serial.println("Comando sem campo 'acao'");
    return;
  }
  
  // Obtém a ação do comando
  String acao = doc["acao"];
  
  if (acao == "ligar_irrigacao") {
    Serial.println("Comando: Ligar irrigação manualmente");
    irrigacaoAtiva = true;
    modoManual = true;
    digitalWrite(PINO_RELE, HIGH);
    digitalWrite(PINO_LED_IRRIGACAO, HIGH);
  }
  else if (acao == "desligar_irrigacao") {
    Serial.println("Comando: Desligar irrigação manualmente");
    irrigacaoAtiva = false;
    modoManual = true;
    digitalWrite(PINO_RELE, LOW);
    digitalWrite(PINO_LED_IRRIGACAO, LOW);
  }
  else if (acao == "modo_automatico") {
    Serial.println("Comando: Ativar modo automático");
    modoManual = false;
    // Toma decisão imediatamente
    tomarDecisoes();
  }
  else {
    Serial.print("Ação desconhecida: ");
    Serial.println(acao);
  }
  
  // Publica o novo status do sistema
  publicarStatusSistema();
}

void lerSensores() {
  // Lê o sensor de fósforo (botão)
  nivelFosforo = !digitalRead(PINO_SENSOR_FOSFORO); // Invertido devido ao pull-up
  
  // Lê o sensor de potássio (botão)
  nivelPotassio = !digitalRead(PINO_SENSOR_POTASSIO); // Invertido devido ao pull-up
  
  // Lê o sensor de pH (LDR)
  valorPH = analogRead(PINO_SENSOR_PH);
  // Converte o valor do LDR para uma escala de pH (0-14)
  // ESP32 tem resolução de 12 bits (0-4095) em vez de 10 bits (0-1023) do Arduino
  phCalculado = map(valorPH, 0, 4095, 0, 140) / 10.0;
  
  // Lê o sensor de umidade (DHT22)
  umidadeSolo = dht.readHumidity();
  
  // Verifica se a leitura do DHT22 falhou
  if (isnan(umidadeSolo)) {
    Serial.println("Falha na leitura do sensor DHT!");
    umidadeSolo = 0.0;
  }
}

void exibirDados() {
  Serial.println("\n--- Leitura dos Sensores ---");
  
  // Exibe o status do fósforo
  Serial.print("Fósforo: ");
  Serial.println(nivelFosforo ? "Adequado" : "Baixo");
  
  // Exibe o status do potássio
  Serial.print("Potássio: ");
  Serial.println(nivelPotassio ? "Adequado" : "Baixo");
  
  // Exibe o valor do pH
  Serial.print("pH: ");
  Serial.println(phCalculado);
  
  // Exibe a umidade do solo
  Serial.print("Umidade do solo: ");
  Serial.print(umidadeSolo);
  Serial.println("%");
  
  // Exibe o modo de operação
  Serial.print("Modo: ");
  Serial.println(modoManual ? "Manual" : "Automático");
}

void tomarDecisoes() {
  bool necessitaIrrigacao = false;
  condicaoCritica = false;
  
  // Verifica se a umidade está baixa
  if (umidadeSolo < LIMITE_UMIDADE_BAIXA) {
    Serial.println("ALERTA: Umidade do solo baixa!");
    necessitaIrrigacao = true;
  }
  
  // Verifica se a umidade está muito alta
  if (umidadeSolo > LIMITE_UMIDADE_ALTA) {
    Serial.println("ALERTA: Umidade do solo muito alta!");
    condicaoCritica = true;
  }
  
  // Verifica se o pH está fora da faixa ideal
  if (phCalculado < PH_IDEAL_MIN || phCalculado > PH_IDEAL_MAX) {
    Serial.println("ALERTA: pH fora da faixa ideal!");
    condicaoCritica = true;
  }
  
  // Verifica se os níveis de nutrientes estão baixos
  if (!nivelFosforo) {
    Serial.println("ALERTA: Nível de fósforo baixo!");
    condicaoCritica = true;
  }
  
  if (!nivelPotassio) {
    Serial.println("ALERTA: Nível de potássio baixo!");
    condicaoCritica = true;
  }
  
  // Atualiza o estado da irrigação
  irrigacaoAtiva = necessitaIrrigacao && !condicaoCritica;
  
  // Controla o relé e os LEDs
  digitalWrite(PINO_RELE, irrigacaoAtiva ? HIGH : LOW);
  digitalWrite(PINO_LED_IRRIGACAO, irrigacaoAtiva ? HIGH : LOW);
  digitalWrite(PINO_LED_ALERTA, condicaoCritica ? HIGH : LOW);
  
  // Exibe o status da irrigação
  Serial.print("Status da irrigação: ");
  Serial.println(irrigacaoAtiva ? "ATIVA" : "DESATIVADA");
  Serial.print("Relé (bomba d'água): ");
  Serial.println(irrigacaoAtiva ? "LIGADO" : "DESLIGADO");
  
  if (condicaoCritica) {
    Serial.println("ATENÇÃO: Condições críticas detectadas! Verifique os sensores.");
  }
}

void publicarDadosSensores() {
  // Cria um objeto JSON para os dados dos sensores
  StaticJsonDocument<256> doc;
  
  doc["umidade"] = umidadeSolo;
  doc["ph"] = phCalculado;
  doc["fosforo"] = nivelFosforo;
  doc["potassio"] = nivelPotassio;
  doc["timestamp"] = millis(); // Em uma implementação real, usaríamos um timestamp real
  
  // Serializa o objeto JSON para uma string
  char buffer[256];
  size_t n = serializeJson(doc, buffer);
  
  // Publica a mensagem no tópico de sensores
  if (client.publish(mqtt_topic_sensores, buffer, n)) {
    Serial.println("Dados dos sensores publicados com sucesso");
  } else {
    Serial.println("Falha ao publicar dados dos sensores");
  }
}

void publicarStatusSistema() {
  // Cria um objeto JSON para o status do sistema
  StaticJsonDocument<256> doc;
  
  doc["irrigacao_ativa"] = irrigacaoAtiva;
  doc["condicao_critica"] = condicaoCritica;
  doc["modo_manual"] = modoManual;
  doc["ultima_atualizacao"] = millis(); // Em uma implementação real, usaríamos um timestamp real
  
  // Serializa o objeto JSON para uma string
  char buffer[256];
  size_t n = serializeJson(doc, buffer);
  
  // Publica a mensagem no tópico de status
  if (client.publish(mqtt_topic_status, buffer, n)) {
    Serial.println("Status do sistema publicado com sucesso");
  } else {
    Serial.println("Falha ao publicar status do sistema");
  }
}