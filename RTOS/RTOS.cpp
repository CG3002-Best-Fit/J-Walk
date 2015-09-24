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
#define STACK_DEPTH 160
// Tasks flash LEDs at Pins 12 and 13 at 1Hz and 2Hz respectively.
/*
void task1(void *p)
{
	while(1)
	{
		digitalWrite(12, HIGH);
		vTaskDelay(1000); // Delay for 500 ticks. Since each tick is 1ms,
						 // this delays for 500ms.
		digitalWrite(12, LOW);
		vTaskDelay(1000);
	}
}

void task2(void *p)
{
	while(1)
	{
		digitalWrite(13, HIGH);
		vTaskDelay(1000);
		digitalWrite(13, LOW);
		vTaskDelay(1000);
	}
} 
*/
// xSemaphoreHandle sonarSema, magnetoSema, gyroSema, acceSema, analogSema = 0;
int echo_1 = 3; //pin 3 for sonar echo
int trigger_1 = 4; //pin 4 for sonar trigger
int analog_1 = A0; 
int numOfData = 9;
LSM303 compass;
L3G gyro;
SharpIR sharp(A0, 25, 93, 20150);
int data[10];
/*
index 1 for sonar
index 2 for acc.x
index 3 for acc.y
index 4 for acc.z
index 5 for gyro.x
index 6 for gyro.y
index 7 for gyro.z
index 8 for analog distance sensor
index 9 for compass heading
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
			//Serial.print(numOfData);
			//Serial.print('\r');
			for(i = 1; i < 10; i++) {
				Serial.println(data[i]);
				Serial.print('\r');
			}
			Serial.println(freeRAM());
			canRead = '0';
		}
		vTaskDelay(1000);
	}
	/*while(1) {
		dprintf("Sonar: %d Acc.x: %d Acc.y: %d Acc.z: %d Gyro.x: %d Gyro.y: %d Gyro.z: %d AnalogD: %d", data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]);
		vTaskDelay(5000);
	}*/
}

void taskReadInfrared(void *p)
{
	int distance;
	while(1) {
		//if(xSemaphoreTake(analogSema, portMAX_DELAY)) {
			distance = sharp.distance();
			data[8] = distance;
			//xSemaphoreGive(gyroSema);
			vTaskDelay(1000);
		//}
	}
}

void taskReadSonar(void *p)
{
	int cm, duration;
	while(1) {
		//if(xSemaphoreTake(sonarSema, portMAX_DELAY)) {
			vTaskSuspendAll();
			digitalWrite(trigger_1, LOW);
			delayMicroseconds(5);
			digitalWrite(trigger_1, HIGH);
			delayMicroseconds(10);
			digitalWrite(trigger_1, LOW);
			pinMode(echo_1, INPUT);
			duration = (int)pulseIn(echo_1, HIGH);
			cm = (int)((duration/2) / 29.1);
			data[1] = cm;
			xTaskResumeAll();
			//xSemaphoreGive(analogSema);
			vTaskDelay(5000);
		//}
	}
}

void taskReadAcc(void *p) 
{
	int accX, accY, accZ;
	while(1){
		//if(xSemaphoreTake(acceSema, portMAX_DELAY)) {
			compass.read();
			accX = (int)((float)compass.a.x / 1000.000 * 61 * 0.001 * 9.8);
			accY = (int)((float)compass.a.y / 1000.000 * 61 * 0.001 * 9.8);
			accZ = (int)((float)compass.a.z / 1000.000 * 61 * 0.001 * 9.8);
			data[2] = accX;
			data[3] = accY;
			data[4] = accZ;
		//	xSemaphoreGive(sonarSema);
			vTaskDelay(1000);
		//}
	}
}

void taskReadGyro(void *p)
{
	int gyroX, gyroY, gyroZ;
	while(1){
		//if(xSemaphoreTake(gyroSema, portMAX_DELAY)) {
			gyro.read();
	
			gyroX = (int)((float)gyro.g.x * 8.75 /1000.00);
			gyroY = (int)((float)gyro.g.y * 8.75 /1000.00);
			gyroZ = (int)((float)gyro.g.z * 8.75 /1000.00);
		
			data[5] = gyroX;
			data[6] = gyroY;
			data[7] = gyroZ;
			//xSemaphoreGive(acceSema);
			vTaskDelay(1000);
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
			data[9] = heading;
			xTaskResumeAll();
		//	xSemaphoreGive(sonarSema);
			vTaskDelay(5000);
		//}
	}
}

void vApplicationIdleHook()
{
	// Do nothing.
}

void setup(void) 
{
	/*vSemaphoreCreateBinary(sonarSema);
	vSemaphoreCreateBinary(acceSema);
	vSemaphoreCreateBinary(magnetoSema);
	vSemaphoreCreateBinary(gyroSema);
	vSemaphoreCreateBinary(analogSema);
	xSemaphoreGive(gyroSema);*/
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
	xTaskCreate(taskReadInfrared, "Read Infrared", STACK_DEPTH, NULL, 7, &t4);
	xTaskCreate(taskReadMagneto, "Read Magneto", STACK_DEPTH, NULL, 6, &t5);
	xTaskCreate(taskReadSonar, "Read Ultrasonic", STACK_DEPTH, NULL, 5, &t6);
	vTaskStartScheduler();
}
