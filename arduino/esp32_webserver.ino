#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <SPIFFS.h>

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

// Servidor Web na porta 80
WebServer server(80);

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

void setup() {
  // Inicializa a comunicação serial
  Serial.begin(115200);
  Serial.println("\nSistema de Irrigação Inteligente com ESP32");
  Serial.println("----------------------------------------");
  
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
  
  // Inicializa o sistema de arquivos SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("Erro ao montar o sistema de arquivos SPIFFS");
    return;
  }
  
  // Conecta ao WiFi
  conectarWiFi();
  
  // Configura as rotas do servidor web
  configurarServidor();
  
  // Inicia o servidor web
  server.begin();
  Serial.println("Servidor HTTP iniciado");
  
  delay(2000); // Aguarda a estabilização dos sensores
}

void loop() {
  // Processa as requisições do cliente
  server.handleClient();
  
  // Verifica se é hora de fazer uma nova leitura
  unsigned long tempoAtual = millis();
  
  if (tempoAtual - ultimaLeitura >= INTERVALO_LEITURA) {
    ultimaLeitura = tempoAtual;
    
    // Leitura dos sensores
    lerSensores();
    
    // Exibe os valores no monitor serial
    exibirDados();
    
    // Toma decisões com base nos dados dos sensores (apenas se não estiver em modo manual)
    if (!modoManual) {
      tomarDecisoes();
    }
  }
}

void conectarWiFi() {
  Serial.print("Conectando ao WiFi");
  WiFi.begin(ssid, password);
  
  // Aguarda a conexão
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void configurarServidor() {
  // Rota para a página principal
  server.on("/", HTTP_GET, handleRoot);
  
  // Rota para obter os dados dos sensores em formato JSON
  server.on("/api/sensores", HTTP_GET, handleSensores);
  
  // Rota para controlar a irrigação
  server.on("/api/irrigacao", HTTP_POST, handleIrrigacao);
  
  // Rota para arquivos estáticos (CSS, JS)
  server.on("/styles.css", HTTP_GET, []() {
    serveFile("/styles.css", "text/css");
  });
  
  server.on("/script.js", HTTP_GET, []() {
    serveFile("/script.js", "application/javascript");
  });
  
  // Rota para lidar com requisições não encontradas
  server.onNotFound(handleNotFound);
}

void serveFile(const char* path, const char* contentType) {
  if (SPIFFS.exists(path)) {
    File file = SPIFFS.open(path, "r");
    server.streamFile(file, contentType);
    file.close();
  } else {
    server.send(404, "text/plain", "Arquivo não encontrado");
  }
}

void handleRoot() {
  if (SPIFFS.exists("/index.html")) {
    File file = SPIFFS.open("/index.html", "r");
    server.streamFile(file, "text/html");
    file.close();
  } else {
    // Se o arquivo não existir, envia uma página HTML básica
    String html = "<!DOCTYPE html><html><head>";
    html += "<meta charset='UTF-8'><title>Sistema de Irrigação</title>";
    html += "<style>body{font-family:Arial;margin:20px;text-align:center;}";
    html += "h1{color:#4CAF50;}table{margin:0 auto;border-collapse:collapse;}";
    html += "td,th{border:1px solid #ddd;padding:8px;text-align:left;}";
    html += "th{background-color:#4CAF50;color:white;}</style></head>";
    html += "<body><h1>Sistema de Irrigação Inteligente</h1>";
    html += "<p>Acesse os dados dos sensores via API: <a href='/api/sensores'>/api/sensores</a></p>";
    html += "<h2>Valores Atuais</h2>";
    html += "<table><tr><th>Sensor</th><th>Valor</th></tr>";
    html += "<tr><td>Umidade</td><td>" + String(umidadeSolo) + "%</td></tr>";
    html += "<tr><td>pH</td><td>" + String(phCalculado) + "</td></tr>";
    html += "<tr><td>Fósforo</td><td>" + String(nivelFosforo ? "Adequado" : "Baixo") + "</td></tr>";
    html += "<tr><td>Potássio</td><td>" + String(nivelPotassio ? "Adequado" : "Baixo") + "</td></tr>";
    html += "<tr><td>Irrigação</td><td>" + String(irrigacaoAtiva ? "Ativa" : "Desativada") + "</td></tr>";
    html += "<tr><td>Alerta</td><td>" + String(condicaoCritica ? "Sim" : "Não") + "</td></tr>";
    html += "</table></body></html>";
    server.send(200, "text/html", html);
  }
}

void handleSensores() {
  // Cria um objeto JSON para armazenar os dados
  StaticJsonDocument<256> doc;
  
  doc["umidade"] = umidadeSolo;
  doc["ph"] = phCalculado;
  doc["fosforo"] = nivelFosforo;
  doc["potassio"] = nivelPotassio;
  doc["irrigacaoAtiva"] = irrigacaoAtiva;
  doc["condicaoCritica"] = condicaoCritica;
  doc["modoManual"] = modoManual;
  
  // Converte o objeto JSON para uma string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Envia a resposta
  server.send(200, "application/json", jsonString);
}

void handleIrrigacao() {
  // Verifica se o parâmetro 'acao' foi fornecido
  if (!server.hasArg("acao")) {
    server.send(400, "text/plain", "Parâmetro 'acao' não fornecido");
    return;
  }
  
  String acao = server.arg("acao");
  
  if (acao == "ligar") {
    irrigacaoAtiva = true;
    modoManual = true;
    digitalWrite(PINO_RELE, HIGH);
    digitalWrite(PINO_LED_IRRIGACAO, HIGH);
    server.send(200, "text/plain", "Irrigação ativada manualmente");
  } 
  else if (acao == "desligar") {
    irrigacaoAtiva = false;
    modoManual = true;
    digitalWrite(PINO_RELE, LOW);
    digitalWrite(PINO_LED_IRRIGACAO, LOW);
    server.send(200, "text/plain", "Irrigação desativada manualmente");
  }
  else if (acao == "automatico") {
    modoManual = false;
    tomarDecisoes(); // Retorna ao modo automático e toma decisão imediatamente
    server.send(200, "text/plain", "Modo automático ativado");
  }
  else {
    server.send(400, "text/plain", "Ação inválida. Use 'ligar', 'desligar' ou 'automatico'");
  }
}

void handleNotFound() {
  server.send(404, "text/plain", "Página não encontrada");
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