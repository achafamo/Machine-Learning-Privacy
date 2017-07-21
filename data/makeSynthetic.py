from random import randint

def addRandom(dataset, newfile, n):
	new = False
	finished = False
	for line in dataset:		
		if line.split('{')[0].strip() == '@attribute classLabels':						
			new = True
		if new and not finished:
			for i in range(n):
				string = '@attribute ' + str(i) + ' {0, 1}\n' 
				newfile.write(string)
			finished = True			
			newfile.write(line)
			continue
		if line.strip()== '':
			newfile.write(line)
			continue
		if line =='@data\n':
			newfile.write(line)		
			continue
		if not new:
			newfile.write(line) 

		if finished:
			temp = line.split(' ')[-1]
			datum = line.split(',')

			for i in range(n):
				val =  str(randint(0,1)) 
				temp = datum[-1]				
				datum.remove(temp)				
				datum.append(val)
				datum.append(temp)			
			line = (',').join(datum)
			newfile.write(line)			
	return 
def main_(name, n):
	dataset = open(name + '.arff', 'r')
	name = name  + '_new' +'.arff'
	newfile = open(name, 'w')
	addRandom(dataset, newfile, n)
main_('data/skin', 50)





