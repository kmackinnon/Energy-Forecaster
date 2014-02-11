'''
Created on Nov 16, 2013

@author: USER
'''

import urllib2, datetime, ast
from datetime import timedelta

# Constants
power_code = 50578
radiation_code = 66094
humidity_code = 66095
temperature_code = 66077
wind_code = 66096

sample_input = str({"id":66077,"label":"Montreal Temperature - CWTA","unit":"AC","quantity":"temperature","resource":"outside","start":"2013-11-15T23:00:00-05:00","end":"2013-11-17T00:00:00-05:00","average":8.243999999999998,"data":[["2013-11-15T23:00:00-05:00",7.7],["2013-11-16T00:00:00-05:00",7.7],["2013-11-16T01:00:00-05:00",7],["2013-11-16T02:00:00-05:00",6],["2013-11-16T03:00:00-05:00",7],["2013-11-16T04:00:00-05:00",5],["2013-11-16T05:00:00-05:00",5],["2013-11-16T06:00:00-05:00",5],["2013-11-16T07:00:00-05:00",4],["2013-11-16T08:00:00-05:00",4],["2013-11-16T09:00:00-05:00",7],["2013-11-16T10:00:00-05:00",9.8],["2013-11-16T11:00:00-05:00",11],["2013-11-16T12:00:00-05:00",12],["2013-11-16T13:00:00-05:00",12],["2013-11-16T14:00:00-05:00",12],["2013-11-16T15:00:00-05:00",12],["2013-11-16T16:00:00-05:00",11.7],["2013-11-16T17:00:00-05:00",11.4],["2013-11-16T18:00:00-05:00",10.8],["2013-11-16T19:00:00-05:00",10.2],["2013-11-16T20:00:00-05:00",7.7],["2013-11-16T21:00:00-05:00",7.2],["2013-11-16T22:00:00-05:00",6.7],["2013-11-16T23:00:00-05:00",6.2]]})

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
      weather_formatted.append("")
  
  return weather_formatted

def main():
  now = datetime.datetime.now()
  query_date = now - timedelta(hours=8)
  query_date = query_date.strftime("%Y-%m-%dT%H:%M-05:00")
  now = now.strftime("%Y-%m-%dT%H:%M")
  print now

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
      power_stripped.append(x[1])
    else:
      power_stripped.append('null')
  
  radiation_interleaved = interleave_weather(dates,radiation_raw)
  humidity_interleaved = interleave_weather(dates,humidity_raw)
  temperature_interleaved = interleave_weather(dates,temperature_raw)
  wind_interleaved = interleave_weather(dates,wind_raw)
  
  d_pulse = dict(date=dates, radiation=radiation_interleaved,humidity = humidity_interleaved,temperature=temperature_interleaved, wind=wind_interleaved, demand=power_stripped)
  for item in d_pulse['dates']:
	f = open('output.txt',"a")
	f.write(str(item))
	print d_pulse['dates']
  f.close()
  
if __name__ == "__main__":
    main()