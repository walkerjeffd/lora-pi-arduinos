int count = 0;

void setup() {
  // put your setup code here, to run once:
  while (!Serial); 
  Serial.begin(9600);
}

void loop() {
  Serial.print("Count: ");
  Serial.println(count++);
  delay(1000);
}
