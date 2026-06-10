#include "HardwareSerial.h"
#include <Arduino.h>
#include <avr/io.h>
#include <AccelStepper.h>
#include <avr/wdt.h>

//First stepper, constant rotation
constexpr uint8_t s1_dir = 13;
constexpr uint8_t s1_pin = 12;

AccelStepper S1{AccelStepper::DRIVER, s1_pin, s1_dir};

//Second stepper, accerlating
constexpr uint8_t s2_dir = 11;
constexpr uint8_t s2_pin = 10;

AccelStepper S2{AccelStepper::DRIVER, s2_pin, s2_dir};

//Global variables placeholders for serial data. All speeds/accelerations are in steps/second.
float s1_max_speed      = 0;
float s1_speed          = 0;

float s2_max_speed      = 0;
float s2_acceleration   = 0;

long s2_final_position = 0;

void resetBoard() {
	wdt_enable(WDTO_250MS);
	while(true){

	}
}

int main() {

	wdt_disable();

	//Initialize serial
	init();
	Serial.begin(9600);
	Serial.println("System ready. Awaiting inputs...");

	//Wait for only our specific "u ... -1" serial parameters to arrive
	while(true) {
		if(Serial.available() > 0) {
			
			char check = Serial.peek();
			if (check == 'u') {
				break;
			
			} else {
				Serial.read();
			}
		}
	}

	//The serial data must be provided in the order below. The first item must be the char 'u' and 
	//the final item must be the int -1. These are used to check that serial communication was successful.

	char first_item = Serial.read();

	s1_max_speed      = Serial.parseFloat();
	s1_speed          = Serial.parseFloat();
	s2_max_speed      = Serial.parseFloat();
	s2_acceleration   = Serial.parseFloat();
	s2_final_position = Serial.parseInt();
	
	int last_item = Serial.parseInt();

        if (first_item != 'u' || last_item != -1) {
          Serial.println("There was an error with the serial communication. "
                         "Please try again.");
          resetBoard();
        }

        Serial.println("Inputs received! Setting parameters...");

	//Set the motors with their parameters
	S1.setMaxSpeed(s1_max_speed);
	S1.setSpeed(s1_speed);

	S2.setCurrentPosition(0);
	S2.setMaxSpeed(s2_max_speed);
	S2.setAcceleration(s2_acceleration);
	S2.moveTo(s2_final_position);

	Serial.println("Parameters set. Beginning motors...");

	while(1) {

		//Trigger each motor. These two commands need to be run as frequently as possible for smooth movement to occur
		S1.runSpeed();
		S2.run();
	}

	return 0;
}