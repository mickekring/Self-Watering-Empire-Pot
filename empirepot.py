import RPi.GPIO as GPIO
import time, random, math, threading, datetime, locale, os, sys, Adafruit_DHT, urllib, yaml, paramiko, tweepy, requests, alsaaudio
from gtts import gTTS
from gpiozero import CPUTemperature
from time import strftime
from time import sleep
from threading import Thread
from twilio.rest import Client

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
blue_on_off_pin = 18

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
GPIO.setup(blue_on_off_pin, GPIO.OUT)

# Led PWM - Pulse width modulation - for pulsating lights
blue_one = GPIO.PWM(blue_one_pin, 100)
blue_two = GPIO.PWM(blue_two_pin, 100)
blue_three = GPIO.PWM(blue_three_pin, 100)
green_one = GPIO.PWM(green_one_pin, 100)
green_two = GPIO.PWM(green_two_pin, 100)
red_one = GPIO.PWM(red_one_pin, 100)
red_two = GPIO.PWM(red_two_pin, 100)
blue_on_off = GPIO.PWM(blue_on_off_pin, 100)

# Sets the diod to start at 0 - which means off
blue_one.start(0)
blue_two.start(0)
blue_three.start(0)
green_one.start(0)
green_two.start(0)
red_one.start(0)
red_two.start(0)
blue_on_off.start(0)

# Hygro reader setup
GPIO.setup(hygro, GPIO.IN)
GPIO.setup(hygro_Power, GPIO.OUT)

# Relay setup
GPIO.setup(relay, GPIO.OUT)

# Variables for logging
cpu = CPUTemperature()

# Misc Variables
pause_time = 0.001 # PWM 
ledSwitch = 0 # 1 or 0 used for rolling leds on or off
powerSwitch = 0 # use 0 for steady light and 1 for flashing
waterLevel = 0 # Used for stats logging to csv to show 0 if no watering och 100 if watered
tankFull = 10 # Number of times the pot can be watered with full tank

connected = 1 # Indicator regarding internet connection

# Fail safe
todaysDate = strftime("%d") # Sets todays date for comparison
timesWateredToday = 0 # Number of times pot has been watered today
waterError = 0 # Used as bolean if pot has been watered
# / Fail safe

# Stores and opens date/time when last watered
f = open('lastwatered.txt','r') # Opens external file for logging last watered date
lastWatered = (f.read()) # Sets variable for use displaying status
f.close() # Closes file

# Loading credentials
conf = yaml.load(open("credentials.yml")) # External file with all credentials

### FUNCTIONS ###

### LED lights

# All leds on
def led_all_on():
	led_off()
	blue_one.ChangeDutyCycle(15)
	blue_two.ChangeDutyCycle(15)
	blue_three.ChangeDutyCycle(15)
	green_one.ChangeDutyCycle(15)
	green_two.ChangeDutyCycle(15)
	red_one.ChangeDutyCycle(15)
	red_two.ChangeDutyCycle(15)

# Red leds on
def led_red():
	led_off()
	red_one.ChangeDutyCycle(100)
	red_two.ChangeDutyCycle(100)

# Green leds on
def led_green():
	led_off()
	green_one.ChangeDutyCycle(100)
	green_two.ChangeDutyCycle(100)

# Blue leds on
def led_blue():
	led_off()
	blue_one.ChangeDutyCycle(100)
	blue_two.ChangeDutyCycle(100)
	blue_three.ChangeDutyCycle(100)

def led_power():
	blue_on_off.ChangeDutyCycle(80)

def led_power_alert():
	try:
		while True:
			if powerSwitch == 1:
					blue_on_off.ChangeDutyCycle(0)
					time.sleep(1)
					blue_on_off.ChangeDutyCycle(80)
					time.sleep(1)
			elif powerSwitch == 0:
				blue_on_off.ChangeDutyCycle(80)
			else:
				break

	except KeyboardInterrupt:
		led_off()

# All leds off
def led_off():
	blue_one.ChangeDutyCycle(0)
	blue_two.ChangeDutyCycle(0)
	blue_three.ChangeDutyCycle(0)
	green_one.ChangeDutyCycle(0)
	green_two.ChangeDutyCycle(0)
	red_one.ChangeDutyCycle(0)
	red_two.ChangeDutyCycle(0)

# Red leds rolling lights
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

# Green leds rolling lights
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

# Blue leds rolling lights
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

# Water pump system - sets number of seconds of relay that controls the water will pump
def water_pump():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Alert,Relay on".format(strftime("%Y-%m-%d %H:%M:%S")))
	GPIO.output(relay, True)
	time.sleep(3)
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Alert,Relay off".format(strftime("%Y-%m-%d %H:%M:%S")))
	GPIO.output(relay, False)

### Main water pump system function #############

def water_reading():
	led_off()
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Soil moisture reading started.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	global dateNow
	global todaysDate
	global timesWateredToday
	global ledSwitch
	global lastWatered
	global tankFull
	global waterError
	global waterLevel
	global powerSwitch

	waterLevel = 0
	dateNow = strftime("%d")
	ledSwitch = 1
	
	Thread(target = led_rolling).start()

	os.system("mpg321 -q emp_march_top.mp3")
	
	try:
		powerSwitch = 0
		tts = gTTS(text="Alert! Testing soil moisture levels in T minus two seconds." , lang='en')
		tts.save("moisture.mp3")
		os.system("mpg321 -q moisture.mp3")
	except:
		powerSwitch = 1
		os.system("mpg321 -q moisture_backup.mp3")
		pass
	
	GPIO.output(hygro_Power, True)
	time.sleep(1)
	
	waterNeed = 0

	for x in range(1,4):
		waterNeed += GPIO.input(hygro)
		try:
			powerSwitch = 0
			tts = gTTS(text="Test {0} of three.".format(x) , lang='en')
			tts.save("test.mp3")
			os.system("mpg321 -q test.mp3")
		except:
			powerSwitch = 1
			os.system("mpg321 -q test_backup.mp3")
			pass
		time.sleep(2)

	GPIO.output(hygro_Power, False)
	ledSwitch = 0
	time.sleep(2)

	if waterNeed <= 1:
		ledSwitch = 1
		waterLevel = 0

		Thread(target = led_green_alert).start()
		
		with open("error_log.csv", "a") as error_log:
				error_log.write("\n{0},Log,Moisture levels are normal".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		try:
			powerSwitch = 0
			tts = gTTS(text="Code green. Moisture levels are acceptable. All systems are functioning within normal parameters." , lang='en')
			tts.save("green.mp3")
			os.system("mpg321 -q green.mp3")
		except:
			powerSwitch = 1
			os.system("mpg321 -q green_backup.mp3")
			pass

		ledSwitch = 0
		time.sleep(2)

		logging()

	elif waterNeed > 1:
		if dateNow == todaysDate:
			if timesWateredToday < 2:
				ledSwitch = 1
				waterLevel = 100
				timesWateredToday += 1

				Thread(target = led_red_alert).start()
				
				try:
					powerSwitch = 0
					tts = gTTS(text="Alert. Code red. Watering protocols will now engage." , lang='en')
					tts.save("red.mp3")
					os.system("mpg321 -q red.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q red_backup.mp3")
					pass
				time.sleep(1)

				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Alert,Water pump engaging.".format(strftime("%Y-%m-%d %H:%M:%S")))
				try:
					powerSwitch = 0
					tts = gTTS(text="Water pump engaging." , lang='en')
					tts.save("water.mp3")
					os.system("mpg321 -q water.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q water_backup.mp3")
					pass
				
				water_pump()
				tankFull -= 1
				
				if tankFull < 3:
					sms_tank_warning()
					ledSwitch = 1
					
					Thread(target = led_red_alert).start()
					
					try:
						powerSwitch = 1
						tts = gTTS(text="Alert. Code red. Water tank is almost depleted. Refill. Priority alpha. Sending SMS" , lang='en')
						tts.save("tankempty.mp3")
						os.system("mpg321 -q tankempty.mp3")
					except:
						powerSwitch = 1
						os.system("mpg321 -q tankempty_backup.mp3")
						pass
					
					ledSwitch = 0
					time.sleep(2)
				
				else:
					pass
				
				lastWatered = (("Status update. The plant was succesfully watered at " + strftime("%H:%M") + ", " + strftime("%A, %B %d" + ".")))
				f = open('lastwatered.txt', 'w')
				f.write(lastWatered)
				f.close()
				
				time.sleep(10)

				logging()
				
				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Log,Moisture levels will now be re-tested".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				try:
					powerSwitch = 0
					tts = gTTS(text="Alert. Moisture levels will now be re-tested by secondary systems." , lang='en')
					tts.save("retest.mp3")
					os.system("mpg321 -q retest.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q retest_backup.mp3")
					pass
				
				ledSwitch = 0
				time.sleep(2)
				
				water_reading()
			
			elif waterError == 0 and timesWateredToday > 1:
				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Error,Moisture sensor problems.".format(strftime("%Y-%m-%d %H:%M:%S")))

				ledSwitch = 1
				
				Thread(target = led_red_alert).start()
				
				try:
					powerSwitch = 1
					tts = gTTS(text="Error. Moisture sensors may be corrupted. Please check. Aborting watering protocols for now. Sending SMS." , lang='en')
					tts.save("sensors.mp3")
					os.system("mpg321 -q sensors.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q sensors_backup.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
					pass
				
				sms_moisture_warning()
				
				ledSwitch = 0
				waterError = 1
				waterLevel = 0

				time.sleep(2)
				
				logging()
				
			elif waterError == 1 and timesWateredToday > 1:
				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Log,Moisture sensor skipped.".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				ledSwitch = 1
				
				Thread(target = led_red_alert).start()
				
				try:
					powerSwitch = 1
					tts = gTTS(text="Alert. Moisture sensors may be corrupted. Please check. Aborting watering protocols for now." , lang='en')
					tts.save("sensors.mp3")
					os.system("mpg321 -q sensors.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q sensors_backup.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
					pass
				
				ledSwitch = 0
				waterLevel = 0

				time.sleep(2)
				
				logging()
		
		elif dateNow != todaysDate:
			timesWateredToday = 0
			waterError = 0
			todaysDate = strftime("%d")
			logging()
			water_reading()

	time.sleep(2)
	led_off()

# Temp and humidity

def temp_humidity():
	global powerSwitch

	try:
		powerSwitch = 0
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Reading temp and humidity".format(strftime("%Y-%m-%d %H:%M:%S")))

		humidity, temperature = Adafruit_DHT.read_retry(11, 4)
		
		r = requests.get(conf['openweather']['api'])
		json_object = r.json()
		temp_k = json_object["main"]["temp"]
		temp_c = (temp_k - 273.15)
		o_humidity = json_object["main"]["humidity"]
		w_text = json_object["weather"][0]["main"]
		w_desc = json_object["weather"][0]["description"]
		
		global tweetMessage
		
		tweetMessage = "Plant Pot Stats\n\nCity: Stockholm, SWE\nTime: {2}\n\nIndoors temp: {0:0.0f}°C\nIndoors humidity: {1:0.0f}%\n\nOutside temp: {3:0.0f}°C\nOutside humidity: {4}%\nOutside weather: {5} | {6}".format(temperature, humidity, strftime("%H:%M"), temp_c, o_humidity, w_text, w_desc)
	
	except:
		powerSwitch = 1
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed reading temp and humidity".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

### Logging of statistics

def logging():
	global powerSwitch
	
	with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Gathering stats for logging.".format(strftime("%Y-%m-%d %H:%M:%S")))

	humidity, temperature = Adafruit_DHT.read_retry(11, 4)
		
	try:
		powerSwitch = 0
		r = requests.get(conf['openweather']['api'])
		json_object = r.json()
		temp_k = json_object["main"]["temp"]
		temp_c = (temp_k - 273.15)
		o_humidity = json_object["main"]["humidity"]
		with open("stats.csv", "a") as log:
			log.write("\n{0},{1},{2},{3},{4:0.0f},{5}".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature),str(humidity),str(waterLevel),(temp_c),str(o_humidity)))
	except:
		powerSwitch = 1
		temp_c = ""
		o_humidity = ""
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Could not connect to openweather API.".format(strftime("%Y-%m-%d %H:%M:%S")))
		with open("stats.csv", "a") as log:
			log.write("\n{0},{1},{2},{3},{4},{5}".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature),str(humidity),str(waterLevel),str(temp_c),str(o_humidity)))
		pass
	
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Stats gathered. Sending stats to upload.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	fileupload_stats()

### Status update with diagnostics

def self_diagnostics():
	led_off()
	
	global powerSwitch
	global ledSwitch
	
	ledSwitch = 1
	
	Thread(target = led_rolling).start()
	
	try:
		powerSwitch = 0
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Diagnostics start up sequence".format(strftime("%Y-%m-%d %H:%M:%S")))
		tts = gTTS(text="Alert. Empire plant pot online. Self diagnostics start up sequence initiated. Checking ligths." , lang='en')
		tts.save("diagnostics_lights.mp3")
		os.system("mpg321 -q diagnostics_lights.mp3")
	except:
		powerSwitch = 1
		with open("error_log.csv", "a") as error_log:
			error_log.write("Error: Internet error.".format(strftime("%Y-%m-%d %H:%M:%S")))
		os.system("mpg321 -q diagnostics_lights_backup.mp3")
		pass
	
	ledSwitch = 0
	time.sleep(2)
	led_all_on()
	time.sleep(1)
	led_blue()
	time.sleep(1)
	led_green()
	time.sleep(1)
	led_red()
	time.sleep(1)
	led_off()
	ledSwitch = 1
	
	Thread(target = led_rolling).start()
	
	humidity, temperature = Adafruit_DHT.read_retry(11, 4)
	temp = cpu.temperature
	
	try:
		powerSwitch = 0
		tts = gTTS(text="Self diagnostics. Central core CPU runs at {0:0.0f} degrees celsius. Room temperature is {1:0.0f} degrees celsius with a relative humidity of {2:0.0f} percent.".format(temp, temperature, humidity) , lang='en')
		tts.save("diagnostics.mp3")
		os.system("mpg321 -q diagnostics.mp3")
	except:
		powerSwitch = 1
		os.system("mpg321 -q diagnostics_backup.mp3")
		pass
	
	ledSwitch = 0
	time.sleep(2)
	internet_on()

### Checking internet connection

def internet_on():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Testing Internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	global ledSwitch
	global connected
	global powerSwitch
	
	try:
		powerSwitch = 0
		urllib.request.urlopen('http://216.58.207.206')
		#urllib.urlopen('http://216.58.207.206', timeout=4)

		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,We have an internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_green_alert).start()
		
		try:
			powerSwitch = 0
			tts = gTTS(text="Code green! All communication systems are online and working within normal parameters." , lang='en')
			tts.save("internet_on.mp3")
			os.system("mpg321 -q internet_on.mp3")
		except:
			powerSwitch = 1
			os.system("mpg321 -q internet_on_backup.mp3")
			pass

		connected = 1
		ledSwitch = 0
		time.sleep(2)

	except:
		powerSwitch = 1
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,No internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		try:
			powerSwitch = 1
			tts = gTTS(text="Alert! All communications are down. Alert! Systems running in emergency mode. Alert! Restoring communications, priority alpha." , lang='en')
			tts.save("internet_off.mp3")
			os.system("mpg321 -q internet_off.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
		except:
			powerSwitch = 1
			os.system("mpg321 -q internet_off_backup.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
			pass
		
		connected = 0
		ledSwitch = 0
		time.sleep(2)
		pass

def internet_on_thread():
	global powerSwitch
	global ledSwitch
	global connected

	while True:
		time.sleep(180)

		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Testing Internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))

		if connected == 1:
			try:
				powerSwitch = 0
				urllib.request.urlopen('http://216.58.207.206')
				#urllib.urlopen('http://216.58.207.206', timeout=4)

				with open("error_log.csv", "a") as error_log:
					error_log.write("\n{0},Log,We have an internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				connected = 1

			except:
				powerSwitch = 1
				with open("error_log.csv", "a") as error_log:
					error_log.write("\n{0},Error,No internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				ledSwitch = 1
				
				Thread(target = led_red_alert).start()
				
				try:
					powerSwitch = 1
					tts = gTTS(text="Alert! All communications are down. Alert! Systems running in emergency mode. Alert! Restoring communications, priority alpha." , lang='en')
					tts.save("internet_off.mp3")
					os.system("mpg321 -q internet_off.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q internet_off_backup.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
					pass
				
				ledSwitch = 0
				connected = 0
				time.sleep(2)
				pass

		elif connected == 0:
			try:
				powerSwitch = 0
				urllib.request.urlopen('http://216.58.192.142')

				with open("error_log.csv", "a") as error_log:
					error_log.write("\n{0},Log,We have an internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				ledSwitch = 1
				
				Thread(target = led_green_alert).start()
				
				try:
					powerSwitch = 0
					tts = gTTS(text="Code green! All communication systems are online and working within normal parameters." , lang='en')
					tts.save("internet_on.mp3")
					os.system("mpg321 -q internet_on.mp3")
				except:
					powerSwitch = 1
					os.system("mpg321 -q internet_on_backup.mp3")
					pass

				ledSwitch = 0
				connected = 1
				time.sleep(2)

			except:
				powerSwitch = 1
				with open("error_log.csv", "a") as error_log:
					error_log.write("\n{0},Error,No internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				connected = 0
				pass

### FILE UPLOADS

### Init files upload

def fileupload_init():
	global powerSwitch
	global ledSwitch

	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,uploading initial files.".format(strftime("%Y-%m-%d %H:%M:%S")))

	try:
		powerSwitch = 0

		host = conf['user']['host']
		port = conf['user']['port']
		transport = paramiko.Transport((host, port))

		password = conf['user']['password']
		username = conf['user']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir("/var/www/bloggmu/public/rum/blomma")
		filepath = "stats.csv"
		localpath = "/home/pi/kod/empirebot/stats.csv"
		filepath2 = "index.html"
		localpath2 = "/home/pi/kod/empirebot/index.html"

		sftp.put(localpath, filepath)
		sftp.put(localpath2, filepath2)

		sftp.close()
		transport.close()
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Init files have been uploaded.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	except:
		powerSwitch = 1
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Warning. Initial files error uploading".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		try:
			powerSwitch = 1
			tts = gTTS(text="Warning. Error. Initial files could not be uploaded to the Galactic Empire." , lang='en')
			tts.save("upload_init_error.mp3")
			os.system("mpg321 -q upload_init_error.mp3")
		except:
			powerSwitch = 1
			os.system("mpg321 -q upload_init_error_backup.mp3")
			pass
		
		ledSwitch = 0
		time.sleep(2)

		pass

### Stat file upload

def fileupload_stats():
	global powerSwitch
	global ledSwitch

	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Uploading stats".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	try:
		powerSwitch = 0
		host = conf['user']['host']
		port = conf['user']['port']
		transport = paramiko.Transport((host, port))

		password = conf['user']['password']
		username = conf['user']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir("/var/www/bloggmu/public/rum/blomma")
		filepath = "stats.csv"
		localpath = "/home/pi/kod/empirebot/stats.csv"

		filepath2 = "error_log.csv"
		localpath2 = "/home/pi/kod/empirebot/error_log.csv"

		sftp.put(localpath, filepath)
		sftp.put(localpath2, filepath2)

		sftp.close()
		transport.close()
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Stat file has been uploaded".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	except:
		powerSwitch = 1
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Warning. Stat file error uploading".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		try:
			powerSwitch = 1
			tts = gTTS(text="Warning. Error. Stat files could not be uploaded to the Galactic Empire mainframe." , lang='en')
			tts.save("upload_error.mp3")
			os.system("mpg321 -q upload_error.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
		except:
			powerSwitch = 1
			os.system("mpg321 -q upload_error_backup.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
			pass
		
		ledSwitch = 0
		time.sleep(2)
		pass

### Twitter

def tweet_follow():
	consumer_key = conf['twitter']['consumer_key']
	consumer_secret = conf['twitter']['consumer_secret']
	access_token = conf['twitter']['access_token']
	access_token_secret = conf['twitter']['access_token_secret']

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	
	try:
		for follower in tweepy.Cursor(api.followers).items():
			follower.follow()
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Twitter followers followed".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	except:
		global ledSwitch
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Unable to follow twitter users".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		try:
			tts = gTTS(text="Warning. Twitter error. Unable to follow twitter users." , lang='en')
			tts.save("twitter_follow_error.mp3")
			os.system("mpg321 -q twitter_follow_error.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
		except:
			os.system("mpg321 -q twitter_follow_error_backup.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
			pass
		
		ledSwitch = 0
		time.sleep(2)
		pass

def tweet_auto():
	global ledSwitch
	global powerSwitch

	while True:

		consumer_key = conf['twitter']['consumer_key']
		consumer_secret = conf['twitter']['consumer_secret']
		access_token = conf['twitter']['access_token']
		access_token_secret = conf['twitter']['access_token_secret']

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)

		f = open('tweetid.txt','r')
		tweetID = (f.read())
		f.close()

		try:
			powerSwitch = 0
			for status in tweepy.Cursor(api.user_timeline, screen_name="mickekring").items(1):
				tweetTextFetched = (status._json["text"])
				tweetIDFetched = str((status._json["id"]))
		except:
			powerSwitch = 1
			with open("error_log.csv", "a") as error_log:
				error_log.write("\n{0},Error,Reading Twitter timeline failed".format(strftime("%Y-%m-%d %H:%M:%S")))
			pass

		try:
			if tweetIDFetched == tweetID:
				pass
			
			else:
				tweetID = tweetIDFetched
				
				f = open('tweetid.txt', 'w')
				f.write(str(tweetID))
				f.close()
				
				tweetText = tweetTextFetched.lower()
				
				if "@empireplantbot" in tweetText:
					ledSwitch = 1
					
					Thread(target = led_rolling).start()
					
					try:
						powerSwitch = 0
						os.system("mpg321 -q emp_march_top.mp3")
						tts = gTTS(text="Alert. Incoming Tweet. Message recieved... {0}".format(tweetTextFetched) , lang='en')
						tts.save("incoming_tweet.mp3")
						os.system("mpg321 -q incoming_tweet.mp3")
						tts = gTTS(text="Lord Vader. Respond to tweet." , lang='en')
						tts.save("responding_tweet.mp3")
						os.system("mpg321 -q responding_tweet.mp3")
					except:
						powerSwitch = 1
						os.system("mpg321 -q emp_march_top.mp3")
						os.system("mpg321 -q responding_tweet_backup.mp3")
						pass
					
					ledSwitch = 0
					time.sleep(2)
					ledSwitch = 1
					
					Thread(target = led_red_alert).start()
					
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_yes.mp3")
					
					ledSwitch = 0
					time.sleep(2)
					
					with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Alert,Twitter message recieved".format(strftime("%Y-%m-%d %H:%M:%S")))
					
					if "status" in tweetText:
						temp_humidity()
						
						api.update_status(status = ("@mickekring\n" + (tweetMessage) + "\n\n" + lastWatered), in_reply_to_status_id = (tweetIDFetched))
						
						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Status twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					
					elif "who" and "are" in tweetText:
						api.update_status(status = "I am an automated plant pot, @mickekring", in_reply_to_status_id = (tweetIDFetched))
						
						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Who - twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					
					elif "refill" in tweetText:
						tankFull = 10
						
						api.update_status(status = "Water levels are now at full again, @mickekring. ", in_reply_to_status_id = (tweetIDFetched))
						
						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Top up refill twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					
					elif "silence" in tweetText:
						audio_vol_none()
						
						api.update_status(status = "I've set speaker volume to 0%, @mickekring. ", in_reply_to_status_id = (tweetIDFetched))
						
						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Audio silence twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					
					elif "loud" in tweetText:
						audio_vol_full()
						
						api.update_status(status = "I've set speaker volume to 100%, @mickekring. ", in_reply_to_status_id = (tweetIDFetched))
						
						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Audio full twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					
					elif "help" in tweetText:
						
						api.update_status(status = "Commands:\nrefill, silence, loud, status - @mickekring.", in_reply_to_status_id = (tweetIDFetched))
						
						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Help twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					else:
						api.update_status(status = "I'm sorry but I don't understand, @mickekring. Please enhance my software.", in_reply_to_status_id = (tweetIDFetched))

						with open("error_log.csv", "a") as error_log:
							error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
				else:
					pass
		except:
			powerSwitch = 1
			with open("error_log.csv", "a") as error_log:
					error_log.write("\n{0},Error,Could not answer twitter message".format(strftime("%Y-%m-%d %H:%M:%S")))
			pass

		time.sleep(60)

### SMS

def sms_tank_warning():
	global powerSwitch

	try:
		powerSwitch = 0
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Alert,Sending tank warning SMS".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		account_sid = conf["twilio"]["account_sid"]
		auth_token = conf["twilio"]["auth_token"]
		client = Client(account_sid, auth_token)
		message = client.messages.create(
			to= conf["twilio"]["to_phone_number"],
			from_= conf["twilio"]["from_phone_number"],
			body="Alert! You need to refill the water tank. Only " + str(tankFull) + " times left.\n\n" + lastWatered)
	
	except:
		powerSwitch = 1
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed sending tank warning SMS".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

def sms_moisture_warning():
	global powerSwitch

	try:
		powerSwitch = 0
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Alert,Sending moisture sensor warning SMS".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		account_sid = conf["twilio"]["account_sid"]
		auth_token = conf["twilio"]["auth_token"]
		client = Client(account_sid, auth_token)
		message = client.messages.create(
			to= conf["twilio"]["to_phone_number"],
			from_= conf["twilio"]["from_phone_number"],
			body="Warning! It seems to be something wrong with the moisture sensors. Please check.")
	
	except:
		powerSwitch = 1
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed sending moisture sensor warning SMS".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

### Audio controls

def audio_vol_full():
	global powerSwitch

	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Setting audio to 100%.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	m = alsaaudio.Mixer("PCM")
	current_volume = m.getvolume()
	m.setvolume(90)
	global ledSwitch
	ledSwitch = 1
	
	Thread(target = led_red_alert).start()

	try:
		powerSwitch = 0
		tts = gTTS(text="Lord Vader... Set audio levels to full." , lang='en')
		tts.save("audio_full.mp3")
		os.system("mpg321 -q audio_full.mp3")
	except:
		powerSwitch = 1
		os.system("mpg321 -q audio_full_backup.mp3")
		pass
	
	os.system("mpg321 -q vader_yes.mp3")
	
	ledSwitch = 0
	time.sleep(2)

def audio_vol_none():
	global ledSwitch
	global powerSwitch

	ledSwitch = 1
	
	Thread(target = led_red_alert).start()
	
	try:
		powerSwitch = 0
		tts = gTTS(text="Lord Vader... Set audio levels to zero." , lang='en')
		tts.save("audio_zero.mp3")
		os.system("mpg321 -q audio_zero.mp3")
	except:
		powerSwitch = 1
		os.system("mpg321 -q audio_zero_backup.mp3")
		pass
	
	os.system("mpg321 -q vader_breathe.mp3")
	os.system("mpg321 -q vader_yes.mp3")
	
	ledSwitch = 0
	time.sleep(2)
	
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Setting audio to 0%".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	m = alsaaudio.Mixer("PCM")
	current_volume = m.getvolume()
	m.setvolume(0)

def emp_march():
	os.system("mpg321 -q emp_march_lo.mp3")

#################### MAIN PROGRRAM #################################

def Main():
	try:
		t1 = threading.Thread(target = led_power_alert)
		t1.daemon = True
		t1.start()

		t2 = threading.Thread(target = emp_march)
		t2.start()
		
		print("---SYSTEM START UP---")
		
		button_delay = 0.2
		led_off()
		GPIO.output(hygro_Power, False)
		
		audio_vol_full()
		self_diagnostics()
		temp_humidity()
		fileupload_init()
		internet_on()
		
		t3 = threading.Thread(target = tweet_auto)
		t3.daemon = True
		t3.start()

		#t4 = threading.Thread(target = internet_on_thread)
		#t4.daemon = True
		#t4.start()
		
		while True:
			tweet_follow()
			water_reading()
			time.sleep(1800)

	except:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Main program ended".format(strftime("%Y-%m-%d %H:%M:%S")))

	finally:
		print("GPIO Clean up")
		GPIO.cleanup()

if __name__ == "__main__":
	Main()