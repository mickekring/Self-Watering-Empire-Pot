# Self Watering Empire Pot
__What is this? Well, it's a simple DIY/Maker/Python3 project which I created to learn more about electronics but it's mostly about learning Python. So the basics are; to design and 3D-print all parts, which will be a pot, a speaker, a water tank and some kind of housing for the Raspberry Pi. After that, I'll attach a couple of sensors measuring soil moisture, temperature, humidity and a couple of more things hopefully. We'll see what I can come up with.<br />
When the soil moisture levels are below a certain number a water pump will pump water into the pot.<br />
So why "empire"? Well, I wanted to throw a bit of Star Wars at it. :)__

## Work in progress - working!
__11 jan 2018:__ This project is a work in progress but it's now up and running to iron out some bugs and quirks. Check updates for more information.

## Disclaimer
My Python skills are at best on a beginners level so I'll gladly take on any good advice. But what you see is what you get. I'm not better than this.

## Where I'm at - at the moment
Here you'll find short movies of the latest state of the project.<br /><br />
[![](https://github.com/mickekring/Self-Watered-Empire-Pot/blob/master/images/2018-01-04.jpg "Latest state")](https://vimeo.com/249696012)

## What it is and what it does
* It's a plant pot, where a plant grows
* It detects whether the soil is too dry, and if it is, switches on a relay which cotrols a water pump, which gives water to the plant
* It reads temperature and humidity via a sensor where the plant is
* It grabs outside local temperature, humidity and the weather via API from openweathermap.org
* It has a speaker and an amplifier which makes it able to "speak" via gTTS (google text to speech)
* It has a couple of led diods, blue, red and green so it can display alerts, code greens and stuff using PWM (pulse width modulation). It also looks kind of cool
* It sends SMS to eg warn if the tank level is low and needs a refill via Twilio
* It can send status updates and recieve commands via Twitter
* It logs to a csv file
* It logs stats, which it sends to a web server via SFTP
* It keeps me company, when alone ;)
* It's got some fail safes, like only beeing able to water the plant for two times a day, then sends a warning SMS that something may be wrong, and it can only text that message once per day
* It's designed and 3D-printed by me, except the stormtrooper and the empire logo, which I found on Thingiverse and 3D-printed
* Since it's pretty internet-dependent, it will try-except ecerything if no connection is available and log it and store locally

## Updates
* __17 jan 2018 - v1.2 - Bug hunt__<br />
I've been running the script for a couple of days and have found some bugs. First, the script broke and stopped at midnight a couple of times. That seems to correspond to internet being down. But, since core pot functionality should keep running I've been hunting the problem. I added some more Try - Excepts. Last night, internet went down again, but the logs showed that the program continued to run. Hopefully that's that with that.<br />
The second problem I'm dealing with is the Twitter functionality. It sorta works, but not for long. At first I thought that I've been requesting data too much and broken the Twitter limits, but that doesn't seem to be the case. So I changed method for getting user timeline and I'll monitor if that works. It seems so at the moment.
* __07 jan 2018 - v1.2 - Fail safes__<br />
Sometimes the moisture sensors misread or are badly tuned or are simply just worn down. To prevent over watering or similar problems, I've coded a fail safe. When watered more than two times, it will send an SMS to check problems and lock watering for the rest of that day.
* __06 jan 2018 - v1.1 - Error logging__<br />
Added some error logging to external file for easier debugging. Test running the program for longer periods of time now, for bug finding. 
* __04 jan 2018 - v1.0 - Up and running__</br>
No more test program. v1.0. Everyting is running by itself and it responds to tweets, sends SMS if water tank levels are getting low... and most important of all, it waters the plant if the soil is too dry.
* __02 jan 2018 - v0.9 - Added weather data from openweathermap.org__<br/>
Outside temperature, humidity and weather conditions are now a part of the program.
* __01 jan 2018 - v0.8 - SMS and more Twitter__<br />
The program can now accept commands via Twitter, from users who are entrusted. It will be one of the main forms of interactions with the program. It can now send SMS. 
* __29 dec 2017 - v0.7 - Twitter capabilities__<br />
The program is now able to tweet, using Tweepy within Python. A function is setup and it's tweeting whatever is stored in the variable tweetMessage.
* __29 dec 2017 - v0.5 - Initial upload__<br />
Today is the day when I decided to start this GitHub project. More info will be added, but most importantly, this is a work in progress. I've been working on this project for a while, but I thought I ought to document it, so stay tuned.

## Hardware
Here I'll post the hardware that I'm using and where I bought it. Mostly, it's off Aliexpress, but you can find these generic part pretty much anywhere. I'll add to the list as the project expands.
* Raspberry Pi 3 model B | __$35-$40__
* Red, blue and green coloured LED diods - https://www.aliexpress.com/item/100pcs-lot-3MM-LED-Diode-Kit-Mixed-Color-Red-Green-Yellow-Blue-White/32792244682.html?spm=a2g0s.9042311.0.0.Vy04KZ - | __$1__
* Water pump - submersible that can run on 3V / 5V DC - https://www.aliexpress.com/item/Mute-Submersible-Pump-Water-Punp-DC-3V-5V-For-PC-Cooling-Water-Circulation-DIY/32717325894.html?spm=a2g0s.9042311.0.0.Vy04KZ | __$3-$4__
* PVC Hose - 16ft, which is a loooot more than you need - https://www.aliexpress.com/item/16FT-8mm-Inner-Dia-Clear-Plastic-PVC-Hose-Pipe-Tube-for-Tank-Air-Pump-Aquarium/32801840071.html?spm=a2g0s.9042311.0.0.Vy04KZ | __$4-$5__
* Soil moisture sensor YL-69 - https://www.aliexpress.com/item/Soil-Moisture-Sensor-Hygrometer-Module-for-Arduino-2560-UNO-1280-Free-Shipping-Wholesale/1398732669.html?spm=a2g0s.9042311.0.0.Vy04KZ | __$1__
* Temperature and relative humidity sensor - DHT11 - https://www.aliexpress.com/item/New-DHT11-Temperature-And-Relative-Humidity-Sensor-Module-For-Arduino/32802129494.html?spm=a2g0s.9042311.0.0.D4HhqX | __$1__
* Relay 1 channel - https://www.aliexpress.com/item/1pcs-KY-019-5V-One-1-Channel-Relay-Module-Board-Shield-For-PIC-AVR-DSP-ARM/32802892040.html?spm=a2g0s.9042311.0.0.D4HhqX __$1__
* Prototype board - https://www.aliexpress.com/item/B1307-Free-shipping-10pcs-Double-Side-Prototype-PCB-diy-Universal-Printed-Circuit-Board-5x7cm/32352552510.html?spm=2114.search0104.3.29.nVPQps&ws_ab_test=searchweb0_0,searchweb201602_4_10152_10151_10065_10344_10068_10342_51102_10343_10340_10341_10084_10083_10307_10301_10303_10312_10313_10059_10314_10534_100031_10604_10103_10605_10594_10142-normal#cfs,searchweb201603_25,ppcSwitch_5&algo_expid=e8c37783-1a55-41a7-aa64-2a65db2bfa78-4&algo_pvid=e8c37783-1a55-41a7-aa64-2a65db2bfa78&rmStoreLevelAB=5 | __$2-$3__
* Amplifier 1.4W - TPA2005D1 | __$6-$7__
* Speaker - 8ohm ø57mm 0.25W | __$1__

## 3D models
Here you can find links to the 3D parts that I've designed in TinkerCAD. They are public, so you can grab them and remix them if you like. I'm using an Ultimaker 2 GO, which is a small printer, so these models should easily print on about any machine.

* Flower pot module - https://www.tinkercad.com/things/fQOVuEjylp8
* Speaker module - https://www.tinkercad.com/things/66gCLMuzKD2
* Speaker top - https://www.tinkercad.com/things/8jMyELo6IXI
* Water tank module - https://www.tinkercad.com/things/9iR5u62zSzV
* Water tank top - https://www.tinkercad.com/things/jUjSysWbdVi
<br /><br />
* Empire logo - This one is not designed by me. I found it on Thingiverse by newayb - https://www.thingiverse.com/thing:590307

## Python libraries and stuff
In this project I'm using a couple of libraries that you'll probably have to install to run the program. Google how to install these on your system.
* Paramiko - Uploading of files via SFTP to server
* Adafruit_DHT - To make easy use of the DHT11 sensor
* gTTS - Google text to speech
* YAML - To store and retrieve credentials from external yml file
* Tweepy - so that the pot can tweet on Twitter
* alsaaudio - to control volume levels
* gpiozero - to get the cpu temperature - for statistics
* twilio - to get twilio and sms functionality working

# Modules
I'll explain what the different modules do here.

## Speaker / Light module
![](https://github.com/mickekring/Self-Watered-Empire-Pot/blob/master/images/speaker_module.jpg "Speaker Module")<br /><br />
The speaker module contains a small speaker and an amplifier (the red little board), with a pot for volume as you can see on the left side of the picture. You can also see the LED diods that I have soldered to a prototype board with resistors. Everything is then glued on.<br />To the right you can see the front, where I've glued on an empire (Star Wars) logo as speaker grille. Above the speaker you see a sort of see through pane which I created (once again) out of glue. This makes the LED lights looking a bit cooler (in my opinion), since you don't really see the individual diods.<br />There's also a separate top and back which will be glued on.

## Pot module
There's not really that much to say about this module, more than that this is where the plant resides.

## Water tank module
![](https://github.com/mickekring/Self-Watered-Empire-Pot/blob/master/images/water_tank.JPG "Water Tank")<br /><br />
At the bottom if the tank I've glued down the water pump. The tank holds about 10-11 cycles of watering (3 seconds).

## Road map and goals
This is sort of what I want out of the project. As I get new ideas, this will grow.
- [x] gTTS - Google text to speech - The pot should be able to communicate through speech.
- [x] ~~STT - Speech to text - preferably I'd like to speak to the pot (which is healthy for it as well) as my main input~~ This will not be implemented, since I find it to unreliable and slow. Main means of communication will be trhough Twitter, where I can send commands.
- [x] Temperature sensor - record temperature near the plant for statistics
- [x] Humidity sensor - record humidity near the plant for statistics
- [x] Soil moisture sensor - to sense whether the plant needs water or not
- [ ] Light sensor - record the amount of light the plant gets
- [ ] Proximity sensor - Sense when people are near the plant for automatic status updates
- [x] PWM - Pulse Width Modulation - for a pulsating light effect when red and green alert and for blue when pot is speaking
- [x] Check internet connection and warn if off
- [x] Log sensory inputs in a csv-file
- [x] Send logs to a web server via SFTP and serve graph charts
- [x] Relay - Control water pump
- [x] ~~Camera - It would be cool if I could hook up a camera and use it to take a snap now and again, which will be sent to a web server~~This will not be implemented, since I think it would be kind of useless after a while. 
- [x] Design and build casings and pots using 3D-software and printing - I'm designing it by using modules. A pot module, speaker/light module, water tank and so on.
- [x] Design and solder some simple circuit boards - Must learn to solder
- [x] ~~Send warnings and status via e-mail or sms or slack or...~~ It will be communicating via SMS and Twitter.
- [x] Twitter - The pot should be able to tweet. It's twitter account is @empireplantbot
- [x] Try / Except - Make sure that the core functions keeps running and logging is done locally only if eg internet goes down
- [x] Fail Safes - Make sure the plant can't be over watered in case of malfunctioning sensors or other.
- [ ] Network messaging - Merge this project with earlier project and make the two RPi's talk to each other
- [x] Glue gun - Glue the s--t out of everything
- [x] Get weather data from openweathermap.org to display and log. Could be interesting to see how much outside temperatures affects the amount of watering needed.
- [x] Message me when the water tank needs refill. Now, the pump is on for 3 seconds. That's enough for 10 waterings.
