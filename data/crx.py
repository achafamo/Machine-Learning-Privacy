def makeDict():
    files = {}
    files['names'] = 'crx.names'
    files['datafile'] = 'crx.data'
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
def writeData(w, d):
    w.write("@data\n")
    for line in d:
        w.write(line)
def writeAttributes(w, a, name):	
    l, attributes, classLabels = a
    w.write("@relation " +  name +"\n")
    w.write("\n")
    
    for attribute in l:
        w.write("@attribute " + attribute + " ")       
        if not (attributes[attribute]=="continuous"):        	
            w.write("{")
            w.writelines([attributes.get(attribute)[i].strip() + ","  for i in range(len(attributes.get(attribute))-1)])           
            w.write(attributes[attribute][-1].strip('.\n'))    
            w.write("}\n")
        else:        	
            w.write("numeric\n")    
    w.writelines("@attribute classLabels {" + classLabels[0].strip() + ", " + classLabels[1].strip() + "}\n")
    w.write("\n")
def getAttributes(names):
	l = []
	attributes = {}
	classLabels = []
	last = False
	start = False
	for line in names:
		if start and line.strip()!= '':
			l.append(line.split(':')[0].strip())			
			if line.split(':')[1].strip() != 'continuous.':
				attributes[line.split(':')[0].strip()] = line.split(':')[1].split(',')
			else:				
				attributes[line.split(':')[0].strip()] = 'continuous'
		if line.split('.')[0] == '7':
			start = True
		if last:
			classLabels = (line.split('(')[0].split(':')[1].split(','))			
			last = False
			break
		if start and line.split(':')[0].strip() == 'A15':			
			start = False
			last = True
	return (l,  attributes, classLabels)
		
def convert(name):
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()
    files = getFiles('config.txt', name, files)    
    a = getAttributes(files['names'])	
    files['datafile'].close()  
    files = makeDict()
    files = getFiles('config.txt', name, files)  
    writeAttributes(w, a, name)
    writeData(w, files['datafile'])
    w.close()
    return
convert('crx')