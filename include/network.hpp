#include "network.h"

#ifdef ESP8266
#include <ESP8266WiFi.h>
#elif defined(ESP32)
#include <WiFi.h>
#endif

#include <WiFiManager.h>

WiFiManager wifiManager(Serial);

void Network::info() {
#if WIFI_VERBOSE
    WiFi.printDiag(Serial);
#endif
}

int Network::getQuality() {
    int rssi = WiFi.RSSI();
    return wifiManager.getRSSIasQuality(rssi);
}

void Network::rtcMode() { wifiManager.setConfigPortalTimeout(120); }

void Network::disable() { wifiManager.disconnect(); }

void Network::reboot() { wifiManager.reboot(); }

void Network::resetSettings() {
    wifiManager.resetSettings();
    wifiManager.reboot();
}

String Network::getSSID() { return wifiManager.getWiFiSSID(); }

void Network::setup(const char *hostname) {
#if defined(ESP8266) || defined(ESP32)
    WiFi.mode(WIFI_STA);
#endif
    wifiManager.setHostname(hostname);
#if MANUAL_WIFI_SETTINGS
    wifiManager.preloadWiFi(WIFI_SSID, WIFI_PASSWORD);
#endif
    wifiManager.setConnectTimeout(20);
#if CP_PROTECTED
    wifiManager.autoConnect(CP_SSID, CP_PASSWORD);
#else
    wifiManager.autoConnect(CP_SSID);
#endif
    // explicitly disable AP, esp defaults to STA+AP
#if defined(ESP8266)
    WiFi.enableAP(false);
#elif defined(ESP32)
    WiFi.softAPdisconnect(true);
#endif
    Network::info();
}

void Network::loop() { wifiManager.process(); }
