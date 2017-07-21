from converter import getUniqueItems, writeAttributes

def makeDict():
    files = {}
    files['names'] = 'kddcup.names'
    files['datafile'] = 'kddcup.data'
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
        w.write(line[0:-2]  + '\n') 

def getValues(l,d):
    ''' takes in a list of attributes and returns a dictionary with the values associated for each attribute'''
    attributes = {}    
    for attribute in l:
        unique = set()
        attributes[attribute]= unique
    for line in d:
        temp = line.split(',')
        for i in range(len(l)):
            val = attributes[l[i]]
            if temp[i][0]=='[':            
                val.add(temp[i]) 
            else:
                val = 'numeric'           
            attributes[l[i]] = val   
    for attribute in l:            
        attributes[attribute] = list(attributes[attribute])
    return attributes

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
    w.write(classLabels[-1][:-2].strip())
    w.write('}\n')

    w.write("\n")

def getAttributes(names, data):
    first = True 
    attributes = {}
    l = []
    for line in names:
        
        if first:
            classLabels = line.split(',')
            first = False
        else:
           
            l.append(line.split(':')[0])
            attributes[line.split(':')[0]] = line.split(':')[1].strip()
    temp = getValues(l, data)
    for attribute in l:
        if attributes[attribute] == "symbolic.":
            attributes[attribute] = temp[attribute]
        else:
            attributes[attribute] = "numeric"
    return (l,attributes, classLabels)

def convert(name):
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()
    files = getFiles('config.txt', name, files)    
    a = getAttributes(files['names'], files['datafile'])  
    files['datafile'].close()  
    files = makeDict()
    files = getFiles('config.txt', name, files)  
    writeAttributes(w, a, name)
    writeData(w, files['datafile'])
    w.close()
    return
convert('kddcup')


