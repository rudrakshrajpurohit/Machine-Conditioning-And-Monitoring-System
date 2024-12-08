// Pin definitions for ADXL335 sensors
const int xPin1 = A0;    // X-axis for first ADXL335
const int yPin1 = A1;    // Y-axis for first ADXL335
const int zPin1 = A2;    // Z-axis for first ADXL335

const int xPin2 = A3;    // X-axis for second ADXL335
const int yPin2 = A4;    // Y-axis for second ADXL335
const int zPin2 = A5;    // Z-axis for second ADXL335

// Relay pins
const int relay1 = 52;    // Relay for fan 1
const int relay2 = 53;    // Relay for fan 2

// Calibration variables
const float zeroG = 512.0; // Typical value for ADXL335 at 0g
const float sensitivity = 0.33; // Sensitivity in V/g (typical for ADXL335)

// Variables for calculations
const int numSamples = 200;  // Increased number of samples
unsigned long sampleDelay = 5; // Reduced delay between samples

void setup() {
  Serial.begin(9600);
  
  // Set relay pins as outputs
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  
  // Turn on both fans
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, LOW);
  
  // Debug print
  Serial.println("Arduino setup complete. Sending vibration data...");
  
  delay(1000); // Startup delay
}

float calculateVibrationIntensity(int xPin, int yPin, int zPin) {
  // Read raw analog values
  long sumX = 0, sumY = 0, sumZ = 0;
  
  // Collect multiple samples
  for(int i = 0; i < numSamples; i++) {
    sumX += analogRead(xPin);
    sumY += analogRead(yPin);
    sumZ += analogRead(zPin);
    delay(sampleDelay);
  }
  
  // Calculate averages
  float avgX = sumX / (float)numSamples;
  float avgY = sumY / (float)numSamples;
  float avgZ = sumZ / (float)numSamples;
  
  // Convert to acceleration
  float accelX = ((avgX - zeroG) / zeroG) / sensitivity;
  float accelY = ((avgY - zeroG) / zeroG) / sensitivity;
  float accelZ = ((avgZ - zeroG) / zeroG) / sensitivity;
  
  // Calculate magnitude (RMS)
  float magnitude = sqrt(
    sq(accelX) + 
    sq(accelY) + 
    sq(accelZ)
  );
  
  // Calculate variance as a measure of vibration intensity
  float varianceX = 0, varianceY = 0, varianceZ = 0;
  
  for(int i = 0; i < numSamples; i++) {
    float x = analogRead(xPin);
    float y = analogRead(yPin);
    float z = analogRead(zPin);
    
    varianceX += sq(x - avgX);
    varianceY += sq(y - avgY);
    varianceZ += sq(z - avgZ);
  }
  
  varianceX /= numSamples;
  varianceY /= numSamples;
  varianceZ /= numSamples;
  
  // Combine magnitude and variance for more sensitive measurement
  float vibrationIntensity = magnitude * sqrt(
    varianceX + 
    varianceY + 
    varianceZ
  );
  
  return vibrationIntensity;
}

void loop() {
  // Ensure fans are running
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, LOW);
  
  // Calculate vibration intensity for both fans
  float vibration1 = calculateVibrationIntensity(xPin1, yPin1, zPin1);
  float vibration2 = calculateVibrationIntensity(xPin2, yPin2, zPin2);
  
  // Send data to Serial with consistent formatting and more precision
  Serial.print(vibration1, 4);  // 4 decimal places
  Serial.print(",");
  Serial.println(vibration2, 4);  // 4 decimal places, with newline
  
  // Short delay between measurements
  delay(500);
} 
