# Self Watered Empire Pot
__What is this? Well, it's a simple DIY/Maker/Python3 project which I created to learn more about electronics but mostly about learning Python3. So the basics are; to design and 3D-print all parts, which will be a pot, a speaker, a water tank and some kind of housing for the Raspberry Pi. After that, I'll attach a couple of sensors measuring soil moisture, temperature, humidity and a couple of more things hopefully. We'll see what I can come up with.<br />
When the soil moisture levels are below a certain number a water pump will pump water into the pot.<br />
So why "empire"? Well, I wanted to throw a bit of Star Wars at it. :)__

## Work in progress
This project is a work in progress. Check updates for more information.

## Disclaimer
My Python skills are at best on a beginners level so I'll gladly take any good advice.

## Where I'm at - at the moment
Here you'll find short movies of the latest state of the project.<br /><br />
[![](https://github.com/mickekring/Self-Watered-Empire-Pot/blob/master/images/2017-12-29.jpg "Latest state")](https://vimeo.com/249059304/2b951d0b1a)

## Road map and goals
This is sort of what I want out of the project. As I get new ideas, this will grow.
- [x] gTTS - Google text to speech - The pot should be able to communicate through speech.
- [ ] STT - Speech to text - preferably I'd like to speak to the pot (which is healthy for it as well) as my main input
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
- [ ] Camera - It would be cool if I could hook up a camera and use it to take a snap now and again, which will be sent to a web server
- [ ] Design and build casings and pots using 3D-software and printing - I'm designing it by using modules. A pot module, speaker/light module, water tank and so on.
- [x] Design and solder some simple circuit boards - Must learn to solder
- [ ] Send warnings and status via e-mail or sms or slack or...
- [ ] Fail safes - Make sure that the core functions keeps running and logging is done locally only if eg internet goes down
- [ ] Network messaging - Merge this project with earlier project and make the two RPi's talk to each other
- [x] Glue gun - Glue the s--t out of everything

## Updates
__29 dec 2017 - Initial upload__
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

## 3D models
Here you can find links to the 3D parts that I've designed in TinkerCAD. They are public, so you can grab them and remix them if you like. I'm using an Ultimaker 2 GO, which is a small printer, so these models should easily print on about any machine.

* Flower pot module - https://www.tinkercad.com/things/fQOVuEjylp8
* Speaker module - https://www.tinkercad.com/things/66gCLMuzKD2
* Speaker top module - https://www.tinkercad.com/things/8jMyELo6IXI
* Water tank module - https://www.tinkercad.com/things/9iR5u62zSzV

## Python libraries and stuff
In this project I'm using a couple of libraries that you'll probably have to install to run the program. Google how to install these on your system.
* Paramiko - Uploading of files via SFTP to server
* Adafruit_DHT - To make easy use of the DHT11 sensor
* gTTS - Google text to speech
* YAML - To store and retrieve credentials from external yml file

# Modules
I'll explain what the different modules do here.

## Speaker / Light module
![](https://github.com/mickekring/Self-Watered-Empire-Pot/blob/master/images/speaker_module.jpg "Speaker Module")<br /><br />


## History and ideas
![](https://github.com/mickekring/Self-Watered-Empire-Pot/blob/master/images/fortproj2-2.jpg "Sketch")
This is how it all started. With a sketch on my whiteboard at the office. I wanted to learn more about Python3 and what you can do with programming.<br />
More info will be written...
