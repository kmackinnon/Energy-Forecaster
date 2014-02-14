import csv
import math

actualValues=[]
predictedValues=[]

def main():
	global actualValues
	global predictedValues
	
	actualValues = outReader('sample_output.txt')
	predictedValues = outReader('output.csv')
	
	error=errorCalculator()
	print str((1 - error) * 100) + "% confidence"

def outReader(file):
	f=open(file, 'rb')
	f.next()
	f.next()
	f.next()
	f.next()
  
	dictReader=csv.DictReader(f, fieldnames=['Date', 'Energy'], delimiter=',', quotechar='"')
  
	values = []
	for row in dictReader:
		for key in row:
			if (key=='Energy'):
				values.append(row[key])
	return values

def errorCalculator():
	error=0
	
	AV=[float(numeric_string) for numeric_string in actualValues]
	PV=[float(numeric_string) for numeric_string in predictedValues]
	
	for i in range(0,len(AV)):
		error=error+math.pow((PV[i]-AV[i])/AV[i], 2)
	error=error/len(AV)
	error=math.pow(error, 0.5)
	return error

if __name__ == "__main__":
    main()
