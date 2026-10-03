# Hardware

## Components

| Item | Notes |
|------|-------|
| ESP32 dev board | USB serial for flash/monitor |
| DS18B20 sensor(s) | 1-Wire, unique 64-bit ROM address each |
| 4.7 kΩ resistor | Pull-up from DATA to 3.3 V |
| TP520 (HP t520) | Linux receiver host (`homeberlandia`) |

## Wiring

All sensors share one 1-Wire bus:

```
ESP32 3.3V ──┬── DS18B20 VDD (red)
             └── 4.7kΩ ── DATA line

ESP32 GND  ────── DS18B20 GND (black)
ESP32 GPIO4 ───── DS18B20 DATA (yellow/white)
```

- **GPIO 4** is the data pin (configured in firmware).
- Use short leads for bench testing; parasitic power is not used (VDD connected).
- Each sensor appears as a unique hex ID in serial logs and API payloads.

## Sensor IDs

On boot the firmware scans the bus and logs every discovered address, for example:

```
DS18B20 devices found: 2
  [0] 28FF1234567890AB
  [1] 28FFABCDEF012345
```

Copy these IDs into `config/node.example.json` labels if you want a human-readable map.
