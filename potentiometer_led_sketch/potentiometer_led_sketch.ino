// The Arduino-only version: the board does everything by itself.
// Turn the potentiometer on A0 to change the LED brightness on pin 9.
// Open Tools > Serial Monitor (9600 baud) to see the values.
//
// The Python version (potentiometer_led.py) does the same thing from your
// computer. For that, upload StandardFirmata to the board instead of this.

const int ledPin = 9;      // must be a PWM pin (marked ~)
const int potPin = A0;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int potValue = analogRead(potPin);              // 0-1023
  int ledValue = map(potValue, 0, 1023, 0, 255);  // 0-255
  Serial.println(ledValue);
  analogWrite(ledPin, ledValue);
  delay(50);
}
