from converter import writeAttributes
def makeDict():
    files = {}
    files['names'] = "adult.names"
    files['datafile'] = "adult.data"
    files['testfile'] = "adult.test"    
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
    classLabels = []
    attributes = {}
    l = []
    for line in f:
        if line[0]!=  "|" and line != '\n':
            line = line[0:-2]
            if first:
                classLabels = line.split(',')
                first = False
            else:       
                temp = line.split(":")           
                values = "numeric"           
                if temp[1].strip()!= "continuous":
                    values = temp[1].split(",")
                l.append(temp[0])
                attributes[temp[0]]= values
    f.close()
    return (l, attributes, classLabels)

    
def writeData(w, d, t):
    w.write("@data\n")
    for line in d:
        w.write(line)
    for line in t:
        if line[0]!="|":
            w.write(line[0:-2] + "\n")
    return 


def convert(name):
    newfile = name + '.arff'
    w = open(newfile, 'w')
    files = makeDict()
    files = getFiles('config.txt', name, files)    
    a = getAttributes(files['names'])   
    x,y,z = a
    print x 
    writeAttributes(w, a, name)
    writeData(w, files['datafile'], files['testfile'])
    w.close()
    return

convert('adult')
