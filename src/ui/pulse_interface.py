'''
Created on Nov 16, 2013

@author: USER
'''


import urllib2, datetime, ast
from datetime import timedelta

# Constants
power = 50578
radiation = 66094
humidity = 66095
temperature = 66077
wind = 66096

sample_input = str({"id":66077,"label":"Montreal Temperature - CWTA","unit":"AC","quantity":"temperature","resource":"outside","start":"2013-11-15T23:00:00-05:00","end":"2013-11-17T00:00:00-05:00","average":8.243999999999998,"data":[["2013-11-15T23:00:00-05:00",7.7],["2013-11-16T00:00:00-05:00",7.7],["2013-11-16T01:00:00-05:00",7],["2013-11-16T02:00:00-05:00",6],["2013-11-16T03:00:00-05:00",7],["2013-11-16T04:00:00-05:00",5],["2013-11-16T05:00:00-05:00",5],["2013-11-16T06:00:00-05:00",5],["2013-11-16T07:00:00-05:00",4],["2013-11-16T08:00:00-05:00",4],["2013-11-16T09:00:00-05:00",7],["2013-11-16T10:00:00-05:00",9.8],["2013-11-16T11:00:00-05:00",11],["2013-11-16T12:00:00-05:00",12],["2013-11-16T13:00:00-05:00",12],["2013-11-16T14:00:00-05:00",12],["2013-11-16T15:00:00-05:00",12],["2013-11-16T16:00:00-05:00",11.7],["2013-11-16T17:00:00-05:00",11.4],["2013-11-16T18:00:00-05:00",10.8],["2013-11-16T19:00:00-05:00",10.2],["2013-11-16T20:00:00-05:00",7.7],["2013-11-16T21:00:00-05:00",7.2],["2013-11-16T22:00:00-05:00",6.7],["2013-11-16T23:00:00-05:00",6.2]]})


def get_pulse_json(code,date):
  data = urllib2.urlopen("https://api.pulseenergy.com/pulse/1/points/"+str(code)+"/data.json?key=A366D4672C54464D423656BD2D3DBAA3&interval=day&start="+date).read() 
  return data


def json_to_list(json):   
    list_out = []
    for x in json['data']:
      y = x.pop()
      list_out.append(y)
    return list_out

def main():

  now = datetime.datetime.now()
  query_date = now - timedelta(hours=8)
  query_date = query_date.strftime("%Y-%m-%dT%H:00-05:00")
  print query_date

  power_data = get_pulse_json(power,query_date)
  power_data = power_data.replace("null","-1")  
  power_dict = ast.literal_eval(power_data)
  power_list = json_to_list(power_dict)

  
  for i in range (0, power_list.count(-1)):
    power_list.remove(-1)

  radiation_data = get_pulse_json(radiation,query_date)
  radiation_dict = ast.literal_eval(radiation_data)
  radiation_list = json_to_list(radiation_dict)

  
  humidity_data = get_pulse_json(humidity,query_date)
  humidity_dict = ast.literal_eval(humidity_data)
  humidity_list = json_to_list(humidity_dict)


  temperature_data = get_pulse_json(temperature,query_date)
  temperature_dict = ast.literal_eval(temperature_data)
  temperature_list = json_to_list(temperature_dict)
  
  wind_data = get_pulse_json(wind,query_date)
  wind_dict = ast.literal_eval(wind_data)
  wind_list = json_to_list(wind_dict)


  
if __name__ == "__main__":
    main()