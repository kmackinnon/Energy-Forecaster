import os
from django.shortcuts import render_to_response

import numpy as np
import csv, requests

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sklearn.svm import SVR

import urllib2, datetime, ast
from datetime import timedelta

# Constants
power_code = 50578
radiation_code = 66094
humidity_code = 66095
temperature_code = 66077
wind_code = 66096

#---------------- home response -------------------
def home(request):
  return render_to_response('home.html')

#---------------- interpolation and machine learning below ------------------

# weather interpolation
def interpolate(input):
	leadingZeros = []
	if input[0] == 'null':
		leadingZeros = ['null']
		if input[1] == 'null':
			leadingZeros = ['null',0]
			if input[2] == 'null':
				leadingZeros = ['null',0,0]
	
	for i in range(0, len(leadingZeros)):
		input.remove('null')
	#generate xs and ys for polyfit
	x = []
	y = []
	for i in range(len(input)):
		if i % 4 != 0:
			continue
		input[i] = float(input[i])
		x.append(float(i))
		y.append(float(input[i]))

	xs = np.array(x)
	ys = np.array(y)

	# piecewise function for weather data interpolation (3 6th degree + 1 5th degree polyfit functions)
	f = lambda z: (np.poly1d(np.polyfit(xs[:7], ys[:7], 6)))(z) if 0 <= z <= 23 else ((np.poly1d(np.polyfit(xs[6:13], ys[6:13], 6)))(z) if 24 <= z <= 47 else ((np.poly1d(np.polyfit(xs[12:19], ys[12:19], 6)))(z) if 48 <= z <= 71 else ((np.poly1d(np.polyfit(xs[18:], ys[18:], 5)))(z) if 72 <= z <= 95 else None)))

	for k in range(len(input)):
		if k % 4 == 0:
			continue
		input[k] = f(float(k))
	
	u = []
	u = leadingZeros + input
	return u
	
def machinelearningCurl(csv_file):
#   parse CSV
	d = {}
	d['date'] = []
	d['radiation'] = []
	d['humidity'] = []
	d['temperature'] = []
	d['wind'] = []
	d['demand'] = []

	dictreader = csv.DictReader(csv_file, fieldnames=['date', 'radiation', 'humidity', 'temperature', 'wind', 'demand'], delimiter=',')

	next(dictreader)
	for row in dictreader:
		for key in row:
			d[key].append(row[key])

#   interpolate weather data
	interpolate(d['radiation'])
	interpolate(d['humidity'])
	interpolate(d['temperature'])
	interpolate(d['wind'])
	
#   train machine learning algorithm
	training_x = np.array(zip(d['radiation'], d['humidity'], d['temperature'], d['wind'])[:32])
	training_y = np.array(d['demand'][:32])
	
	poly_svr = SVR(kernel='poly', degree=2)
	poly_svr.fit(training_x, training_y)

	prediction_x = np.array(zip(d['radiation'], d['humidity'], d['temperature'], d['wind'])[32:])
	demand_predictions = poly_svr.predict(prediction_x)

	return demand_predictions

#------------- curl interface ----------------

@csrf_exempt
def machine_interface(request):
  #return render_to_response('home.html')
  response = HttpResponse(content_type='text/plain')
  
  if request.method == 'POST':
    file = request.FILES['file']
    demand = machinelearningCurl(file)
  else:
  	demand = 'Whelp, somethin done fucked up...'
	
  response.write(demand)
  return response

#------------------ pulse below --------------------

def get_pulse_json(code,date):
  data = urllib2.urlopen("https://api.pulseenergy.com/pulse/1/points/"+str(code)+"/data.json?key=A366D4672C54464D423656BD2D3DBAA3&interval=day&start="+date).read() 
  return data

def json_to_list(json):   
    list_out = []
    for x in json['data']:
      #y = x.pop()
      #list_out.append(y)
      list_out.append(x)
    return list_out

def interleave_weather(dates,weather_raw):
  weather_formatted = []
  for x in dates:
    date_found = 0
    for y in weather_raw:
      if x == y[0]:
        weather_formatted.append(y[1])
        date_found = 1
      #  break
    if date_found == 0:
      weather_formatted.append('null')
  
  return weather_formatted

def convertListToChartData(input):	
	avgValue = 0
	values = list(input)
	x = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	
	if len(values) > 100:
		rangeMax = 100
	else:
		rangeMax = len(values)
		
	
	if values[0] == 'null':
		offset = 1
	else:
		offset = 0
		rangeMax = rangeMax - 4;	
	
	average = 0
	for i in range(0, rangeMax):
		if i == 0 and offset == 1:
			continue
			
		if values[i] != 'null':
			if i % 4 == 0 and i < rangeMax - 4: 
				avgValue = 0
				divisor = 0
				for j in range(i, i+4):
					if values[j] != 'null':
						avgValue = avgValue + values[j]
						divisor = divisor + 1
				avgValue = avgValue / divisor
				index = int(i / 4) - offset
				x[index] = avgValue
				avgValue = 0
		
	return x

def extrapolate(oldData, newData):
	# extrapolates the energy demand data
	index = 0
	newDemand = newData['demand']
	oldDemand = oldData['demand']
	
	currIndex = -1
	for i in range(0,len(newDemand)):
		if newDemand[i] == 0:
			if currIndex == -1 and i != 0:
				currIndex = i-1
				
			# finds the differences in last week's data and applies the safe variation to this week
			oldDiff = (oldDemand[i] - oldDemand[currIndex])
			newDemand[i] = newDemand[currIndex] + oldDiff
	
	return newDemand
	
@csrf_exempt
def pulse_interface(request):
	d_pulseRef = get_data(15 + 168)
	d_pulse2 = get_data(15 + 24)
	d_pulse = get_data(15)
	
	extraDemand = extrapolate(d_pulseRef, d_pulse)
	
	return render_to_response('pulse_chart.html', {"demand":extraDemand, "demand2":d_pulse2['demand'], "temp":d_pulse['temperature'], "temp2":d_pulse2['temperature'],"humidity":d_pulse['humidity'], "humidity2":d_pulse2['humidity'],"radiation":d_pulse['radiation'], "radiation2":d_pulse2['radiation'],"wind":d_pulse['wind'], "wind2":d_pulse2['wind']})

def get_data(deltaTime):
	now = datetime.datetime.now() # - timedelta(minutes=1)
	if now.minute % 15 == 0:
		now = now - timedelta(minutes=1)
		
	query_date = now - timedelta(hours=deltaTime)
	query_date = query_date.strftime("%Y-%m-%dT%H:%M-05:00")
	now = now.strftime("%Y-%m-%dT%H:%M")
		
	power_raw = get_pulse_json(power_code,query_date)
	power_raw = power_raw.replace("null","-1")  
	power_raw = ast.literal_eval(power_raw)
	power_raw = json_to_list(power_raw)

	radiation_raw = get_pulse_json(radiation_code,query_date)
	radiation_raw = ast.literal_eval(radiation_raw)
	radiation_raw = json_to_list(radiation_raw)
	
	humidity_raw = get_pulse_json(humidity_code,query_date)
	humidity_raw = ast.literal_eval(humidity_raw)
	humidity_raw = json_to_list(humidity_raw)
	
	temperature_raw = get_pulse_json(temperature_code,query_date)
	temperature_raw = ast.literal_eval(temperature_raw)
	temperature_raw = json_to_list(temperature_raw)
		
	wind_raw = get_pulse_json(wind_code,query_date)
	wind_raw = ast.literal_eval(wind_raw)
	wind_raw = json_to_list(wind_raw)
  
  # CSV specs: 1st line should be dummy 
  # DATE - RADIATION - HUMIDITY - TEMPERATURE - WIND - POWER
  
  # DATE/POWER
	dates = []
	power_stripped = []
	for x in power_raw:
		dates.append(x[0])
		if x[1] != -1:
			power_stripped.append(float(x[1]))
		else:
			power_stripped.append('null')
  
	radiation_interleaved = interleave_weather(dates,radiation_raw)
	humidity_interleaved = interleave_weather(dates,humidity_raw)
	temperature_interleaved = interleave_weather(dates,temperature_raw)
	wind_interleaved = interleave_weather(dates,wind_raw)

	interpTemp = interpolate(temperature_interleaved)
	interpHum = interpolate(humidity_interleaved)
	interpWind = interpolate(wind_interleaved)
	interpRad = interpolate(radiation_interleaved)	
	
	demandList = convertListToChartData(power_stripped)
	tempList = convertListToChartData(interpTemp)
	humidList = convertListToChartData(interpHum)
	windList = convertListToChartData(interpWind)
	radList = convertListToChartData(interpRad)
	
	return dict(date=dates, radiation=radList,humidity = humidList,temperature=tempList, wind=windList, demand=demandList)

	

     
	  
      
    
