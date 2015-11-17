import os, sys
import simplejson as json
import numpy as np
import operator



def loadJSON(path):
   
   with open(path,'r') as f:
      jsonstr = f.read()
   return json.loads(jsonstr)

   
   
def buildTips(clade): 
   """
   @summary: flattens to tips and return list of tip clades(dicts)
   unsure how calculations would reflect/change if more tips in tree
   than in PAM.  If it does it needs to check for matrix key
   """ 
   tips = []
   internal = {}
   def buildLeaves(clade):
      if "children" in clade: 
         internal[clade["pathId"]] = clade["children"][0] 
         for i,child in enumerate(clade["children"]):
            
            buildLeaves(child)
      else: 
         castClade = clade.copy()
         castClade["mx"] = int(castClade["mx"]) # if not in PAM, under if statement
         tips.append(castClade)  # this assumes all tips are in PAM
         if "mx" in clade:  ## might want append to tips under this
            pass
   buildLeaves(clade)  
   tips.sort(key=operator.itemgetter('mx'))   # what if mx is string, like 
   # in this case 
   
   return tips, internal


# ...............................
def oneSide(internal):
   negDict = {}
   for k in internal:
      l = negs(internal[k])
      negDict[k] = l
      
   return negDict
           
# ..........................      
def negs(clade):
   sL = []
   def getNegIds(clade):
      
      if "children" in clade:
         sL.append(int(clade["pathId"]))
         for child in clade["children"]:
            #sL.append(child["pathId"])
            getNegIds(child)
      else:
         sL.append(int(clade["pathId"]))
   getNegIds(clade)
   return sL
   
def initMatrix(rowCnt,colCnt):
   return np.empty((rowCnt,colCnt))



def getIds(tipsDictList):
   
   tipIds = [int(tp["pathId"]) for tp in tipsDictList ]
   total = (len(tipIds) * 2) - 1
   allIds = [x for x in range(0,total)]
   internalIds = list(set(allIds).difference(set(tipIds)))
   return tipIds,internalIds
   

def buildMatrix(emptyMtx,internalIds, tipsDictList, whichSide):
   #negs = {'0': [1,2,3,4,5,6,7], '2': [3, 4, 5], '1':[2,3,4,5,6],
   #        '3':[4],'8':[9]}
   
   negs = whichSide
   for ri,tip in enumerate(tipsDictList):
      newRow = np.zeros(len(internalIds),dtype=np.float)
      pathList = [int(x) for x in tip["path"].split(",")][1:]
      tipId = tip["pathId"]
      for i,n in enumerate(pathList):
         m = 1
         if int(tipId) in negs[str(n)]:
            m = -1
         idx = internalIds.index(n)
         newRow[idx] = (.5**i) * m
      emptyMtx[ri] = newRow  
   
   return emptyMtx      
   
   





if __name__ == "__main__":
   
   jsP = "/home/jcavner/PhyloXM_Examples/"
   fN = "Liebold.json"
   path = os.path.join(jsP,fN)
   d = loadJSON(path)
   tips,whichSide = buildTips(d)
   negsDict = oneSide(whichSide)
   tipIds,internalIds = getIds(tips)
   matrix = initMatrix(len(tipIds),len(internalIds))
   m = buildMatrix(matrix,internalIds,tips, negsDict)
   print
   print 
   print m

   