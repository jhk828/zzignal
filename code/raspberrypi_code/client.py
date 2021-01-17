import socket
import time
import threading
import RPi.GPIO as GPIO
from imutils.video import VideoStream
import imagezmq
import paho.mqtt.client as mqtt
import pigpio

from time import sleep

### 실행전 sudo pigpiod 꼭 실행하기
### 그리고 끄기전 꼭 sudo killall pigpiod 실행하기

count = 0
ms = 0
pi = pigpio.pi()
nowAngle = 75
pi.set_servo_pulsewidth(18, 1350)
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("hand") #구독 "nodemcu"

def on_message(client, userdata, message):
  global nowAngle
  global count
  global ms
  point = float(str(message.payload.decode("utf-8")))
  print(point)
  if int(point) > 65:
    nowAngle += 2
  elif int(point) < 35:
    nowAngle -= 2
  set_servo_pos()
  count = 0
  ms = 0

def start_timer():
    global count
    global ms 
    ms += 1
    count = ms / 10
    if(count%1 == 0):
        print(count)
    timer = threading.Timer(0.1,start_timer)
    timer.start()

    if(count>10):
        print("no MAN")
        serching_man()
        
def serching_man():
    global count
    global nowAngle
    if (int(count/10))%2 == 1:
        nowAngle = 150/100*(ms%100 + 1) 
    else:
        nowAngle = 150/100*(100-(ms%100 + 1)) 
    set_servo_pos()
    
def set_servo_pos():
  global nowAngle
  if nowAngle > 150:
    nowAngle = 150
  elif nowAngle < 0:
    nowAngle = 0

  #각도(degree)를 duty로 변경
  duty = 600 + (nowAngle*10)
  # duty 값 출력
  print("Degree: {} to {}(Duty)".format(nowAngle, duty))

  #변경된 duty값을 서보 pwm에 적용
  pi.set_servo_pulsewidth(18, duty)

client = mqtt.Client() #client A 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정
client.connect("ip주소", 1883, 60) #학원

client.loop_stop()
start_timer()
while True:  # send images as stream until Ctrl-C
  client.loop_start()
