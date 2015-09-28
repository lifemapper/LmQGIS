import simplejson
import csv

amphibJSONPath = '/home/jcavner/PhyloXM_Examples/amphibians_re_path2.json'
amphibDict = simplejson.loads(open(amphibJSONPath,'r').read())

mxCSV = '/home/jcavner/PhyloXM_Examples/african_amphib.csv'
amphibCSVDict = {}
with open(mxCSV, 'rb') as csvfile:
     amphibreader = csv.reader(csvfile, delimiter=',')
     # build a dictionary with name minus _EASE
     for row in amphibreader:
        amphibCSVDict[row[0].replace("_EASE",'')] = int(row[1])
        
print amphibCSVDict
print

match = {'c':0}
def recAmphibians(clade):
   if "children" in clade:
      for child in clade["children"]:
         recAmphibians(child)
   else:
      # this is a leaf
      if clade["name"] in amphibCSVDict:
         match['c'] += 1
         clade["mx"] = amphibCSVDict[clade["name"]]
      
recAmphibians(amphibDict)      
with open('/home/jcavner/PhyloXM_Examples/amphibian_mammal_testMX.json','w') as outfile:               
   simplejson.dump(amphibDict,outfile,indent=4)  
   
print match["c"]