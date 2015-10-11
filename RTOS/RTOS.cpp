/*
 * RTOS.cpp
 *
 * Created: 13/9/2015 4:35:58 PM
 *  Author: uSER
 */ 


#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <LSM303.h>
#include <semphr.h>
#include <Wire.h>
#include <queue.h>
#include <SharpIR.h>
#define STACK_DEPTH 160

// xSemaphoreHandle sonarSema, magnetoSema, gyroSema, acceSema, analogSema = 0;
int echo_1 = 3; //pin 3 for sonar echo
int trigger_1 = 4; //pin 4 for sonar trigger
int echo_2 = 5;
int trigger_2 = 6;
int echo_3 = 7;
int trigger_3 = 8;
int checkSum = 0;
int numOfData = 5;
char canRead = '0';
LSM303 compass;
int data[5];

void handShake(void *p) {
	int i;
	while(1) {
		if(Serial1.available()) {
			canRead = Serial1.read();
			if(canRead == 'H') {
				Serial1.print('A');
				Serial1.print('\r');
			}
			else if(canRead == 'P') {
				checkSum = numOfData;
				Serial1.print(numOfData);
				Serial1.print('\n');
				for(i = 0; i < 5; i++) {
					checkSum += data[i];
					Serial1.print(data[i]);
					Serial1.print('\n');
				}
				Serial1.print(checkSum);
				Serial1.print('\n');
				Serial1.print('\r');
			}
			else {
				Serial1.print('N');
				Serial1.print('\r');
			}
			canRead = '0';
			data[3] = 0;
		}
		vTaskDelay(100);
	}
}

void printArray(void *p) {
	int i;
	char canRead = '0';


	 
	while(1) {
		for(i = 0; i < 6; i++) {
			Serial.println(data[i]);
		}
		
		vTaskDelay(1000);
		
	}
}

void taskReadSonar(void *p)
{
	int duration_1, duration_2, duration_3;
	while(1) {
		vTaskSuspendAll();
		digitalWrite(trigger_1, LOW);
		delayMicroseconds(5);
		digitalWrite(trigger_1, HIGH);
		delayMicroseconds(10);
		digitalWrite(trigger_1, LOW);
		pinMode(echo_1, INPUT);
		duration_1 = (int)pulseIn(echo_1, HIGH);
		data[0] = (int)((duration_1/2) / 29.1);
			
		digitalWrite(trigger_2, LOW);
		delayMicroseconds(5);
		digitalWrite(trigger_2, HIGH);
		delayMicroseconds(10);
		digitalWrite(trigger_2, LOW);
		duration_2 = (int)pulseIn(echo_2, HIGH);
		data[1] = (int)((duration_2/2) / 29.1);
			
		digitalWrite(trigger_3, LOW);
		delayMicroseconds(5);
		digitalWrite(trigger_3, HIGH);
		delayMicroseconds(10);
		digitalWrite(trigger_3, LOW);
		duration_3 = (int)pulseIn(echo_3, HIGH);
		data[2] = (int)((duration_3/2) / 29.1);
		xTaskResumeAll();
			
		vTaskDelay(500);
	}
}

void taskReadAcc(void *p) 
{
	int accX, accY, accZ, offset, hasOffset, stepCount;
	int acc = 0;
	long lastTimeStepDetected = 0;
	hasOffset = stepCount = 0;
	double accSquare = 0;
	while(1){
		vTaskSuspendAll();
		compass.read();
		xTaskResumeAll();
		
		accX = compass.a.x / 1000;
		accY = compass.a.y / 1000;
		accZ = compass.a.z / 1000;
		
		/*
		Serial.println(accX);
		Serial.println(accY);
		Serial.println(accZ);
		Serial.println(accSquare);
		*/
		accSquare = accX*accX + accY*accY + accZ*accZ;
		acc = (int)sqrt(accSquare);

		if (hasOffset == 0) {
			offset = acc;
			hasOffset = 1;
		}
		
		
		if (acc > 18 || acc < 13) {
			if (millis() - lastTimeStepDetected > 1000) {
				//stepCount++;
				data[3] = 1; //stepCount;
				lastTimeStepDetected = millis();
			}
		}
		
		data[4] = (int) compass.heading();
		
		vTaskDelay(200);
	}
}

void setup(void) 
{
	// Starting up serial monitor
	Serial1.begin(9600);
	//Serial1.begin(9600);
	// Setting up compass
	Wire.begin();
	compass.init();
	compass.enableDefault();
	compass.m_min = (LSM303::vector<int16_t>){+1824, +347, +1103};
	compass.m_max = (LSM303::vector<int16_t>){+1884, +420, +1203};
	// Setting up sonar sensor
	pinMode(trigger_1, OUTPUT);
	pinMode(echo_1, INPUT);
	pinMode(echo_2, INPUT);
	pinMode(trigger_2, OUTPUT);
	pinMode(echo_3, INPUT);
	pinMode(trigger_3, OUTPUT);
}

int main(void)
{
	init();
	setup();
	TaskHandle_t t1, t2, t3;
	// Create tasks
	xTaskCreate(handShake, "Handshake", STACK_DEPTH, NULL, 10, &t1);
	//xTaskCreate(printArray, "printA", STACK_DEPTH, NULL, 10, &t1);
	xTaskCreate(taskReadAcc, "Read Accelerometer", 250, NULL, 9, &t2);
	xTaskCreate(taskReadSonar, "Read Ultrasonic", STACK_DEPTH, NULL, 7, &t3);
	vTaskStartScheduler();
}