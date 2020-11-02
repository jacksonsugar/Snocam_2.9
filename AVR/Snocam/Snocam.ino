#include "LowPower.h"

int WIFI_SIG = 3;
int Pi_on = 5;
int LED = 7;

void setup(void)
{
  pinMode(WIFI_SIG, INPUT_PULLUP);
  pinMode(Pi_on, OUTPUT); 
  pinMode(LED, OUTPUT);

  digitalWrite(Pi_on, LOW);
  digitalWrite(LED, LOW);

  for(int i = 0; i < 3; i++){
    digitalWrite(LED, HIGH);
    delay(400);
    digitalWrite(LED, LOW);
    delay(100);
  }
}

void Pi_Samp() {
  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  int WIFI_Status = digitalRead(WIFI_SIG);

  do {
    digitalWrite(LED, HIGH);
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    WIFI_Status = digitalRead(WIFI_SIG);
  }
  while (WIFI_Status == HIGH);

  digitalWrite(LED, LOW);

  for (int i = 1; i <= 5; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  digitalWrite(Pi_on, LOW);
}


void loop(void) 
{

  Pi_Samp();

  //This is the sleep cycle! Set for 150 cycles of 4 seconds for 10 minutes
  for (int i = 1; i <= 150; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

}




