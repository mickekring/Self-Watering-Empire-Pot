import RPi.GPIO as GPIO
import time, random, math, threading, datetime, locale, os, sys
from gtts import gTTS
from gpiozero import CPUTemperature
import Adafruit_DHT
from time import strftime
from time import sleep
from multiprocessing import Process
import threading
from threading import Thread
import urllib
import yaml
import paramiko
import tweepy

locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')

### GPIO and VARIABLES for input/outpus on the Raspberry Pi ###

# Relay
relay = 17

# Hygro
hygro = 23
hygro_Power = 24

# Led Diods
blue_one_pin = 27
blue_two_pin = 22
blue_three_pin = 5
green_one_pin = 6
green_two_pin = 26
red_one_pin = 25
red_two_pin = 16

# GPIO Set mode to BCM instead of Board
GPIO.setmode(GPIO.BCM)

# GPIO input output
GPIO.setup(blue_one_pin, GPIO.OUT)
GPIO.setup(blue_two_pin, GPIO.OUT)
GPIO.setup(blue_three_pin, GPIO.OUT)
GPIO.setup(green_one_pin, GPIO.OUT)
GPIO.setup(green_two_pin, GPIO.OUT)
GPIO.setup(red_one_pin, GPIO.OUT)
GPIO.setup(red_two_pin, GPIO.OUT)

# Led PWM - Pulse width modulation - for pulsating lights
blue_one = GPIO.PWM(blue_one_pin, 100)
blue_two = GPIO.PWM(blue_two_pin, 100)
blue_three = GPIO.PWM(blue_three_pin, 100)
green_one = GPIO.PWM(green_one_pin, 100)
green_two = GPIO.PWM(green_two_pin, 100)
red_one = GPIO.PWM(red_one_pin, 100)
red_two = GPIO.PWM(red_two_pin, 100)

# Sets the diod to start at 0 - which means off
blue_one.start(0)
blue_two.start(0)
blue_three.start(0)
green_one.start(0)
green_two.start(0)
red_one.start(0)
red_two.start(0)

# Hygro reader setup
GPIO.setup(hygro, GPIO.IN)
GPIO.setup(hygro_Power, GPIO.OUT)

# Relay setup
GPIO.setup(relay, GPIO.OUT)

# Variables for logging
cpu = CPUTemperature()

# Misc Variables
pause_time = 0.001
ledSwitch = 0
waterLevel = 0
lastWatered = "No watering since reboot of this program."

############### FUNCTIONS ##################

# Relay
def relay_pump_on():
	GPIO.output(relay, True)

def relay_pump_off():
	GPIO.output(relay, False)

# Water pump system - sets number of seconds that the water will pump. Change time.sleep.
def water_pump():
	relay_pump_on()
	time.sleep(3)
	relay_pump_off()

# Main water pump system function
def water_reading():
	led_off()
	global ledSwitch
	ledSwitch = 1
	global waterLevel
	waterLevel = 0
	global lastWatered
	Thread(target = led_rolling).start()
	try:
		tts = gTTS(text="Alert! Soil moisture levels will we tested in T minus two seconds." , lang='en')
		tts.save("moisture.mp3")
		os.system("mpg321 -q moisture.mp3")
	except:
		os.system("mpg321 -q moisture.mp3")
		pass
	vattenbehov = 0
	GPIO.output(hygro_Power, True)
	time.sleep(1)
	for x in range(1,4):
		vattenbehov += GPIO.input(hygro)
		print(vattenbehov)
		try:
			tts = gTTS(text="Test {0} of three.".format(x) , lang='en')
			tts.save("test.mp3")
			os.system("mpg321 -q test.mp3")
		except:
			pass
		time.sleep(2)
	GPIO.output(hygro_Power, False)
	ledSwitch = 0
	time.sleep(2)
	if vattenbehov <= 1:
		ledSwitch = 1
		waterLevel = 0
		Thread(target = led_green_alert).start()
		try:
			tts = gTTS(text="Code green. We have a code green. All systems stabilized and functioning within normal parameters." , lang='en')
			tts.save("green.mp3")
			os.system("mpg321 -q green.mp3")
		except:
			os.system("mpg321 -q green.mp3")
			pass
		logging()
		ledSwitch = 0
	if vattenbehov > 1:
		ledSwitch = 1
		waterLevel = 50
		lastWatered = (("Status update. The plant was last watered at " + strftime("%H:%M") + ", " + strftime("%A, %B %d" + ".")))
		Thread(target = led_red_alert).start()
		try:
			tts = gTTS(text="Code red. We have a code red. Watering protocols will now engage." , lang='en')
			tts.save("red.mp3")
			os.system("mpg321 -q red.mp3")
		except:
			os.system("mpg321 -q red.mp3")
			pass
		time.sleep(1)
		try:
			tts = gTTS(text="Alert! Water pump engaging." , lang='en')
			tts.save("water.mp3")
			os.system("mpg321 -q water.mp3")
		except:
			os.system("mpg321 -q water.mp3")
			pass
		water_pump()
		time.sleep(10)
		logging()
		try:
			tts = gTTS(text="Moisture levels will now be re-tested by secondary systems." , lang='en')
			tts.save("retest.mp3")
			os.system("mpg321 -q retest.mp3")
		except:
			os.system("mpg321 -q retest.mp3")
			pass
		ledSwitch = 0
		time.sleep(2)
		water_reading()
	time.sleep(1)
	led_off()

# LED lights
def led_all_on():
	led_off()
	blue_one.ChangeDutyCycle(10)
	blue_two.ChangeDutyCycle(10)
	blue_three.ChangeDutyCycle(10)
	green_one.ChangeDutyCycle(10)
	green_two.ChangeDutyCycle(10)
	red_one.ChangeDutyCycle(10)
	red_two.ChangeDutyCycle(10)

def led_red():
	led_off()
	red_one.ChangeDutyCycle(100)
	red_two.ChangeDutyCycle(100)

def led_green():
	led_off()
	green_one.ChangeDutyCycle(100)
	green_two.ChangeDutyCycle(100)

def led_blue():
	led_off()
	blue_one.ChangeDutyCycle(100)
	blue_two.ChangeDutyCycle(100)
	blue_three.ChangeDutyCycle(100)

def led_off():
	blue_one.ChangeDutyCycle(0)
	blue_two.ChangeDutyCycle(0)
	blue_three.ChangeDutyCycle(0)
	green_one.ChangeDutyCycle(0)
	green_two.ChangeDutyCycle(0)
	red_one.ChangeDutyCycle(0)
	red_two.ChangeDutyCycle(0)

def led_red_alert():
	led_off()
	try:
		while True:
			if ledSwitch == 1:
				for i in range(0, 101):
					red_one.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(0, 101):
					red_two.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					red_one.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					red_two.ChangeDutyCycle(i)
					sleep(pause_time)
			else:
				break

	except KeyboardInterrupt:
		led_off()

def led_green_alert():
	led_off()
	try:
		while True:
			if ledSwitch == 1:
				for i in range(0, 101):
					green_one.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(0, 101):
					green_two.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					green_one.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					green_two.ChangeDutyCycle(i)
					sleep(pause_time)
			else:
				break

	except KeyboardInterrupt:
		led_off()

# Blue leds rolling
def led_rolling():
	led_off()
	try:
		while True:
			if ledSwitch == 1:
				for i in range(0, 101):
					blue_one.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(0, 101):
					blue_three.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(0, 101):
					blue_two.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					blue_one.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					blue_three.ChangeDutyCycle(i)
					sleep(pause_time)
				for i in range(100, -1, -1):
					blue_two.ChangeDutyCycle(i)
					sleep(pause_time)
			else:
				break

	except KeyboardInterrupt:
		led_off()

# Temp and humidity
def temp_humidity():
	humidity, temperature = Adafruit_DHT.read_retry(11, 4)
	global tweetMessage
	tweetMessage = "Temperature: {0:0.1f} C  Humidity: {1:0.1f} %".format(temperature, humidity)
	print("Tweeting: " + tweetMessage)
	tweet()

# Logging of statistics
def logging():
	humidity, temperature = Adafruit_DHT.read_retry(11, 4)
	with open("stats.csv", "a") as log:
		log.write("\n{0},{1},{2},{3}".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature),str(humidity),str(waterLevel)))
	fileupload_stats()

# Status update with diagnostics
def self_diagnostics():
	global ledSwitch
	ledSwitch = 1
	Thread(target = led_rolling).start()
	humidity, temperature = Adafruit_DHT.read_retry(11, 4)
	temp = cpu.temperature
	try:
		tts = gTTS(text="Self diagnostics. My CPU runs at {0:0.0f} degrees celsius. Environmental temperature is {1:0.0f} degrees celsius with a relative humidity of {2:0.0f} percent.".format(temp, temperature, humidity) , lang='en')
		tts.save("diagnostics.mp3")
		os.system("mpg321 -q diagnostics.mp3")
	except:
		print("Internet error.")
		internet_on()
		pass
	ledSwitch = 0
	time.sleep(1)
	internet_on()

# Displaying last time plant was watered
def water_log():
	print("Status update. The plant was last watered at " + strftime("%H:%M") + ", " + strftime("%A, %B %d" + "."))

# Checking internet connection
def internet_on():
	global ledSwitch
	try:
		urllib.request.urlopen('http://www.google.com')
	except:
		print("No internet connection.")
		ledSwitch = 1
		Thread(target = led_red_alert).start()
		try:
			tts = gTTS(text="Alert! All communications are down. Alert! Systems running in emergency mode. Alert! Restoring communications, priority alpha." , lang='en')
			tts.save("internet_off.mp3")
			os.system("mpg321 -q internet_off.mp3")
		except:
			os.system("mpg321 -q internet_off.mp3")
			pass
		ledSwitch = 0
		pass
	else:
		print("We have an internet connection.")
		ledSwitch = 1
		Thread(target = led_green_alert).start()
		try:
			tts = gTTS(text="Code green! All communications systems working within normal parameters." , lang='en')
			tts.save("internet_on.mp3")
			os.system("mpg321 -q internet_on.mp3")
		except:
			os.system("mpg321 -q internet_on.mp3")
			pass
		ledSwitch = 0

# FILE UPLOADS

# Init files upload
def fileupload_init():
	try:
		conf = yaml.load(open('credentials.yml'))
		host = conf['user']['host']
		port = conf['user']['port']
		transport = paramiko.Transport((host, port))

		password = conf['user']['password']
		username = conf['user']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir("/var/www/bloggmu/public/rum/blomma")
		filepath = "stats.csv"
		localpath = "/home/pi/kod/empirepot/stats.csv"
		filepath2 = "index.html"
		localpath2 = "/home/pi/kod/empirepot/index.html"

		sftp.put(localpath, filepath)
		sftp.put(localpath2, filepath2)

		sftp.close()
		transport.close()
		print("Init files have been uploaded.")
	except:
		global ledSwitch
		print("Warning. Initial files error uploading.")
		ledSwitch = 1
		Thread(target = led_red_alert).start()
		tts = gTTS(text="Warning. Initial files error uploading." , lang='en')
		tts.save("upload_init_error.mp3")
		os.system("mpg321 -q upload_init_error.mp3")
		ledSwitch = 0
		internet_on()
		pass

# Stat file upload
def fileupload_stats():
	try:
		conf = yaml.load(open('credentials.yml'))
		host = conf['user']['host']
		port = conf['user']['port']
		transport = paramiko.Transport((host, port))

		password = conf['user']['password']
		username = conf['user']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir("/var/www/bloggmu/public/rum/blomma")
		filepath = "stats.csv"
		localpath = "/home/pi/kod/empirepot/stats.csv"

		sftp.put(localpath, filepath)

		sftp.close()
		transport.close()
		print("Stat file has been uploaded.")
	except:
		global ledSwitch
		print("Warning. Stat file error uploading.")
		ledSwitch = 1
		Thread(target = led_red_alert).start()
		tts = gTTS(text="Warning. Stat file error uploading." , lang='en')
		tts.save("upload_error.mp3")
		os.system("mpg321 -q upload_error.mp3")
		ledSwitch = 0
		internet_on()
		pass

# COMMUNICATIONS

# Twitter

def tweet():
	try:
		conf = yaml.load(open('credentials.yml'))

		consumer_key = conf['twitter']['consumer_key']
		consumer_secret = conf['twitter']['consumer_secret']
		access_token = conf['twitter']['access_token']
		access_token_secret = conf['twitter']['access_token_secret']

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)

		api.update_status(status=tweetMessage)
		print("Tweet sent.")
	except:
		global ledSwitch
		print("Warning. Twitter error. Unable to send tweet.")
		ledSwitch = 1
		Thread(target = led_red_alert).start()
		tts = gTTS(text="Warning. Twitter error. Unable to send tweet." , lang='en')
		tts.save("twitter_error.mp3")
		os.system("mpg321 -q twitter_error.mp3")
		ledSwitch = 0
		internet_on()
		pass

def tweet_follow():
	try:
		conf = yaml.load(open('credentials.yml'))

		consumer_key = conf['twitter']['consumer_key']
		consumer_secret = conf['twitter']['consumer_secret']
		access_token = conf['twitter']['access_token']
		access_token_secret = conf['twitter']['access_token_secret']

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)

		for follower in tweepy.Cursor(api.followers).items():
			follower.follow()
		print("Twitter followers followed.")
	except:
		global ledSwitch
		print("Warning. Twitter error. Unable to follow twitter users.")
		ledSwitch = 1
		Thread(target = led_red_alert).start()
		tts = gTTS(text="Warning. Twitter error. Unable to follow twitter users." , lang='en')
		tts.save("twitter_follow_error.mp3")
		os.system("mpg321 -q twitter_follow_error.mp3")
		ledSwitch = 0
		internet_on()
		pass

#################### MAIN PROGRRAM #################################

def Main():
	try:
		button_delay = 0.2
		led_off()
		GPIO.output(hygro_Power, False)
		relay_pump_off()
		while True:
			print("\n--- TESTPROGRAM ---\n")
			print("1. Alla lampor på\n")
			print("2. Alla lampor av\n")
			print("3. Fuktmätning\n")
			print("4. Relay Test\n")
			print("5. Status\n")
			print("6. Temp Moisture\n")
			print("7. Internet Connection\n")
			print("8. Hygro on\n")
			print("9. Hygro off\n")
			print("10. Logging and upload\n")
			print("11. Upload init\n")
			print("12. Tweet follow\n")
			val = input("\n>>> ")
			if val == "1":
				time.sleep(button_delay)
				print("\n### ALLA LAMPOR PÅ###\n")
				led_all_on()
			if val == "2":
				time.sleep(button_delay)
				print("\n### ALLA LAMPOR AV ###\n")
				led_off()
			if val == "3":
				water_reading()
			if val == "4":
				relay_pump_on()
				time.sleep(2)
				relay_pump_off()
			if val == "5":
				self_diagnostics()
			if val == "6":
				temp_humidity()
			if val =="7":
				internet_on()
			if val =="8":
				GPIO.output(hygro_Power, True)
				vattenbehov = GPIO.input(hygro)
				print(vattenbehov)
				print(lastWatered)
			if val =="9":
				GPIO.output(hygro_Power, False)
			if val =="10":
				logging()
			if val =="11":
				fileupload_init()
			if val =="12":
				tweet_follow()

	finally:
		print("GPIO Clean up")
		GPIO.cleanup()

if __name__ == "__main__":
	Main()