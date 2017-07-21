from converter import writeAttributes
def makeDict():
    files = {}
    files['names'] = "bank-names.txt"
    files['datafile'] = "bank-full.csv"     
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
	first = True
	classLabels = ['"yes"', '"no"']
	attributes = {}
	l = []
	parse = False
	for line in f:
	    if line.strip() == '\n' and parse:
	    	print 'here'
	        parse = False
	    if parse and line.strip()[0]!= "#":
	        temp = line.split(' - ')	        
	        temp2 = temp[1].split(':')
	        if len(temp2)>2:
	            attributes[temp2[0].strip()]= temp2[2][0:-2].strip().split(',')
	            l.append(temp2[0].strip())
	        else:
	            attributes[temp2[0]] = "numeric"
	            l.append(temp2[0])
	    
	    if len(line.strip())>0 and line.strip()[0] == "#":
	       parse = True
	    if parse and line.strip()[0:2] == '16':
	    	parse = False
	f.close()
	return (l, attributes, classLabels)


def writeData(w, d):
    w.write("@data\n")    
    for line in d:
    	if line[0]!= '\"':
    		line = line.replace(';', ',')
        	w.write(line)
    return 
def convert(name):
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()
    files = getFiles('config.txt', name, files)
    a = getAttributes(files['names'])    
    writeAttributes(w, a, name)
    writeData(w, files['datafile'])
    w.close()
    return
convert('bank')

