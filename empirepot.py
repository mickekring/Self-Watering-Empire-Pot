import RPi.GPIO as GPIO
import time, random, math, threading, datetime, locale, os, sys, Adafruit_DHT, urllib, yaml, paramiko, tweepy, requests
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
lastWatered = "No watering since reboot of system core."

# Loading credentials
conf = yaml.load(open("credentials.yml"))

### FUNCTIONS ###

# Water pump system - sets number of seconds that the water will pump. Change time.sleep.
def water_pump():
	print("Relay on")
	GPIO.output(relay, True)
	time.sleep(3)
	print("Relay off")
	GPIO.output(relay, False)

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
		print("Alert! Soil moisture levels will be tested in T minus two seconds.")
		tts = gTTS(text="Alert! Soil moisture levels will be tested in T minus two seconds." , lang='en')
		tts.save("moisture.mp3")
		os.system("mpg321 -q moisture.mp3")
	except:
		os.system("mpg321 -q moisture.mp3")
		pass
	waterNeed = 0
	GPIO.output(hygro_Power, True)
	time.sleep(1)
	for x in range(1,4):
		waterNeed += GPIO.input(hygro)
		print(waterNeed)
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
		try:
			print("Code green. We have a code green. All systems stabilized and functioning within normal parameters.")
			tts = gTTS(text="Code green. We have a code green. All systems stabilized and functioning within normal parameters." , lang='en')
			tts.save("green.mp3")
			os.system("mpg321 -q green.mp3")
		except:
			os.system("mpg321 -q green.mp3")
			pass
		logging()
		ledSwitch = 0
	if waterNeed > 1:
		ledSwitch = 1
		waterLevel = 50
		lastWatered = (("Status update. The plant was succesfully watered at " + strftime("%H:%M") + ", " + strftime("%A, %B %d" + ".")))
		Thread(target = led_red_alert).start()
		try:
			print("Code red. We have a code red. Watering protocols will now engage.")
			tts = gTTS(text="Code red. We have a code red. Watering protocols will now engage." , lang='en')
			tts.save("red.mp3")
			os.system("mpg321 -q red.mp3")
		except:
			os.system("mpg321 -q red.mp3")
			pass
		time.sleep(1)
		try:
			print("Alert! Water pump engaging.")
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
			print("Moisture levels will now be re-tested by secondary systems.")
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
	r = requests.get(conf['openweather']['api'])
	json_object = r.json()
	temp_k = json_object["main"]["temp"]
	temp_c = (temp_k - 273.15)
	o_humidity = json_object["main"]["humidity"]
	w_text = json_object["weather"][0]["main"]
	w_desc = json_object["weather"][0]["description"]
	humidity, temperature = Adafruit_DHT.read_retry(11, 4)
	global tweetMessage
	tweetMessage = "Plant Pot Stats\n\nCity: Stockholm, SWE\nTime: {2}\n\nIndoors temp: {0:0.0f}°C\nIndoors humidity: {1:0.0f}%\n\nOutside temp: {3:0.0f}°C\nOutside humidity: {4}%\nOutside weather: {5} | {6}".format(temperature, humidity, strftime("%H:%M"), temp_c, o_humidity, w_text, w_desc)
	#print(tweetMessage)

# Logging of statistics
def logging():
	print("\n{0},{1},{2},{3}".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature),str(humidity),str(waterLevel)))
	with open("stats.csv", "a") as log:
		log.write("\n{0},{1},{2},{3}".format(strftime("%Y-%m-%d %H:%M:%S"),str(temperature),str(humidity),str(waterLevel)))
	fileupload_stats()

# Status update with diagnostics
def self_diagnostics():
	led_off()
	try:
		print("Diagnostics start up sequence. Checking ligths.")
		tts = gTTS(text="Diagnostics start up sequence. Checking ligths." , lang='en')
		tts.save("diagnostics_lights.mp3")
		os.system("mpg321 -q diagnostics_lights.mp3")
	except:
		print("Internet error.")
		internet_on()
		pass
	time.sleep(1)
	led_all_on()
	time.sleep(1)
	led_off()
	time.sleep(1)
	led_blue()
	time.sleep(1)
	led_green()
	time.sleep(1)
	led_red()
	time.sleep(1)
	led_off()
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
		consumer_key = conf['twitter']['consumer_key']
		consumer_secret = conf['twitter']['consumer_secret']
		access_token = conf['twitter']['access_token']
		access_token_secret = conf['twitter']['access_token_secret']

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)

		img = "wateringplants.jpg"
		api.update_with_media(img, status=tweetMessage + " " + lastWatered)
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

def tweet_auto():
	tweetID = 947891597160706050
	tweetText = "ABC"

	consumer_key = conf['twitter']['consumer_key']
	consumer_secret = conf['twitter']['consumer_secret']
	access_token = conf['twitter']['access_token']
	access_token_secret = conf['twitter']['access_token_secret']

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	while True:
		tweetFetched = api.user_timeline(screen_name = "mickekring", count = 1)

		for status in tweetFetched:
			tweetTextFetched = (status.text)
			tweetIDFetched = (status.id)

			if tweetIDFetched == tweetID:
				#print("\nNo new message has arrived.")
				pass
			else:
				tweetID = tweetIDFetched
				tweetText = tweetTextFetched.lower()
				
				if "@empireplantbot" in tweetText:
					if "status" in tweetText:
						temp_humidity()
						api.update_status(status = ("@mickekring\n" + (tweetMessage) + "\n\nWatering system: " + lastWatered), in_reply_to_status_id = (tweetIDFetched))
					elif "who" and "are" in tweetText:
						api.update_status(status = "I am an automated plant pot, @mickekring", in_reply_to_status_id = (tweetIDFetched))
					elif "green" in tweetText:
						led_green()
						api.update_status(status = "The green lights are on now, @mickekring", in_reply_to_status_id = (tweetIDFetched))
						time.sleep(5)
						led_off()
					else:
						api.update_status(status = "I'm sorry but I don't understand, @mickekring. Please enhance my software.", in_reply_to_status_id = (tweetIDFetched))
				else:
					pass


		time.sleep(20)

# SMS

def sms():
	account_sid = conf["twilio"]["account_sid"]
	auth_token = conf["twilio"]["auth_token"]

	client = Client(account_sid, auth_token)

	message = client.messages.create(
		to= conf["twilio"]["to_phone_number"],
		from_= conf["twilio"]["from_phone_number"],
		body=tweetMessage + "\n" + lastWatered + "\n🌱🌱🌱🌱🌱")

	print(message.sid)

#################### MAIN PROGRRAM #################################

def Main():
	try:
		button_delay = 0.2
		led_off()
		GPIO.output(hygro_Power, False)
		temp_humidity()
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
			print("13. SMS\n")
			print("14. Auto Tweet.\n")
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
				water_pump()
			if val == "5":
				self_diagnostics()
			if val == "6":
				temp_humidity()
			if val =="7":
				internet_on()
			if val =="8":
				GPIO.output(hygro_Power, True)
				waterNeed = GPIO.input(hygro)
				print(waterNeed)
				print(lastWatered)
			if val =="9":
				GPIO.output(hygro_Power, False)
			if val =="10":
				logging()
			if val =="11":
				fileupload_init()
			if val =="12":
				tweet_follow()
			if val =="13":
				sms()
			if val =="14":
				Thread(target = tweet_auto).start()

	finally:
		print("GPIO Clean up")
		GPIO.cleanup()

if __name__ == "__main__":
	Main()