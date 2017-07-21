#from converter import writeAttributes
def makeDict():
    files = {}    
    files['datafile'] = "optdigits.tra"
    files['testfile'] = 'optdigits.tes'
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
	classLabels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	attributes = {}
	l = []
	for i in range(64):
	    l.append("exp_" +str(i))
	for attribute in l:
	    attributes[attribute] = "numeric"
	return (l, attributes, classLabels)
def writeAttributes(w, a, name):
    l, attributes, classLabels = a
    w.write("@relation " +  name +"\n")
    w.write("\n")
    #print attributes
    for attribute in l:
        w.write("@attribute " + attribute + " ")
        if not (attributes[attribute]=="numeric"):
            w.write("{")
            w.writelines([attributes.get(attribute)[i] + ","  for i in range(len(attributes.get(attribute))-1)])           
            w.write(attributes[attribute][-1].strip(')'))    
            w.write("}\n")
        else:
            w.write("numeric\n")
    w.writelines("@attribute classLabels {" )
    w.writelines([classLabels[i] + ", " for i in range(len(classLabels)-1)])
    w.write(classLabels[-1].strip())
    w.write('}\n')

    w.write("\n")


def writeData(w, d, t):
    w.write("@data\n")
    for line in d:
	w.write(line)
    for line in t:
        w.write(line)    	
     
def  convert(name):	
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()   
    files = getFiles('config.txt', name, files) 
    a = getAttributes()
    writeAttributes(w, a, name)   
    writeData(w, files['datafile'], files['testfile'])
    w.close()
    
convert('optdigits')
