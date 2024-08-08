const int groundpin = 18;
const int powerpin = 19; 

const int ypin = A2;           

const int acc = A0;
const int brak = A1;

int accelerator=0;
int brake=0;
int y = 0;

int a1 = 2;
int a2 = 3;

int b1 = 4;
int b2 = 7;

int c1 = 8;
int c2 = 9;

void setup() {

  Serial.begin(9600);

  pinMode(groundpin, OUTPUT);
  pinMode(powerpin, OUTPUT);

  digitalWrite(groundpin, LOW);
  digitalWrite(powerpin, HIGH);

  pinMode(a1, OUTPUT);
  pinMode(a2, OUTPUT);

  pinMode(b1, OUTPUT);
  pinMode(b2, OUTPUT);

  pinMode(c1, OUTPUT);
  pinMode(c2, OUTPUT);
}

void loop() {

  accelerator = analogRead(acc);
  brake = analogRead(brak);

  y = analogRead(ypin);

  if(accelerator>=0 && accelerator<=25){
    a1 = LOW;
    a2 = LOW;
  }

  else if(accelerator>=26 && accelerator<=300){
    a1 = LOW;
    a2 = HIGH;
  }

  else if(accelerator>=301 && accelerator<=700){
    a1 = HIGH;
    a2 = LOW;
  }

  else if(accelerator>=701){
    a1 = HIGH;
    a2 = HIGH;
  }


  if(brake>=0 && brake<=5){
    b1 = LOW;
    b2 = LOW;
  }

  else if(brake>5 && brake<=50){
    b1 = LOW;
    b2 = HIGH;
  }

  else if(brake>50 && brake<=450){
    b1 = HIGH;
    b2 = LOW;
  }

  else if(brake>450){
    b1 = HIGH;
    b2 = HIGH;
  }
 Serial.println(accelerator);
 Serial.println(brake);

  Serial.println(accelerator);
  Serial.print("A1:");
  Serial.println(a1);
  Serial.print("A2:");
  Serial.println(a2);

  
  Serial.println(brake);
  Serial.print("B1:");
  Serial.println(b1);
  Serial.print("B2:");
  Serial.println(b2);


  if(y >= 315 && y <= 349){
    Serial.println("IDLE");
    c1 = LOW;
    c2 = LOW;
  }

  else if(y >= 0 && y <= 314){
    Serial.println("LEFT CORNERING");
    c1 = LOW;
    c2 = HIGH;
  }
  
  else if(y >= 350){
    Serial.println("RIGHT CORNERING");
    c1 = HIGH;
    c2 = LOW;
  }


  Serial.print("Y-AXIS - ");
  Serial.println(analogRead(y));



  delay(500);
}
