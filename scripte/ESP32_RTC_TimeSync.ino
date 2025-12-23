/*
 * ESP32 RTC Time Sync mit optionalem OLED Display
 * 
 * Verbindet sich mit WLAN, holt die aktuelle Zeit via NTP
 * und programmiert einen TinyRTC (DS1307) über I2C
 * Zeigt Status auf 0,96" OLED Display an (optional)
 * 
 * Verbindungen (beide am selben I2C Bus):
 * TinyRTC SDA -> ESP32 GPIO21 (SDA)
 * TinyRTC SCL -> ESP32 GPIO22 (SCL)
 * TinyRTC VCC -> 5V
 * TinyRTC GND -> GND
 * 
 * OLED SDA -> ESP32 GPIO21 (SDA)
 * OLED SCL -> ESP32 GPIO22 (SCL)
 * OLED VCC -> 3.3V
 * OLED GND -> GND
 */

#include <WiFi.h>
#include <Wire.h>
#include <RTClib.h>
#include <time.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// WLAN Zugangsdaten
const char* ssid = "iPhone 15pro Max Robert";
const char* password = "somerandompassword";

// NTP Server Einstellungen
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600;        // GMT+1 für Deutschland (Winter)
const int daylightOffset_sec = 3600;    // +1 Stunde für Sommerzeit

// OLED Display Einstellungen
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

// RTC Objekt
RTC_DS1307 rtc;

// OLED Display Objekt
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Variable um zu prüfen ob Display verfügbar ist
bool displayAvailable = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\nESP32 RTC Time Sync");
  Serial.println("====================\n");
  
  // I2C initialisieren
  Wire.begin();
  
  // OLED Display initialisieren (optional)
  if(display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    displayAvailable = true;
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("ESP32 RTC Sync");
    display.println("==============");
    display.display();
    delay(1000);
    Serial.println("OLED Display bereit");
  } else {
    Serial.println("OLED Display nicht gefunden - läuft ohne Display");
  }
  
  // RTC initialisieren
  if (!rtc.begin()) {
    Serial.println("RTC nicht gefunden! Bitte Verkabelung prüfen.");
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("FEHLER:");
      display.println("RTC nicht");
      display.println("gefunden!");
      display.display();
    }
    while (1) delay(1000);
  }
  
  Serial.println("RTC gefunden");
  if (displayAvailable) {
    display.println("\nRTC: OK");
    display.display();
    delay(500);
  }
  
  // Mit WLAN verbinden
  Serial.print("Verbinde mit WLAN: ");
  Serial.println(ssid);
  
  if (displayAvailable) {
    display.println("\nWLAN...");
    display.display();
  }
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int wifiTimeout = 0;
  while (WiFi.status() != WL_CONNECTED && wifiTimeout < 20) {
    delay(500);
    Serial.print(".");
    wifiTimeout++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nWLAN Verbindung fehlgeschlagen!");
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("FEHLER:");
      display.println("WLAN Verbindung");
      display.println("fehlgeschlagen!");
      display.display();
    }
    return;
  }
  
  Serial.println("\nWLAN verbunden!");
  Serial.print("IP Adresse: ");
  Serial.println(WiFi.localIP());
  
  if (displayAvailable) {
    display.println("WLAN: OK");
    display.display();
    delay(500);
  }
  
  // NTP Zeit holen
  Serial.println("\nHole Zeit vom NTP Server...");
  if (displayAvailable) {
    display.println("NTP Sync...");
    display.display();
  }
  
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Zeit konnte nicht abgerufen werden!");
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("FEHLER:");
      display.println("NTP Sync");
      display.println("fehlgeschlagen!");
      display.display();
    }
    return;
  }
  
  // Zeit auf Serial ausgeben
  Serial.println("\nAktuelle Zeit vom NTP Server:");
  Serial.println(&timeinfo, "%A, %d.%m.%Y %H:%M:%S");
  
  if (displayAvailable) {
    display.println("NTP: OK");
    display.display();
    delay(500);
  }
  
  // RTC mit aktueller Zeit programmieren
  DateTime now(timeinfo.tm_year + 1900, 
               timeinfo.tm_mon + 1, 
               timeinfo.tm_mday,
               timeinfo.tm_hour, 
               timeinfo.tm_min, 
               timeinfo.tm_sec);
  
  rtc.adjust(now);
  Serial.println("\nRTC wurde mit aktueller Zeit programmiert!");
  
  if (displayAvailable) {
    display.println("RTC Sync: OK");
    display.println("\nFertig!");
    display.display();
    delay(2000);
  }
  
  // WiFi trennen um Strom zu sparen
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  Serial.println("WLAN getrennt");
  
  Serial.println("\n=== Synchronisation abgeschlossen ===\n");
}

void loop() {
  // Zeit vom RTC auslesen und anzeigen
  DateTime now = rtc.now();
  
  Serial.print("RTC Zeit: ");
  Serial.print(now.day(), DEC);
  Serial.print('.');
  Serial.print(now.month(), DEC);
  Serial.print('.');
  Serial.print(now.year(), DEC);
  Serial.print(" ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  if (now.minute() < 10) Serial.print('0');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  if (now.second() < 10) Serial.print('0');
  Serial.println(now.second(), DEC);
  
  // Zeit auf OLED anzeigen (wenn verfügbar)
  if (displayAvailable) {
    display.clearDisplay();
    
    // Datum
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("Datum: ");
    if (now.day() < 10) display.print('0');
    display.print(now.day(), DEC);
    display.print('.');
    if (now.month() < 10) display.print('0');
    display.print(now.month(), DEC);
    display.print('.');
    display.println(now.year(), DEC);
    
    // Uhrzeit (groß)
    display.setTextSize(2);
    display.setCursor(10, 20);
    if (now.hour() < 10) display.print('0');
    display.print(now.hour(), DEC);
    display.print(':');
    if (now.minute() < 10) display.print('0');
    display.print(now.minute(), DEC);
    display.print(':');
    if (now.second() < 10) display.print('0');
    display.println(now.second(), DEC);
    
    // Temperatur (falls verfügbar)
    display.setTextSize(1);
    display.setCursor(0, 50);
    display.print("Temp: ");
    display.print(rtc.getTemperature());
    display.println(" C");
    
    display.display();
  }
  
  delay(1000);
}
