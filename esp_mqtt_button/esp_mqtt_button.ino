#include "PubSubClient.h" // Connect and publish to the MQTT broker
#include "ESP8266WiFi.h"  // Enables the ESP8266 to connect to the local network (via WiFi)

// WiFi
#include "arduino_secrets.h"
//const char* ssid = "";
//const char* pass = "";


// MQTT
const char* MQTT_SERVER = "192.168.0.183";  // IP of the MQTT broker (raspberry pi)
const char* MQTT_TOPIC = "home/bathroom_button";

// Button
const int PUSH_BUTTON_PIN = 15;
const int BUILTIN_LED_OVERRIDE = 2;
int buttonState = 0;

WiFiClient espClient;
PubSubClient client(espClient);

// ----------------------------------------------------------
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.println("Connecting to " + String(ssid));

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.print("WiFi connected. IP address: ");
  Serial.println(WiFi.localIP());
}
// ----------------------------------------------------------
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
// ----------------------------------------------------------
void setup() {
  Serial.begin(9600);
  pinMode(PUSH_BUTTON_PIN, INPUT);
  setup_wifi();
  client.setServer(MQTT_SERVER, 1883);

  // switch off built-in blue LED
  pinMode(BUILTIN_LED_OVERRIDE, OUTPUT);
  digitalWrite(BUILTIN_LED_OVERRIDE, HIGH);

}

void loop() {
  buttonState = digitalRead(PUSH_BUTTON_PIN);
//  Serial.println("buttonState: " + String(buttonState));

  if (buttonState > 0) {
    // reconnect to MQTT if needed.
    if (!client.connected()) {reconnect();}
    client.loop();

    // publish message
    client.publish(MQTT_TOPIC, "pressed");
    digitalWrite(BUILTIN_LED_OVERRIDE, LOW);
    delay(1000);
    digitalWrite(BUILTIN_LED_OVERRIDE, HIGH);
  }
  delay(100);
}
