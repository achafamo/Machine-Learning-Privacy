from converter import writeAttributes
def makeDict():
    files = {}    
    files['datafile'] = "ds1.10.csv"
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
def getAttributes():
	classLabels = ['0', '1']
	attributes = {}
	l = []
	for i in range(10):
	    l.append("exp_" +str(i))
	for attribute in l:
	    attributes[attribute] = "numeric"
	return (l, attributes, classLabels)
     

def writeData(w, d):
	w.write("@data\n")
	for line in d:
		w.write(line)	

    	
     
def  convert(name):	
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()   
    files = getFiles('config.txt', name, files) 
    a = getAttributes()
    writeAttributes(w, a, name)   
    writeData(w, files['datafile'])
    w.close()
    
convert('ds1.10')