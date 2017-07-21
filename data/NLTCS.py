#from converter import writeAttributes
def makeDict():
    files = {}    
    files['datafile'] = "2to16disabilityNLTCS.txt"
    return files
def getFiles(c, filename, files):
    config = open(c, 'r')

    for line in  config:    	
        print line.split(',')[0],  filename
        if line.split(',')[0] == filename:        	
                for key in files.keys():                    
                    files[key]= line.split(',')[1].strip() +  files[key]                
                    temp = open(files[key], 'r')
                    files[key] = temp
                return files
    print "Filename not found in config"  
    return {}               
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
    #w.writelines("@attribute classLabels {" + classLabels[0] + ", " + classLabels[1] + "}\n")
    w.write("\n")
def getAttributes(datafile):
    attributes = {}
    line  = datafile.readline()
    l = line.split()[:-2]
    for item in l:
        attributes[item] = ['0','1']
    classLabels = ['0','1']
    return (l, attributes, classLabels)
def writeData(w, datafile):
    w.write('@data\n')
    first = True
    for line in datafile:
        if not first:
            count = int(line.split()[-2])
            temp = line.split()[:-2]
            line = ' ,'.join(temp) + '\n'
            for i in range(count):
                w.write(line)
        if first:
            first = False
def convert(name):
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()
    files = getFiles('config.txt', name, files)
    a = getAttributes(files['datafile'])    
    writeAttributes(w, a, name)
    writeData(w, files['datafile'])
    w.close()
    return
convert('NLTCS')


