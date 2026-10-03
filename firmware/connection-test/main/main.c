#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// DS18B20 1-Wire bus (not used yet)
#define DS18B20_GPIO 4

void app_main(void)
{
    while (1) {
        printf("ESP32 alive\n");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
