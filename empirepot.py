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
tankFull = 10

# Fail safe
todaysDate = strftime("%d")
timesWateredToday = 0
waterError = 0
# / Fail safe

# Stores and opens date/time when last watered
f = open('lastwatered.txt','r')
lastWatered = (f.read())
f.close()

# Loading credentials
conf = yaml.load(open("credentials.yml"))

### FUNCTIONS ###

### LED lights

# All leds on
def led_all_on():
	led_off()
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,All leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
	blue_one.ChangeDutyCycle(10)
	blue_two.ChangeDutyCycle(10)
	blue_three.ChangeDutyCycle(10)
	green_one.ChangeDutyCycle(10)
	green_two.ChangeDutyCycle(10)
	red_one.ChangeDutyCycle(10)
	red_two.ChangeDutyCycle(10)

# Red leds on
def led_red():
	led_off()
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Red leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
	red_one.ChangeDutyCycle(100)
	red_two.ChangeDutyCycle(100)

# Green leds on
def led_green():
	led_off()
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Green leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
	green_one.ChangeDutyCycle(100)
	green_two.ChangeDutyCycle(100)

# Blue leds on
def led_blue():
	led_off()
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Blue leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
	blue_one.ChangeDutyCycle(100)
	blue_two.ChangeDutyCycle(100)
	blue_three.ChangeDutyCycle(100)

# All leds off
def led_off():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,All leds off".format(strftime("%Y-%m-%d %H:%M:%S")))
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
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Rolling red alert leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
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
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Rolling green alert leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
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
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Rolling blue alert leds on".format(strftime("%Y-%m-%d %H:%M:%S")))
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
		error_log.write("\n{0},Log,Water reading started.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	global dateNow
	global todaysDate
	global timesWateredToday
	global ledSwitch
	global lastWatered
	global tankFull
	global waterError
	global waterLevel
	waterLevel = 0
	dateNow = strftime("%d")
	ledSwitch = 1
	
	Thread(target = led_rolling).start()
	
	try:
		tts = gTTS(text="Alert! Testing soil moisture levels in T minus two seconds." , lang='en')
		tts.save("moisture.mp3")
		os.system("mpg321 -q moisture.mp3")
	except:
		os.system("mpg321 -q moisture.mp3")
		pass
	
	GPIO.output(hygro_Power, True)
	time.sleep(1)
	
	waterNeed = 0

	for x in range(1,4):
		waterNeed += GPIO.input(hygro)
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

	if waterNeed <= 1:
		ledSwitch = 1
		waterLevel = 0

		Thread(target = led_green_alert).start()
		
		with open("error_log.csv", "a") as error_log:
				error_log.write("\n{0},Log,Moisture levels are normal".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		try:
			tts = gTTS(text="Code green. Moisture levels are acceptable. All systems are functioning within normal parameters." , lang='en')
			tts.save("green.mp3")
			os.system("mpg321 -q green.mp3")
		except:
			os.system("mpg321 -q green.mp3")
			pass

		logging()
		ledSwitch = 0
		time.sleep(2)

	elif waterNeed > 1:
		if dateNow == todaysDate:
			if timesWateredToday < 2:
				ledSwitch = 1
				waterLevel = 100
				timesWateredToday += 1

				Thread(target = led_red_alert).start()
				
				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Alert,Watering protocols will now engage".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				try:
					tts = gTTS(text="Alert. Code red. Watering protocols will now engage." , lang='en')
					tts.save("red.mp3")
					os.system("mpg321 -q red.mp3")
				except:
					os.system("mpg321 -q red.mp3")
					pass
				time.sleep(1)

				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Alert,Water pump engaging.".format(strftime("%Y-%m-%d %H:%M:%S")))
				try:
					tts = gTTS(text="Water pump engaging." , lang='en')
					tts.save("water.mp3")
					os.system("mpg321 -q water.mp3")
				except:
					os.system("mpg321 -q water.mp3")
					pass
				
				water_pump()
				tankFull -= 1
				
				if tankFull < 3:
					sms_tank_warning()
					ledSwitch = 1
					
					Thread(target = led_red_alert).start()
					
					try:
						tts = gTTS(text="Alert. Code red. Water tank is almost depleted. Refill. Priority alpha. Sending SMS" , lang='en')
						tts.save("tankempty.mp3")
						os.system("mpg321 -q tankempty.mp3")
					except:
						os.system("mpg321 -q tankempty.mp3")
						pass
					
					ledSwitch = 0
					time.sleep(2)
				
				else:
					pass
				
				lastWatered = (("Status update. The plant was succesfully watered at " + strftime("%H:%M") + ", " + strftime("%A, %B %d" + ".")))
				f = open('lastwatered.txt', 'w')
				f.write(lastWatered)
				f.close()
				
				time.sleep(2)
				logging()
				
				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Log,Moisture levels will now be re-tested".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				try:
					tts = gTTS(text="Alert. Moisture levels will now be re-tested by secondary systems." , lang='en')
					tts.save("retest.mp3")
					os.system("mpg321 -q retest.mp3")
				except:
					os.system("mpg321 -q retest.mp3")
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
					tts = gTTS(text="Error. Moisture sensors may be corrupted. Please check. Aborting watering protocols for now. Sending SMS." , lang='en')
					tts.save("sensors.mp3")
					os.system("mpg321 -q sensors.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
				except:
					os.system("mpg321 -q sensors.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
					pass
				
				sms_moisture_warning()
				
				ledSwitch = 0
				waterError = 1
				waterLevel = 0
				
				logging()
				time.sleep(2)
			
			elif waterError == 1 and timesWateredToday > 1:
				with open("error_log.csv", "a") as error_log:
						error_log.write("\n{0},Log,Moisture sensor skipped.".format(strftime("%Y-%m-%d %H:%M:%S")))
				
				ledSwitch = 1
				
				Thread(target = led_red_alert).start()
				
				try:
					tts = gTTS(text="Alert. Moisture sensors may be corrupted. Please check. Aborting watering protocols for now." , lang='en')
					tts.save("sensors.mp3")
					os.system("mpg321 -q sensors.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
				except:
					os.system("mpg321 -q sensors.mp3")
					os.system("mpg321 -q vader_breathe.mp3")
					os.system("mpg321 -q vader_dont_fail.mp3")
					pass
				
				ledSwitch = 0
				waterLevel = 0
				
				logging()
				time.sleep(2)
		
		elif dateNow != todaysDate:
			todaysDate = strftime("%d")
			timesWateredToday = 0
			waterError = 0
			logging()
			water_reading()

	time.sleep(2)
	led_off()

# Temp and humidity

def temp_humidity():
	try:
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
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed reading temp and humidity".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

### Logging of statistics

def logging():
	try:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Gathering stats for logging.".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		humidity, temperature = Adafruit_DHT.read_retry(11, 4)
		
		r = requests.get(conf['openweather']['api'])
		json_object = r.json()
		temp_k = json_object["main"]["temp"]
		temp_c = (temp_k - 273.15)
		o_humidity = json_object["main"]["humidity"]
		
		with open("stats.csv", "a") as log:
			log.write("\n{0},{1},{2},{3},{4:0.0f},{5}".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature),str(humidity),str(waterLevel), (temp_c), str(o_humidity)))
		fileupload_stats()

	except:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed gathering stats for logging.".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

### Status update with diagnostics

def self_diagnostics():
	led_off()
	
	global ledSwitch
	ledSwitch = 1
	
	Thread(target = led_rolling).start()
	
	try:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Diagnostics start up sequence".format(strftime("%Y-%m-%d %H:%M:%S")))
		tts = gTTS(text="Alert. Empire plant pot online. Self diagnostics start up sequence initiated. Checking ligths." , lang='en')
		tts.save("diagnostics_lights.mp3")
		os.system("mpg321 -q diagnostics_lights.mp3")
	except:
		with open("error_log.csv", "a") as error_log:
			error_log.write("Error: Internet error.".format(strftime("%Y-%m-%d %H:%M:%S")))
		internet_on()
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
		tts = gTTS(text="Self diagnostics. Central core CPU runs at {0:0.0f} degrees celsius. Room temperature is {1:0.0f} degrees celsius with a relative humidity of {2:0.0f} percent.".format(temp, temperature, humidity) , lang='en')
		tts.save("diagnostics.mp3")
		os.system("mpg321 -q diagnostics.mp3")
	except:
		print("{0}\n Error: Internet error.".format(strftime("%Y-%m-%d %H:%M:%S")))
		internet_on()
		pass
	
	ledSwitch = 0
	time.sleep(2)
	internet_on()

### Checking internet connection

def internet_on():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Testing Internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	global ledSwitch
	
	try:
		urllib.request.urlopen('http://www.google.com')
	except:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,No internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		try:
			tts = gTTS(text="Alert! All communications are down. Alert! Systems running in emergency mode. Alert! Restoring communications, priority alpha." , lang='en')
			tts.save("internet_off.mp3")
			os.system("mpg321 -q internet_off.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
		except:
			os.system("mpg321 -q internet_off.mp3")
			os.system("mpg321 -q vader_breathe.mp3")
			os.system("mpg321 -q vader_dont_fail.mp3")
			pass
		
		ledSwitch = 0
		time.sleep(2)
		pass
	
	else:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,We have an internet connection.".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_green_alert).start()
		
		try:
			tts = gTTS(text="Code green! All communication systems are online and working within normal parameters." , lang='en')
			tts.save("internet_on.mp3")
			os.system("mpg321 -q internet_on.mp3")
		except:
			os.system("mpg321 -q internet_on.mp3")
			pass
		
		ledSwitch = 0
		time.sleep(2)

### FILE UPLOADS

### Init files upload

def fileupload_init():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,uploading initial files.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	host = conf['user']['host']
	port = conf['user']['port']
	transport = paramiko.Transport((host, port))

	password = conf['user']['password']
	username = conf['user']['username']
	transport.connect(username = username, password = password)

	sftp = paramiko.SFTPClient.from_transport(transport)
	
	try:
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
		global ledSwitch
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Warning. Initial files error uploading".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		tts = gTTS(text="Warning. Initial files error uploading." , lang='en')
		tts.save("upload_init_error.mp3")
		os.system("mpg321 -q upload_init_error.mp3")
		os.system("mpg321 -q vader_breathe.mp3")
		os.system("mpg321 -q vader_dont_fail.mp3")
		
		ledSwitch = 0
		time.sleep(2)
		
		internet_on()
		pass

### Stat file upload

def fileupload_stats():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Uploading stats".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	host = conf['user']['host']
	port = conf['user']['port']
	transport = paramiko.Transport((host, port))

	password = conf['user']['password']
	username = conf['user']['username']
	transport.connect(username = username, password = password)

	sftp = paramiko.SFTPClient.from_transport(transport)
	
	try:
		sftp.chdir("/var/www/bloggmu/public/rum/blomma")
		filepath = "stats.csv"
		localpath = "/home/pi/kod/empirebot/stats.csv"

		sftp.put(localpath, filepath)

		sftp.close()
		transport.close()
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Log,Stat file has been uploaded".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	except:
		global ledSwitch
		
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Warning. Stat file error uploading".format(strftime("%Y-%m-%d %H:%M:%S")))
		
		ledSwitch = 1
		
		Thread(target = led_red_alert).start()
		
		tts = gTTS(text="Warning. Status file error uploading." , lang='en')
		tts.save("upload_error.mp3")
		os.system("mpg321 -q upload_error.mp3")
		os.system("mpg321 -q vader_breathe.mp3")
		os.system("mpg321 -q vader_dont_fail.mp3")
		
		ledSwitch = 0
		time.sleep(2)
		internet_on()
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
		
		tts = gTTS(text="Warning. Twitter error. Unable to follow twitter users." , lang='en')
		tts.save("twitter_follow_error.mp3")
		os.system("mpg321 -q twitter_follow_error.mp3")
		os.system("mpg321 -q vader_breathe.mp3")
		os.system("mpg321 -q vader_dont_fail.mp3")
		
		ledSwitch = 0
		time.sleep(2)
		internet_on()
		pass

def tweet_auto():
	global ledSwitch

	try:
		while True:
			f = open('tweetid.txt','r')
			tweetID = (f.read())
			f.close()

			consumer_key = conf['twitter']['consumer_key']
			consumer_secret = conf['twitter']['consumer_secret']
			access_token = conf['twitter']['access_token']
			access_token_secret = conf['twitter']['access_token_secret']

			auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			api = tweepy.API(auth)

			tweetFetched = api.user_timeline(screen_name = "mickekring", count = 1)

			for status in tweetFetched:
				tweetTextFetched = (status.text)
				tweetIDFetched = str(status.id)

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
						
						tts = gTTS(text="Alert. Incoming Tweet. Message recieved... {0}".format(tweetTextFetched) , lang='en')
						tts.save("incoming_tweet.mp3")
						os.system("mpg321 -q incoming_tweet.mp3")
						tts = gTTS(text="Lord Vader. Respond to tweet." , lang='en')
						tts.save("responding_tweet.mp3")
						os.system("mpg321 -q responding_tweet.mp3")
						
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
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
						
						elif "who" and "are" in tweetText:
							api.update_status(status = "I am an automated plant pot, @mickekring", in_reply_to_status_id = (tweetIDFetched))
							
							with open("error_log.csv", "a") as error_log:
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
						
						elif "refill" in tweetText:
							tankFull = 10
							
							api.update_status(status = "Water levels are now at full again, @mickekring. ", in_reply_to_status_id = (tweetIDFetched))
							
							with open("error_log.csv", "a") as error_log:
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
						
						elif "silence" in tweetText:
							audio_vol_none()
							
							api.update_status(status = "I've set speaker volume to 0%, @mickekring. ", in_reply_to_status_id = (tweetIDFetched))
							
							with open("error_log.csv", "a") as error_log:
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
						
						elif "loud" in tweetText:
							audio_vol_full()
							
							api.update_status(status = "I've set speaker volume to 100%, @mickekring. ", in_reply_to_status_id = (tweetIDFetched))
							
							with open("error_log.csv", "a") as error_log:
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
						
						elif "help" in tweetText:
							
							api.update_status(status = "Commands:\nrefill, silence, loud, status - @mickekring.", in_reply_to_status_id = (tweetIDFetched))
							
							with open("error_log.csv", "a") as error_log:
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
						else:
							api.update_status(status = "I'm sorry but I don't understand, @mickekring. Please enhance my software.", in_reply_to_status_id = (tweetIDFetched))

							with open("error_log.csv", "a") as error_log:
								error_log.write("\n{0},Alert,Twitter message sent".format(strftime("%Y-%m-%d %H:%M:%S")))
					else:
						pass

			time.sleep(50)

	except:
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Twitter error - could not reply".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

### SMS

def sms():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Sending status SMS.".format(strftime("%Y-%m-%d %H:%M:%S")))
	account_sid = conf["twilio"]["account_sid"]
	auth_token = conf["twilio"]["auth_token"]
	client = Client(account_sid, auth_token)
	message = client.messages.create(
		to= conf["twilio"]["to_phone_number"],
		from_= conf["twilio"]["from_phone_number"],
		body=tweetMessage + "\n" + lastWatered)

def sms_tank_warning():
	try:
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
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed sending tank warning SMS".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

def sms_moisture_warning():
	try:
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
		with open("error_log.csv", "a") as error_log:
			error_log.write("\n{0},Error,Failed sending moisture sensor warning SMS".format(strftime("%Y-%m-%d %H:%M:%S")))
		pass

### Audio controls

def audio_vol_full():
	with open("error_log.csv", "a") as error_log:
		error_log.write("\n{0},Log,Setting audio to 100%.".format(strftime("%Y-%m-%d %H:%M:%S")))
	
	m = alsaaudio.Mixer("PCM")
	current_volume = m.getvolume()
	m.setvolume(90)
	global ledSwitch
	ledSwitch = 1
	
	Thread(target = led_red_alert).start()

	try:
		tts = gTTS(text="Lord Vader... Set audio levels to full." , lang='en')
		tts.save("audio_full.mp3")
		os.system("mpg321 -q audio_full.mp3")
	except:
		os.system("mpg321 -q audio_full.mp3")
		pass
	
	os.system("mpg321 -q vader_yes.mp3")
	
	ledSwitch = 0
	time.sleep(2)

def audio_vol_none():
	global ledSwitch
	ledSwitch = 1
	
	Thread(target = led_red_alert).start()
	
	try:
		tts = gTTS(text="Lord Vader... Set audio levels to zero." , lang='en')
		tts.save("audio_zero.mp3")
		os.system("mpg321 -q audio_zero.mp3")
	except:
		os.system("mpg321 -q audio_zero.mp3")
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

#################### MAIN PROGRRAM #################################

def Main():
	try:
		print("---SYSTEM START UP---")
		button_delay = 0.2
		led_off()
		GPIO.output(hygro_Power, False)
		audio_vol_full()
		self_diagnostics()
		temp_humidity()
		Thread(target = tweet_auto).start()
		fileupload_init()
		
		while True:
			tweet_follow()
			water_reading()
			time.sleep(1800)

	finally:
		print("GPIO Clean up")
		GPIO.cleanup()

if __name__ == "__main__":
	Main()