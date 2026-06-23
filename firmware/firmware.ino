#include <Arduino.h>
#include <avr/io.h>
#include <AccelStepper.h>
#include <avr/wdt.h>
#include <string.h>

//First stepper, constant rotation
constexpr uint8_t s1_dir = 13;
constexpr uint8_t s1_pin = 12;

AccelStepper S1{AccelStepper::DRIVER, s1_pin, s1_dir};

//Second stepper, accerlating
constexpr uint8_t s2_dir = 11;
constexpr uint8_t s2_pin = 10;

AccelStepper S2{AccelStepper::DRIVER, s2_pin, s2_dir};

//Global variables placeholders for serial data. All speeds/accelerations are in steps/second.
float s1_max_speed = 0;
float s1_speed = 0;

float s2_max_speed = 0;
float s2_acceleration = 0;

long s2_final_position = 0;
long s2_home_prime = 0;

constexpr uint8_t BUFFER_SIZE = 64;
char input_buffer[BUFFER_SIZE];
uint8_t buffer_index = 0;

void resetBoard() {
	wdt_enable(WDTO_250MS);
	while(true){

	}
}

// A djb2 hash string converter that is C++11 compliant.
// Uses recursion instead of a while loop.

constexpr uint32_t hashString11(const char* str, uint32_t hash = 5381) {
    return *str ? hashString11(str + 1, ((hash << 5) + hash) + *str) : hash;
}

void parseAndExecute(char* packet) {
	int cmd_tracker = 1;
	char* packet_bookmark;
	char* cmd_data_bookmark;

	char* cmd_data_substring = strtok_r(packet, ",", &packet_bookmark);

	while (cmd_data_substring != nullptr) {
		
		char* cmd = strtok_r(cmd_data_substring, "=", &cmd_data_bookmark);
		char* value_str = strtok_r(nullptr, "=", &cmd_data_bookmark);

		switch (hashString11(cmd)) {
			
			case hashString11("S1_MAX"):

				s1_max_speed = atof(value_str);
				S1.setMaxSpeed(s1_max_speed);

				Serial.print("S1 max speed: ");
				Serial.print(s1_max_speed);
				Serial.print(" step/s | ");

				break;
			
			case hashString11("S1_SPD"):

				s1_speed = atof(value_str);
                S1.setSpeed(s1_speed);

				Serial.print("S1 speed: ");
				Serial.print(s1_speed);
				Serial.print(" step/s | ");

				break;

			case hashString11("S2_MAX"):

				s2_max_speed = atof(value_str);
				S2.setMaxSpeed(s2_max_speed);

				Serial.print("S2 max speed: ");
				Serial.print(s2_max_speed);
				Serial.print(" step/s | ");

				break;

			case hashString11("S2_ACC"):

				s2_acceleration = atof(value_str);
				S2.setAcceleration(s2_acceleration);

				Serial.print("S2 acceleration: ");
				Serial.print(s2_acceleration);
				Serial.print(" step/s^2 | ");

				break;
			
			case hashString11("S2_END"):

				s2_final_position = atof(value_str);
				S2.moveTo(s2_final_position);

				Serial.print("S2 final position: ");
				Serial.print(s2_final_position);
				Serial.print(" step | ");

				break;

			case hashString11("S2_SET"):

				s2_home_prime = S2.currentPosition();
				S2.moveTo(s2_home_prime);

				Serial.print("Home @: ");
				Serial.print(s2_home_prime);
				Serial.print(" step | ");

				break;
			
			case hashString11("S2_HOM"):

				S2.moveTo(s2_home_prime);

				Serial.print("Going home");

				break;

			case hashString11("S2_MOV"):
			{
				long rel_steps = atol(value_str);
				S2.move(rel_steps);

				Serial.print("Moving ");
				Serial.print(rel_steps);
				Serial.print(" steps | ");

				break;
			}

			case hashString11("S2_MTP"):
			{
				long abs_steps_prime = atol(value_str);
				S2.moveTo(s2_home_prime + abs_steps_prime);

				Serial.print("Moving to ");
				Serial.print(abs_steps_prime);
				Serial.print(" steps | ");

				break;
			}

			case hashString11("S2_RST"):

				s2_home_prime = 0;
				
				Serial.print("Home @: 0 step | ");

				break;

			case hashString11("S2_MTA"):
			{
				long abs_steps = atol(value_str);
				S2.moveTo(abs_steps);

				Serial.print("Moving to ");
				Serial.print(abs_steps);
				Serial.print(" steps | ");

				break;
			}

			case hashString11("RESET"):

				resetBoard();

				break;

			default:
				cmd = nullptr;
				value_str = nullptr;

				Serial.print("Command ");
				Serial.print(cmd_tracker);
				Serial.println(" is invalid. Please try again... | ");

				break;
			
		}
		
		Serial.print("\n");
		cmd_tracker ++;
		cmd_data_substring = strtok_r(nullptr, ",", &packet_bookmark);
	}
}

void bufferTransfer() {
	while (Serial.available() > 0) {
		char incoming_char = (char) Serial.read();

		if (incoming_char == '\n' || incoming_char == '\r') {
			if (buffer_index > 0) {
				input_buffer[buffer_index] = '\0';
				parseAndExecute(input_buffer);
				buffer_index = 0;
			}
		}
		else {
			if (buffer_index < (BUFFER_SIZE - 1)) {
				input_buffer[buffer_index] = incoming_char;
				buffer_index ++;
			}
		}
	}
}

int main() {

	wdt_disable();

	//Initialize serial
	init();
	Serial.begin(115200);
	Serial.println("System ready. Awaiting inputs...");

	while(1) {
		
		bufferTransfer();

		//Trigger each motor. These two commands need to be run as frequently as possible for smooth movement to occur
		S1.runSpeed();
		S2.run();
	}

	return 0;
}