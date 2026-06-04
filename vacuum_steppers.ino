#include <Arduino.h>
#include <avr/io.h>
#include <AccelStepper.h>
#include <avr/wdt.h>

//First stepper, constant rotation
constexpr uint8_t S1_PIN = PB5;
constexpr uint8_t S1_DIR = PB4;

AccelStepper S1{AccelStepper::DRIVER, S1_PIN, S1_DIR};

//Second stepper, accerlating
constexpr uint8_t S2_PIN = PB3;
constexpr uint8_t S2_DIR = PB2;

AccelStepper S2{AccelStepper::DRIVER, S2_PIN, S2_DIR};

//Global variables placeholders for serial data. All speeds/accelerations are in steps/second.
long s1_max_speed      = 0;
long s1_speed          = 0;

long s2_max_speed      = 0;
long s2_acceleration   = 0;
long s2_final_position = 0;

//Safety check to ensure that all serial information is received.
//The final serial input must be -1 so that check = -1. If check == -1 is false, then resetBoard() is called.
int check = 0;

void resetBoard() {
	wdt_enable(WDTO_500MS);
	while(true){

	}
}

int main() {

	init();
	Serial.begin(9600);
	Serial.println("System ready. Awaiting inputs...");

	//Wait for serial parameters to arrive
	while(Serial.available() == 0) {

	}

	//The serial will provide a list of ints in the following order:
	s1_max_speed      = Serial.parseInt();
	s1_speed          = Serial.parseInt();
	s2_max_speed      = Serial.parseInt();
	s2_acceleration   = Serial.parseInt();
	s2_final_position = Serial.parseInt();
	check             = Serial.parseInt(); //Sets check = -1

	//Ensures that all serial parameters were received
	if (check != -1) {
		Serial.println("ERROR: Missing serial parameters. Please try again.");
		resetBoard();
	}
	
	Serial.println("Inputs received! Setting parameters...");

	//Set the motors with their parameters
	S1.setMaxSpeed(s1_max_speed);
	S1.setSpeed(s1_speed);

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