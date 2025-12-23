/*
 * ESP32 RTC Time Sync mit optionalem OLED Display und RGB LED
 * 
 * Verbindet sich mit WLAN, holt die aktuelle Zeit via NTP
 * und programmiert einen TinyRTC (DS1307) über I2C
 * Zeigt Status auf 0,96" OLED Display (optional) und RGB LED (optional)
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
#include <Adafruit_NeoPixel.h>

// RGB LED Einstellungen (ESP32-S3-WROOM-1)
#define RGB_LED_PIN 48
#define RGB_LED_COUNT 1

// WLAN Zugangsdaten
const char* ssid = "WLAN SSID";
const char* password = "somerandompassword";

// NTP Server Einstellungen
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;           // UTC Zeit (keine Anpassung)
const int daylightOffset_sec = 0;       // Keine Sommerzeit

// OLED Display Einstellungen
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

// RTC Objekt
RTC_DS1307 rtc;

// OLED Display Objekt
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// RGB LED Objekt
Adafruit_NeoPixel rgbLed(RGB_LED_COUNT, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);

// Variable um zu prüfen ob Display verfügbar ist
bool displayAvailable = false;
bool rgbLedAvailable = false;
bool syncSuccess = false;
String errorMessage = "";

// RGB LED Funktionen
void setLED(uint8_t r, uint8_t g, uint8_t b) {
  if (rgbLedAvailable) {
    rgbLed.setPixelColor(0, rgbLed.Color(r, g, b));
    rgbLed.show();
  }
}

void pulseLED(uint8_t r, uint8_t g, uint8_t b, int duration) {
  if (!rgbLedAvailable) return;
  
  for (int i = 0; i < 3; i++) {
    for (int brightness = 0; brightness <= 255; brightness += 5) {
      rgbLed.setPixelColor(0, rgbLed.Color(
        (r * brightness) / 255,
        (g * brightness) / 255,
        (b * brightness) / 255
      ));
      rgbLed.show();
      delay(5);
    }
    for (int brightness = 255; brightness >= 0; brightness -= 5) {
      rgbLed.setPixelColor(0, rgbLed.Color(
        (r * brightness) / 255,
        (g * brightness) / 255,
        (b * brightness) / 255
      ));
      rgbLed.show();
      delay(5);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\nBreMesh RePeter RTC time Sync");
  Serial.println("====================\n");
  
  // RGB LED initialisieren (optional)
  rgbLed.begin();
  rgbLed.setBrightness(25); // 10% Helligkeit
  rgbLedAvailable = true;
  Serial.println("RGB LED bereit");
  
  // I2C initialisieren
  Wire.begin();
  
  // OLED Display initialisieren (optional)
  if(display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    displayAvailable = true;
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("BreMesh RePeter RTC");
    display.println("=======Setup=======");
    display.println("\nWarte auf RTC...");
    display.display();
    Serial.println("OLED Display bereit");
  } else {
    Serial.println("OLED Display nicht gefunden - läuft ohne Display");
  }
  
  // Warte auf RTC (weiß pulsend)
  Serial.println("Warte auf TinyRTC via I2C...");
  bool rtcFound = false;
  int pulseValue = 0;
  int pulseDirection = 5;
  
  while (!rtcFound) {
    // Weiß pulsen
    setLED(pulseValue, pulseValue, pulseValue);
    pulseValue += pulseDirection;
    if (pulseValue >= 255 || pulseValue <= 0) {
      pulseDirection = -pulseDirection;
    }
    
    // Prüfe ob RTC verfügbar ist
    if (rtc.begin()) {
      rtcFound = true;
      Serial.println("RTC gefunden!");
      if (displayAvailable) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("BreMesh RePeter RTC");
        display.println("=======Setup=======");
        display.println("\nRTC: OK");
        display.display();
      }
      setLED(255, 0, 0); // Rot
      delay(500);
    } else {
      delay(10);
    }
  }
  
  // Mit WLAN verbinden
  Serial.print("Verbinde mit WLAN: ");
  Serial.println(ssid);
  
  if (displayAvailable) {
    display.println("\nWLAN Hotspot...");
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
    errorMessage = "WLAN fehlt";
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("FEHLER:");
      display.println("WLAN Verbindung");
      display.println("fehlgeschlagen!");
      display.println();
      display.println("SSID:");
      display.println(ssid);
      display.display();
    }
    return;
  }
  
  Serial.println("\nWLAN verbunden!");
  Serial.print("IP Adresse: ");
  Serial.println(WiFi.localIP());
  
  setLED(255, 255, 0); // Gelb
  
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
  
  pulseLED(255, 255, 0, 1000); // Gelb pulsend
  
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Zeit konnte nicht abgerufen werden!");
    errorMessage = "NTP Sync fehlt";
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
  
  pulseLED(255, 255, 0, 500); // Gelb pulsend während RTC-Programmierung
  
  rtc.adjust(now);
  Serial.println("\nRTC wurde mit aktueller Zeit programmiert!");
  
  syncSuccess = true;
  setLED(0, 255, 0); // Grün - Fertig!
  
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
  // Zeit vom RTC auslesen (UTC)
  DateTime now = rtc.now();
  
  // Deutsche Zeit berechnen (UTC+1)
  DateTime deTime = now + TimeSpan(0, 1, 0, 0); // +1 Stunde
  
  Serial.print("RTC Zeit (UTC): ");
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
  
  Serial.print("DE Zeit (CET):  ");
  Serial.print(deTime.day(), DEC);
  Serial.print('.');
  Serial.print(deTime.month(), DEC);
  Serial.print('.');
  Serial.print(deTime.year(), DEC);
  Serial.print(" ");
  Serial.print(deTime.hour(), DEC);
  Serial.print(':');
  if (deTime.minute() < 10) Serial.print('0');
  Serial.print(deTime.minute(), DEC);
  Serial.print(':');
  if (deTime.second() < 10) Serial.print('0');
  Serial.println(deTime.second(), DEC);
  
  // Zeit auf OLED anzeigen (wenn verfügbar)
  if (displayAvailable) {
    display.clearDisplay();
    
    // Datum
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("DE Zeit (CET):");
    if (deTime.day() < 10) display.print('0');
    display.print(deTime.day(), DEC);
    display.print('.');
    if (deTime.month() < 10) display.print('0');
    display.print(deTime.month(), DEC);
    display.print('.');
    display.println(deTime.year(), DEC);
    
    // Uhrzeit (groß)
    display.setTextSize(2);
    display.setCursor(10, 20);
    if (deTime.hour() < 10) display.print('0');
    display.print(deTime.hour(), DEC);
    display.print(':');
    if (deTime.minute() < 10) display.print('0');
    display.print(deTime.minute(), DEC);
    display.print(':');
    if (deTime.second() < 10) display.print('0');
    display.println(deTime.second(), DEC);
    
    // Status
    display.setTextSize(1);
    display.setCursor(0, 50);
    if (syncSuccess) {
      display.print("Status: OK");
    } else {
      display.print("Fehler: ");
      display.print(errorMessage);
    }
    
    display.display();
  }
  
  delay(1000);
}
