from converter import writeAttributes
def makeDict():
    files = {}
    files['names'] = "agaricus-lepiota.names"
    files['datafile'] = "agaricus-lepiota.data"    
    return files

def getFiles(c, filename, files):
    config = open(c, 'r')
    for line in  config:
        if line.split(',')[0] == filename:
                for key in files.keys():                    
                    files[key]= line.split(',')[1].strip() +  files[key]
                    temp = open(files[key], 'r')
                    files[key] = temp
                return files
    print "Filename not found in config"  
    return {}                

def getAttributes(f):
	processing = False
	classLabels = []
	attributes = {}
	l = []
	tempBool = True
	first = True
	for line in f:
		if line.split('.')[0]== '7':			
			processing = True 
		if processing and first:
			temp = line.split(':')[-1].split(',')
			for label in temp:
				temp_item = label.split('=')[1].strip().strip(')')
				classLabels.append(temp_item)
			tempBool = False
		if processing and not first:			
			attribute = line.split('.')[1].split(':')[0]			
			l.append(attribute)
			temp = line.split('.')[1].split(':')[1].split(',')
			temp2 = []			
			for item in temp:				
				temp_item = item.split('=')[1].strip()				
				temp2.append(temp_item)
			attributes[attribute] = temp2
		if line.split('.')[0].strip() ==  '22':
			processing = False
		first = tempBool
	return (l, attributes, classLabels)
def writeData(w, d):
    w.write("@data\n")
    for line in d:
    	line = line[2:].strip()  + ',' + line.split(',')[0] + '\n'
        w.write(line)
def convert(name):	
	files = makeDict()
	files = getFiles('config.txt', name, files)
	a = getAttributes(files['names'])
	w = open(name+'.arff', 'w')
	writeAttributes(w, a, name)
	writeData(w, files['datafile'])
	w.close()
	return
convert('mushroom')






