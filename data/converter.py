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
    w.writelines("@attribute classLabels {" + classLabels[0] + ", " + classLabels[1] + "}\n")
    w.write("\n")
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

def getUniqueItems(l):
        '''
        returns a list of unique entries from the list l

        '''
       
        unique = set()
        for item in l:
            unique.add(l)
        return list(unique)
