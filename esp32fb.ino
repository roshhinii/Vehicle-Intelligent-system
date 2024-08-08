#include <Arduino.h>
#if defined(ESP32)
  #include <WiFi.h>
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
#endif
#include <Firebase_ESP_Client.h>

//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"

// Insert your network credentials
#define WIFI_SSID "ENTER_YOUR_SSID"
#define WIFI_PASSWORD "ENTER_YOUR_PASSWORD"

// Insert Firebase project API Key
#define API_KEY "ENTER_YOUR_API_KEY"

// Insert RTDB URLefine the RTDB URL */
#define DATABASE_URL "ENTER_YOUR_DATABASE_URL" 

//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;
int count = 0;
bool signupOK = false;

int therm = 0;
int eng = 0;
int steer = 0;
int bat = 0;

int cool_temp = 0;
int eng_temp = 0;
int steering = 0;
float battery = 0;

void setup(){
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Sign up */
  if (Firebase.signUp(&config, &auth, "", "")){
    Serial.println("ok");
    signupOK = true;
  }
  else{
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void loop(){
  if (Firebase.ready() && signupOK && (millis() - sendDataPrevMillis > 500 || sendDataPrevMillis == 0)){
    sendDataPrevMillis = millis();
    
    therm = analogRead(34);
    //eng = analogRead(32);
    steer = analogRead(35);
   // bat = analogRead(33); 

    //Serial.println(therm); //Displays the value
    eng_temp = map(therm, 4095, 100, 29, 70);
    //Serial.println(cool_temp);

    //Serial.println(eng); //Displays the value
    cool_temp =  19; //map(eng, 4095, 100, 29, 70);
    //Serial.println(eng_temp);

    Serial.println(steer); //Displays the value
    steering = map(steer, 0, 4095, 170, 10);
    Serial.println(steering);

    //Serial.println(bat); //Displays the value
    battery = 12.2 ;//map(bat, 0, 4095, 0, 255);
    //Serial.println(battery);


    
    if (Firebase.RTDB.setInt(&fbdo, "COOLANT TEMP", cool_temp) &&
        Firebase.RTDB.setInt(&fbdo, "ENGINE TEMP", eng_temp) &&
        Firebase.RTDB.setInt(&fbdo, "STEERING POSITION", steering) &&
        Firebase.RTDB.setInt(&fbdo, "BATTERY LEVEL", battery)) {
      Serial.println("Data uploaded successfully");
    }
    else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
  }
}
