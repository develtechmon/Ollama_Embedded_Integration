#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

WebServer server(80);

#define LED_PIN 2
#define MOTOR_PIN 18

void handleCommand()
{
    String cmd = server.arg("cmd");

    if(cmd == "LED_ON")
        digitalWrite(LED_PIN,HIGH);

    if(cmd == "LED_OFF")
        digitalWrite(LED_PIN,LOW);

    if(cmd == "MOTOR_ON")
        digitalWrite(MOTOR_PIN,HIGH);

    if(cmd == "MOTOR_OFF")
        digitalWrite(MOTOR_PIN,LOW);

    server.send(200,"text/plain","OK");
}

void setup()
{
    pinMode(LED_PIN,OUTPUT);
    pinMode(MOTOR_PIN,OUTPUT);

    WiFi.begin(ssid,password);

    while(WiFi.status()!=WL_CONNECTED)
    {
        delay(500);
    }

    server.on("/command",handleCommand);
    server.begin();
}

void loop()
{
    server.handleClient();
}
