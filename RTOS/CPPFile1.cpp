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
#include <Wire.h>
#include <queue.h>
#define STACK_DEPTH 128

int x = 0;
int y = 100;

void taskX(void *p)
{
	
	while(1) {
		x++;
		Serial.print(x);
		vTaskDelay(1000);
	}
}

void taskY(void *p)
{
	while(1){
		y++;
		Serial.print(y);
		digitalWrite(13, HIGH);
		vTaskDelay(500);
		digitalWrite(13, LOW);
		vTaskDelay(500);
	}
}
/*
void vApplicationIdleHook()
{
	// Do nothing.
}*/

void setup1(void) 
{
	// Starting up serial monitor
	Serial.begin(9600);
	// Setting up compass
	
	// Setting up sonar sensor
	
	pinMode(12, OUTPUT);
	pinMode(13, OUTPUT);
}
/*
int main(void)
{
	init();
	setup1();
	TaskHandle_t t1, t2, t3;
	// Create tasks
	xTaskCreate(taskX, "Read Ultrasonic", STACK_DEPTH, NULL, 6, &t1);
	xTaskCreate(taskY, "Read Magneto", STACK_DEPTH, NULL, 5, &t2);
	//xTaskCreate(printQ, "printQ", STACK_DEPTH, NULL, 3, &t3);
	vTaskStartScheduler();
}*/