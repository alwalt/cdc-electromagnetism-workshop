#include <CapacitiveSensor.h>

CapacitiveSensor sensor = CapacitiveSensor(4, 2);

void setup() {
  Serial.begin(115200);

  sensor.set_CS_AutocaL_Millis(0);
}

void loop() {

  long value = sensor.capacitiveSensor(30);

  Serial.print(value);
  Serial.print(" |");

  int bars = map(value, 0, 400, 0, 80);

  bars = constrain(bars, 0, 80);

  for (int i = 0; i < bars; i++)
    Serial.print("#");

  Serial.println();

  delay(30);
}