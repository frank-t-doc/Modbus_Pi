#!/usr/bin/env python3

import struct
import json
import paho.mqtt.client as mqtt

# MQTT
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "smartmeter/dtsu666/raw"

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)


def decode_frame(frame_hex, start_register=0x2012):

    frame = bytes.fromhex(frame_hex)

    slave = frame[0]
    function = frame[1]
    byte_count = frame[2]

    data = frame[3:3 + byte_count]

    payload = {
        "slave": slave,
        "function": function,
        "registers": {}
    }

    regs = []

    for i in range(0, len(data), 2):
        reg = struct.unpack(">H", data[i:i + 2])[0]
        regs.append(reg)

    for i in range(0, len(regs), 2):

        if i + 1 >= len(regs):
            break

        addr = start_register + i

        raw = struct.pack(">HH",
                          regs[i],
                          regs[i + 1])

        float_val = struct.unpack(">f", raw)[0]

        payload["registers"][f"0x{addr:04X}"] = float_val

    return payload


# Beispiel
frame = "040310461c8c0044b02000455cf000459e9000f8c2"

result = decode_frame(frame)

print(json.dumps(result, indent=2))

mqtt_client.publish(
    MQTT_TOPIC,
    json.dumps(result),
    retain=False
)

mqtt_client.disconnect()