import RPi.GPIO as GPIO
import time
import json
import paho.mqtt.client as mqtt
import adafruit_dht
import psutil

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

MQTT_PUB_TOPIC = "mobile/gmnt2580/sensing"
MQTT_SUB_TOPIC = "mobile/gmnt2580/light"

client = mqtt.Client()

client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
time_stamp = time.time()

BUTTON = 24
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

gpio_pin = 12
GPIO.setup(gpio_pin, GPIO.OUT)


scale = [220, 293.6648, 329.6276, 440, 293.6648, 329.6276, 493.8833]
list = [0, 1, 2, 3, 4, 5, 6]
term = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.5]

TRIG = 13
ECHO = 19
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
time_stamp2 = time.time()

def my_callback(channel):
    print("ready")
    global time_stamp
    time_now = time.time()
    if (time_now - time_stamp) >= 0.3:
        p = GPIO.PWM(gpio_pin, 100)
        p.start(100)
        p.ChangeDutyCycle(90)

        for i in range(28):
            num = i % 7
            p.ChangeFrequency(scale[list[num]])
            time.sleep(term[num])

        p.stop()

def my_callback2():
    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17000
    distance = round(distance, 2)

    print("Distance: ", distance, "cm")
    
    client.publish(MQTT_PUB_TOPIC, distance)
    
    
    if distance <= 10:
        print("henshin!")
        global time_stamp2
        time_now = time.time()
        if (time_now - time_stamp2) >= 0.3:
            p = GPIO.PWM(gpio_pin, 100)
            p.start(100)
            p.ChangeDutyCycle(90)

            scale2 = [440, 1, 440, 1, 440, 220]
            list2 = [0, 1, 2, 3, 4, 5]
            term2 = [0.4, 0.1, 0.3, 0.1, 0.2, 0.1]

            for i in range(6):
                p.ChangeFrequency(scale2[list2[i]])
                time.sleep(term2[i])

            p.stop()
            
            

GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=my_callback)

try:
    while True:
        my_callback2()

except KeyboardInterrupt:
    print("I'm done!")

finally:
    GPIO.cleanup()
