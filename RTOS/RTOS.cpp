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
#include <L3G.h>
#include <LSM303.h>
#include <semphr.h>
#include <Wire.h>
#include <queue.h>
#include <SharpIR.h>
#define STACK_DEPTH 200

// xSemaphoreHandle sonarSema, magnetoSema, gyroSema, acceSema, analogSema = 0;
int echo_1 = 3; //pin 3 for sonar echo
int trigger_1 = 4; //pin 4 for sonar trigger
int echo_2 = 5;
int trigger_2 = 6;
int echo_3 = 7;
int trigger_3 = 8;

int analog_1 = A0; 
int numOfData = 11;
LSM303 compass;
L3G gyro;
SharpIR sharp(A0, 25, 93, 20150);
int data[12];

/*
index 1 for sonar 1
index 2 for sonar 2
index 3 for sonar 3
index 4 for acc.x
index 5 for acc.y
index 6 for acc.z
index 7 for gyro.x
index 8 for gyro.y
index 9 for gyro.z
index 10 for analog distance sensor
index 11 for compass heading
*/

int freeRAM() {
	extern int __heap_start, *__brkval;
	int v;
	return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int)__brkval);
}

void printArray(void *p) {
	int i;
	char canRead = '0';
	while(1) {
		if(Serial.available()){
			canRead = Serial.read();
		}
		if(canRead - '0'){
			Serial.print(numOfData);
			Serial.print('\r');
			for(i = 1; i < 12; i++) {
				Serial.print(data[i]);
				Serial.print('\r');
			}
			//Serial.println(freeRAM());
			canRead = '0';	
		}
		/*
		for(i = 1; i < 12; i++) {
			Serial.println(data[i]);
			Serial.print('\r');
		}*/
		vTaskDelay(100);
	}
}

void taskReadInfrared(void *p)
{
	int distance;
	while(1) {
		//if(xSemaphoreTake(analogSema, portMAX_DELAY)) {
			distance = sharp.distance();
			data[10] = distance;
			//xSemaphoreGive(gyroSema);
			vTaskDelay(500);
		//}
	}
}

void taskReadSonar(void *p)
{
	unsigned int duration_1, duration_2, duration_3;
	while(1) {
		//if(xSemaphoreTake(sonarSema, portMAX_DELAY)) {
			vTaskSuspendAll();
			digitalWrite(trigger_1, LOW);
			delayMicroseconds(5);
			digitalWrite(trigger_1, HIGH);
			delayMicroseconds(10);
			digitalWrite(trigger_1, LOW);
			pinMode(echo_1, INPUT);
			duration_1 = (unsigned int)pulseIn(echo_1, HIGH);
			data[1] = (int)((duration_1/2) / 29.1);
			
			digitalWrite(trigger_2, LOW);
			delayMicroseconds(5);
			digitalWrite(trigger_2, HIGH);
			delayMicroseconds(10);
			digitalWrite(trigger_2, LOW);
			duration_2 = (unsigned int)pulseIn(echo_2, HIGH);
			data[2] = (int)((duration_2/2) / 29.1);
			
			digitalWrite(trigger_3, LOW);
			delayMicroseconds(5);
			digitalWrite(trigger_3, HIGH);
			delayMicroseconds(10);
			digitalWrite(trigger_3, LOW);
			duration_3 = (unsigned int)pulseIn(echo_3, HIGH);
			data[3] = (int)((duration_3/2) / 29.1);
			xTaskResumeAll();
			//xSemaphoreGive(analogSema);
			vTaskDelay(500);
		//}
	}
}

void taskReadAcc(void *p) 
{
	int accX, accY, accZ;
	while(1){
		//if(xSemaphoreTake(acceSema, portMAX_DELAY)) {
			vTaskSuspendAll();
			compass.read();
			xTaskResumeAll();
			accX = (int)((float)compass.a.x / 1000.000 * 61 * 0.001 * 9.8);
			accY = (int)((float)compass.a.y / 1000.000 * 61 * 0.001 * 9.8);
			accZ = (int)((float)compass.a.z / 1000.000 * 61 * 0.001 * 9.8);
			data[4] = accX;
			data[5] = accY;
			data[6] = accZ;
		//	xSemaphoreGive(sonarSema);
			vTaskDelay(500);
		//}
	}
}

void taskReadGyro(void *p)
{
	int gyroX, gyroY, gyroZ;
	while(1){
		//if(xSemaphoreTake(gyroSema, portMAX_DELAY)) {
			vTaskSuspendAll();
			gyro.read();
			xTaskResumeAll();
	
			gyroX = (int)((float)gyro.g.x * 8.75 /1000.00);
			gyroY = (int)((float)gyro.g.y * 8.75 /1000.00);
			gyroZ = (int)((float)gyro.g.z * 8.75 /1000.00);
		
			data[7] = gyroX;
			data[8] = gyroY;
			data[9] = gyroZ;
			//xSemaphoreGive(acceSema);
			vTaskDelay(500);
		//}
	}
}

void taskReadMagneto(void *p)
{	
	int heading;
	while(1){
	//	if(xSemaphoreTake(magnetoSema, portMAX_DELAY)) {
			vTaskSuspendAll();
			compass.read();
			heading = (int) compass.heading();
			data[11] = heading;
			xTaskResumeAll();
		//	xSemaphoreGive(sonarSema);
			vTaskDelay(500);
		//}
	}
}

void setup(void) 
{
	// Starting up serial monitor
	Serial.begin(9600);
	// Setting up compass
	Wire.begin();
	compass.init();
	compass.enableDefault();
	compass.m_min = (LSM303::vector<int16_t>){+1824, +347, +1103};
	compass.m_max = (LSM303::vector<int16_t>){+1884, +420, +1203};
	gyro.init();
	gyro.enableDefault();
	// Setting up sonar sensor
	pinMode(trigger_1, OUTPUT);
	pinMode(echo_1, INPUT);
	pinMode(echo_2, INPUT);
	pinMode(trigger_2, OUTPUT);
	pinMode(echo_3, INPUT);
	pinMode(trigger_3, OUTPUT);
	
	pinMode(analog_1, INPUT);
}

int main(void)
{
	init();
	setup();
	TaskHandle_t t1, t2, t3, t4, t5, t6;
	// Create tasks
	xTaskCreate(printArray, "printA", STACK_DEPTH, NULL, 10, &t1);
	xTaskCreate(taskReadGyro, "Read Gyrometer", STACK_DEPTH, NULL, 9, &t2);
	xTaskCreate(taskReadAcc, "Read Accelerometer", STACK_DEPTH, NULL, 8, &t3);
	//xTaskCreate(taskReadInfrared, "Read Infrared", STACK_DEPTH, NULL, 7, &t4);
	xTaskCreate(taskReadMagneto, "Read Magneto", STACK_DEPTH, NULL, 6, &t5);
	xTaskCreate(taskReadSonar, "Read Ultrasonic", STACK_DEPTH, NULL, 5, &t6);
	vTaskStartScheduler();
}
