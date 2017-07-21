from converter import writeAttributes
def makeDict():
    files = {}    
    files['datafile'] = "US.csv"
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

def writeData(w, data):
    first = True     
    w.write('@data\n')    
    for line in data:
        if not first:        
            w.write(line)
        else:
            first = False
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
        if attributes[attribute] != 'numeric':
            attributes[attribute] = list(attributes[attribute])
    return attributes
def getAttributes(data):
    attributes = {}
    line = data.readline()
    l = line.split(',')
    l = l[:-1]
   
    attributes = getValues(l, data)
    classLabels = ['<=50K', '>50K']
   
    return (l, attributes, classLabels)
def convert(name):
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()    
    files = getFiles('config.txt', name, files)   
    a = getAttributes(files['datafile']) 
    x,y,z = a
    print y  
    writeAttributes(w, a, name)
    files = makeDict()    
    files = getFiles('config.txt', name, files)
    writeData(w, files['datafile'])
    w.close()
    return
convert('US')