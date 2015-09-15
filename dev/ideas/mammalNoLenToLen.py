
import simplejson
import os

NoLenLeaves =  {} #WITH MX
LengthLeaves = {}

def recNoLenMammals(clade):
   
  
   if "children" in clade:
      for child in clade["children"]:
         recNoLenMammals(child)
      
   else:
      NoLenLeaves[clade["name"]] = clade 
      
def recLenMammals(clade):
   
  
   if "children" in clade:
      for child in clade["children"]:
         recLenMammals(child)
      
   else:
      LengthLeaves[clade["name"]] = clade 

base = "/home/jcavner/PhyloXM_Examples"
NoLenFile = "african_mammal_realDealMX.json"  # WITH MX
LenFile = "mammalsWithLengths.json"
mammalsDictNoLen = simplejson.loads(open(os.path.join(base,NoLenFile),'r').read())
mammalsDictLen = simplejson.loads(open(os.path.join(base,LenFile),'r').read())

recNoLenMammals(mammalsDictNoLen)
recLenMammals(mammalsDictLen)


for k,v in NoLenLeaves.items():
   if v.has_key("mx"):
      LengthLeaves[k]["mx"] = v["mx"]
      

with open('/home/jcavner/PhyloXM_Examples/mammalsWithLengthsandMX.json','w') as f:
   f.write(simplejson.dumps(mammalsDictLen,sort_keys=True, indent=4))    