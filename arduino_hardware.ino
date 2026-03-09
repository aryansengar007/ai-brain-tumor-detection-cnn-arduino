/**
 * BRAIN TUMOR CLASSIFICATION - ARDUINO ROBOTICS INTEGRATION
 * 
 * Components:
 * - Arduino UNO
 * - Ultrasonic Sensor HC-SR04 (pins D9, D10)
 * - Servo Motor SG90 (pin D6)
 * - Red LED (pin D2)
 * - Blue LED (pin D3)
 * - Green LED (pin D4)
 * - LCD 16x2 JHD162A (4-bit mode)
 * - 10k Potentiometer (for LCD contrast control)
 * 
 * Hardware Wiring:
 * 
 * ULTRASONIC (HC-SR04):    SERVO (SG90):        LEDs:
 * ├─ VCC → 5V              ├─ Red → 5V          ├─ Red → D2
 * ├─ GND → GND             ├─ Brown → GND       ├─ Blue → D3
 * ├─ TRIG → D9             └─ Orange → D6       └─ Green → D4
 * └─ ECHO → D10
 * 
 * LCD (16x2 JHD162A):
 * ├─ VSS (1) → GND                              ├─ E (6) → D11
 * ├─ VDD (2) → 5V                               ├─ D4 (11) → D5
 * ├─ V0 (3) → Potentiometer middle pin          ├─ D5 (12) → D7
 * ├─ RS (4) → D12                               ├─ D6 (13) → D8
 * ├─ R/W (5) → GND                              ├─ D7 (14) → D13
 * └─ A (15) → 5V                                └─ K (16) → GND
 * 
 * 10k Potentiometer:
 * ├─ Pin 1 → GND
 * ├─ Pin 2 → LCD V0 (pin 3)
 * └─ Pin 3 → 5V
 * 
 * Serial Communication Signals from Laptop:
 * R - Red LED + Servo 180° (High Risk)
 * Y - Blue LED + Servo 90° (Moderate Risk)
 * G - Green LED + Servo 0° (Healthy)
 * B - Blue LED (Low Confidence)
 */

#include <Servo.h>
#include <LiquidCrystal.h>

// LCD Initialization (4-bit mode)
// RS → D12, E → D11, D4 → D5, D5 → D7, D6 → D8, D7 → D13
LiquidCrystal lcd(12, 11, 5, 7, 8, 13);

// Servo motor
Servo servo;
const int SERVO_PIN = 6;

// Ultrasonic sensor pins
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

// LED pins
const int RED_LED = 2;
const int BLUE_LED = 3;
const int GREEN_LED = 4;

// Distance threshold (cm)
const int DETECTION_DISTANCE = 40;

// Global variables
int lastDetectionDistance = 0;
unsigned long lastPatientDetectionTime = 0;
const unsigned long PATIENT_DETECTION_TIMEOUT = 5000; // 5 seconds

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize servo
  servo.attach(SERVO_PIN);
  servo.write(0); // Home position
  
  // Initialize LED pins
  pinMode(RED_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  
  // Initialize ultrasonic sensor pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Initialize LCD (16x2)
  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("Brain Tumor");
  lcd.setCursor(0, 1);
  lcd.print("Classification");
  
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Ready");
  delay(1000);
  lcd.clear();
  
  // Turn off all LEDs initially
  digitalWrite(RED_LED, LOW);
  digitalWrite(BLUE_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
}

void loop() {
  // Check for patient detection
  int distance = measureDistance();
  lastDetectionDistance = distance;
  
  if (distance < DETECTION_DISTANCE && distance > 0) {
    // Patient detected
    if (millis() - lastPatientDetectionTime > PATIENT_DETECTION_TIMEOUT) {
      // First time detection in this session
      displayPatientDetected();
      lastPatientDetectionTime = millis();
    }
  }
  
  // Check for serial data from laptop
  if (Serial.available() > 0) {
    char signal = Serial.read();
    processSignal(signal);
  }
  
  delay(100); // Short delay for stability
}

/**
 * Measure distance using ultrasonic sensor
 * Returns: distance in cm, or -1 if error
 */
int measureDistance() {
  // Clear trigger pin
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Send ultrasonic pulse
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Measure pulse duration
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
  
  if (duration == 0) {
    return -1; // Sensor error
  }
  
  // Calculate distance (speed of sound: 343 m/s)
  int distance = duration * 0.034 / 2;
  return distance;
}

/**
 * Display "Patient Detected" message on LCD
 */
void displayPatientDetected() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Patient Detected");
  lcd.setCursor(0, 1);
  lcd.print("Scan QR: Upload");
  
  // Optional: blink all LEDs to indicate detection
  for (int i = 0; i < 3; i++) {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(BLUE_LED, HIGH);
    digitalWrite(GREEN_LED, HIGH);
    delay(200);
    
    digitalWrite(RED_LED, LOW);
    digitalWrite(BLUE_LED, LOW);
    digitalWrite(GREEN_LED, LOW);
    delay(200);
  }
  
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Awaiting Result");
  lcd.setCursor(0, 1);
  lcd.print("Distance: ");
  lcd.print(lastDetectionDistance);
  lcd.print("cm");
}

/**
 * Process incoming signal from laptop
 * R = High Risk (Red)
 * Y = Moderate Risk (Blue)
 * G = Healthy (Green)
 * B = Low Confidence (Blue alternate pattern)
 */
void processSignal(char signal) {
  // Clear LCD and display status
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Result Received:");
  
  switch (signal) {
    case 'R': // HIGH RISK - Red LED + Servo 180°
      handleHighRisk();
      Serial.println("HIGH_RISK: Red LED, Servo 180°");
      break;
      
    case 'B': // MODERATE RISK - Blue LED + Servo 90°
      handleModerateRisk();
      Serial.println("MODERATE_RISK: Blue LED, Servo 90°");
      break;
      
    case 'G': // HEALTHY - Green LED + Servo 0°
      handleHealthy();
      Serial.println("HEALTHY: Green LED, Servo 0°");
      break;
      
    default:
      Serial.print("Unknown signal: ");
      Serial.println(signal);
      break;
  }
}

/**
 * HIGH RISK Handler
 */
void handleHighRisk() {
  // Turn off all LEDs
  allLedsOff();
  
  // Blink red LED
  for (int i = 0; i < 5; i++) {
    digitalWrite(RED_LED, HIGH);
    delay(300);
    digitalWrite(RED_LED, LOW);
    delay(300);
  }
  
  // Keep red LED on
  digitalWrite(RED_LED, HIGH);
  
  // Move servo to 180° (alert position)
  servo.write(180);
  
  // Display on LCD
  lcd.setCursor(0, 1);
  lcd.print("TUMOR DETECTED");
  
  delay(3000);
  allLedsOff();
  servo.write(0);
}

/**
 * MODERATE RISK Handler
 */
void handleModerateRisk() {
  // Turn off all LEDs
  allLedsOff();
  
  // Toggle blue LED
  for (int i = 0; i < 3; i++) {
    digitalWrite(BLUE_LED, HIGH);
    delay(400);
    digitalWrite(BLUE_LED, LOW);
    delay(400);
  }
  
  // Keep blue LED on
  digitalWrite(BLUE_LED, HIGH);
  
  // Move servo to 90° (middle position)
  servo.write(90);
  
  // Display on LCD
  lcd.setCursor(0, 1);
  lcd.print("CHECK REQUIRED");
  
  delay(3000);
  allLedsOff();
  servo.write(0);
}

/**
 * HEALTHY Handler
 */
void handleHealthy() {
  // Turn off all LEDs
  allLedsOff();
  
  // Turn on green LED
  digitalWrite(GREEN_LED, HIGH);
  delay(500);
  
  // Blink green LED twice
  for (int i = 0; i < 2; i++) {
    digitalWrite(GREEN_LED, LOW);
    delay(300);
    digitalWrite(GREEN_LED, HIGH);
    delay(300);
  }
  
  // Keep green LED on
  digitalWrite(GREEN_LED, HIGH);
  
  // Move servo to 0° (home position)
  servo.write(0);
  
  // Display on LCD
  lcd.setCursor(0, 1);
  lcd.print("NO TUMOR");
  
  delay(3000);
  allLedsOff();
}

/**
 * Turn off all LEDs
 */
void allLedsOff() {
  digitalWrite(RED_LED, LOW);
  digitalWrite(BLUE_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
}