import numpy as np
import csv
import requests
from sklearn.svm import SVR
from django.http import HttpRequest
from django.http import HttpResponse
from .forms import UploadFileForm
from django.core.files import File

#Author: Adam

# weather interpolation
def interpolate(input):
  # generate xs and ys for polyfit
  x = []
  y = []
  
  if input[0] != "":
    starts_at = 0
  elif input[1] != "":
    starts_at = 1
  elif input[2] != "":
    starts_at = 2
  elif input[3] != "":
    starts_at = 3
  
  for i in range(len(input)):
    if i % 4 != starts_at:
      continue
    input[i] = float(input[i])
    x.append(float(i))
    y.append(float(input[i]))

  xs = np.array(x)
  ys = np.array(y)

  # piecewise function for weather data interpolation (3 6th degree + 1 5th degree polyfit functions)
  f = lambda z: (np.poly1d(np.polyfit(xs[:7], ys[:7], 6)))(z) if 0 <= z <= 23  else ((np.poly1d(np.polyfit(xs[6:13], ys[6:13], 6)))(z) if 24 <= z <= 47 else ((np.poly1d(np.polyfit(xs[12:19], ys[12:19], 6)))(z) if 48 <= z <= 71  else ((np.poly1d(np.polyfit(xs[18:], ys[18:], 5)))(z) if 72 <= z <= 95 else None)))

  for k in range(len(input)):
    if k % 4 == starts_at:
      continue
    input[k] = f(float(k))

def machinelearning(csv_file):
  # parse CSV
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

  # interpolate weather data
  interpolate(d['radiation'])
  interpolate(d['humidity'])
  interpolate(d['temperature'])
  interpolate(d['wind'])

  # train machine learning algorithm
  training_x = np.array(zip(d['radiation'], d['humidity'], d['temperature'], d['wind'])[:32])
  training_y = np.array(d['demand'][:32])

  poly_svr = SVR(kernel='poly', degree=2)
  poly_svr.fit(training_x, training_y)

  prediction_x = np.array(zip(d['radiation'], d['humidity'], d['temperature'], d['wind'])[32:])
  demand_predictions = poly_svr.predict(prediction_x)

  return demand_predictions

def (request):
  if request.method == 'POST':
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
      # print file back to client
      response = HttpResponse(content_type='text/plain')
      for line in file:
        response.write(line)
