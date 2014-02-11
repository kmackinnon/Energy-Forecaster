import csv
import math

actualValues=[]
predictedValues=[]

def main():
  AVreader()
  PVreader()
  error=errorCalculator()
  print error

def AVreader():
  f=open('test_data_set.csv', 'rb')
  f.next()
  
  dictReader=csv.DictReader(f, fieldnames=['Date', 'Radiation', 'Humidity', 'Temperature','Wind Speed', 'Energy'], delimiter=',', quotechar='"')
  for row in dictReader:
    for key in row:
      if (key=='Energy'):
        actualValues.append(row[key])


def PVreader():
  f=open('sample_output.txt', 'rb')
  f.next()
  f.next()
  f.next()
  f.next()
    
  dictReader=csv.DictReader(f, fieldnames=['Date','Energy'], delimiter=',', quotechar='"')
  for row in dictReader:
    for key in row:
      if (key=='Energy'):
        predictedValues.append(row[key])

def errorCalculator():
  error=0
  
  AV=[float(numeric_string) for numeric_string in actualValues]
  PV=[float(numeric_string) for numeric_string in predictedValues]
  
  for i in range(len(AV)):
    error=error+math.pow((AV[i]-PV[i]), 2)
  error=error/len(AV)
  error=math.pow(error, 0.5)
  return error

if __name__ == "__main__":
    main()
