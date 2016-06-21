import os, sys
import simplejson as json
import cPickle
import numpy as np
import operator
import collections
from contextlib import contextmanager
np.seterr(all='warn')  # for divide by zero 






##############  tree  ###################
# ........................................
def makeP(treeDict,I,branchLengths=False):
   """
   @summary: encodes phylogeny into matrix P and checks
   for sps in tree but not in PAM (I), if not in PAM, returns
   new PAM (I) in addition to P
   """
   ######### make P ###########
   tips, internal, tipsNotInMtx, lengths = buildTips(treeDict,I.shape[1])
   if branchLengths:
      sides = getSides(internal,lengths)
      P = buildP_WithBranch(sides) 
   else:
      negsDict = processInternalNodes(internal)
      tipIds,internalIds = getIds(tips,internalDict=internal)
      matrix = initMatrix(len(tipIds),len(internalIds))
      P = buildPMatrix(matrix,internalIds,tips, negsDict)
   
   if len(tipsNotInMtx) > 0:
      I = processTipNotInMatrix(tipsNotInMtx, internal, I)
      
   return P, I, internal
# ........................................
   
def buildTips(clade, noColPam): 
   """
   @summary: flattens to tips and return list of tip clades(dicts)
   unsure how calculations would reflect/change if more tips in tree
   than in PAM.  If it does it needs to check for matrix key
   @param noColPam: at what point does this arg get set/sent, compression to consider !!!!!!!
   """ 
   
      
   noMx = {'c':noColPam}  # needs to start with last sps in pam
   tips = []
   tipsNotInMatrix = []
   internal = {}
   lengths = {}
   def buildLeaves(clade):
   
      if "children" in clade: 
         #### just a check, probably take out 
         if "length" in clade:
            lengths[int(clade["pathId"])] = float(clade["length"])
         if len(clade["children"]) > 2:
            print "polytomy ",clade["pathId"]
         ############    
         internal[clade["pathId"]] = clade["children"] # both sides
         for child in clade["children"]:  
            buildLeaves(child)
      else: 
         if "mx" in clade: 
            castClade = clade.copy()
            #if layersPresent is not None:
            #   if layersPresent[int(clade['mx'])]:
            #      castClade["mx"] = sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])
            #      tips.append(castClade)
            #   else:
            #      pass
            #else:
            castClade["mx"] = int(castClade["mx"])
            tips.append(castClade)
            
         else:
            castClade = clade.copy()
            castClade['mx'] = noMx['c']  # assigns a mx starting at end of pam
            tips.append(castClade)
            tipsNotInMatrix.append(castClade)
            noMx['c'] = noMx['c'] + 1
         if "length" in clade:
            lengths[int(clade["pathId"])] = float(clade["length"])   
   buildLeaves(clade)  
   tips.sort(key=operator.itemgetter('mx'))   
   tipsNotInMatrix.sort(key=operator.itemgetter('mx'))
   return tips, internal, tipsNotInMatrix, lengths


# ..........................
def getSiblingsMx(clade):
   """
   @summary: gets all tips that are siblings that are in PAM, (have 'mx')
   """
   
   mx = []
   def getMtxIds(clade):
      if "children" in clade:
         for child in clade['children']:
            getMtxIds(child)
      else:
         if "mx" in clade:
            #if layersPresent is None:
            mx.append(int(clade["mx"]))
            #else:
            #   compressedMx = sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])
            #   mx.append(compressedMx)
   getMtxIds(clade)
   return mx
# ..........................
def processTipNotInMatrix(tipsNotInMtx,internal,pam):
   """
   @param tipsNotInMtx: list of tip dictionaries
   @param internal: list of internal nodes made in buildTips
   """  
   
   mxMapping = {} 
   for tip in tipsNotInMtx:
      parentId = [x for x in tip["path"].split(",")][1]  
      parentsChildren = internal[parentId]#['children']  
      for sibling in parentsChildren:
         if tip['pathId'] != sibling['pathId']:
            # not itself
            if 'children' in sibling:
               # recurse unitl it get to tips with 'mx'
               mxs = getSiblingsMx(sibling)
               mxMapping[int(tip['mx'])] = mxs
            else:
               if "mx" in sibling:
                  #if layersPresent is None:
                  mxMapping[int(tip['mx'])] = [int(sibling['mx'])]
                  #else:
                  #   mxMapping[int(tip['mx'])] = sum([x[1] for x in lPItems[:int(sibling["mx"])] if x[1]])
               else:
                  mxMapping[int(tip['mx'])] = 0
   la = [] # list of arrays              
   for k in sorted(mxMapping.keys()):
      if isinstance(mxMapping[k],list):
         
         t = np.take(pam,np.array(mxMapping[k]),axis = 1)
         b = np.any(t,axis = 1)  #returns bool logical or
      else:
         b = np.ones(pam.shape[0],dtype=np.int)
      la.append(b)
   newPam = np.append(pam,np.array(la).T,axis=1)
   return newPam
# ...............................
def processInternalNodes(internal):
   """
   @summary: takes dict of interal nodes from one side of the phylogeny
   returns dict of lists of ids that descend from parent on that branch,
   key is parent pathId
   """
   negDict = {}
   for k in internal:
      #l = negs(internal[k])  #for when one side is captured in buildTips
      l = negs(internal[k][0]) # for when all children are attached to internal
      negDict[str(k)] = l  # cast key to string, Dec. 10, 2015
      # since looked like conversion to json at one point wasn't converting
      # pathId 0 at root of tree to string
   return negDict

# ..........................      
def negs(clade):
   sL = []
   def getNegIds(clade):    
      if "children" in clade:
         sL.append(int(clade["pathId"]))
         for child in clade["children"]:
            getNegIds(child)
      else:
         sL.append(int(clade["pathId"]))
   getNegIds(clade)
   return sL

# ..........................................   
def initMatrix(rowCnt,colCnt):
   return np.empty((rowCnt,colCnt))
# ..........................................
def getIds(tipsDictList,internalDict=None):
   """
   @summary: get tip ids and internal ids
   """
   
   tipIds = [int(tp["pathId"]) for tp in tipsDictList ]
   if internalDict is None:
      
      total = (len(tipIds) * 2) - 1 # assumes binary tree
      allIds = [x for x in range(0,total)]
      internalIds = list(set(allIds).difference(set(tipIds)))
   else:
      internalIds = [int(k) for k in internalDict.keys()]
      internalIds.sort()
   #print "from getIDs ",len(tipIds)," ",len(internalIds)  # this is correct
   return tipIds,internalIds
   

def buildPMatrix(emptyMtx, internalIds, tipsDictList, whichSide):
   #negs = {'0': [1,2,3,4,5,6,7], '2': [3, 4, 5], '1':[2,3,4,5,6],
   #        '3':[4],'8':[9]}
   negs = whichSide
   for ri,tip in enumerate(tipsDictList):
      newRow = np.zeros(len(internalIds),dtype=np.float)
      pathList = [int(x) for x in tip["path"].split(",")][1:]
      tipId = tip["pathId"]
      for i,n in enumerate(pathList):
         m = 1
         #print n
         if int(tipId) in negs[str(n)]:
            m = -1
         idx = internalIds.index(n)
         newRow[idx] = (.5**i) * m
      emptyMtx[ri] = newRow  
   
   return emptyMtx  


def getSides(internal,lengths):
   """
   has to have complete lengths
   """
   def goToTip(clade):
      
      if "children" in clade:
         lengthsfromSide.append(float(clade["length"]))
         for child in clade["children"]:
            goToTip[clade["children"]]
      else:
         # tips
         lengthsfromSide.append(float(clade["length"]))
   # for each key (pathId) in internal recurse each side
   sides = {}
   for pi in internal:
      sides[pi] = {}
      lengthsfromSide = []
      goToTip(internal[pi][0])
      sides[pi][0] = lengthsfromSide
      
      lengthsfromSide = []
      goToTip(internal[pi][1])
      sides[pi][1] = lengthsfromSide
   return sides

def buildP_WithBranch(sides):
   pass

def buildP_WithBranch_dep(emptyMtx, internalIds, tipsDictList, whichSide, lengths):
   #negs = {'0': [1,2,3,4,5,6,7], '2': [3, 4, 5], '1':[2,3,4,5,6],
   #        '3':[4],'8':[9]}
   negs = whichSide
   for ri,tip in enumerate(tipsDictList):
      newRow = np.zeros(len(internalIds),dtype=np.float)
      pathList = [int(x) for x in tip["path"].split(",")] #[1:]
      tipId = tip["pathId"]
      toSum = []
      for i,n in enumerate(pathList):
         m = 1
         #print n
         if int(tipId) in negs[str(n)]:
            m = -1
         den = i + 1.0
         toSum.append(lengths[n]/den)
         #idx = internalIds.index(n)
         #newRow[idx] = (.5**i) * m
      s = sum(toSum)
      emptyMtx[ri] = newRow  
   
   return emptyMtx

if __name__ == "__main__":
   
   tree = {"name": "0",
           "path": "0",
           "pathId": "0",
           "children":[
                       {"pathId":"1","length":".4","path":"1,0",
                       "children":[
                                   {"pathId":"2","length":".15","path":"9,5,0",
                                    "children":[
                                                {"pathId":"3","length":".65","path":"3,2,1,0",
                                                 
                                                 "children":[
                                                             {"pathId":"4","length":".2","path":"4,3,2,1,0"},
                                                             {"pathId":"5","length":".2","path":"5,3,2,1,0"}
                                                             ]
                                                 
                                                 },
                                                
                                                {"pathId":"6","length":".85","path":"6,2,1,0"}
                                                
                                                ]
                                    
                                    },
                                    {"pathId":"7","length":"1.0","path":"7,1,0"}
                                   
                                   ] },
                       

                       {"pathId":"8","length":".9","path":"8,0",
                        "children":[{"pathId":"9","length":".5","path":"9,5,0"},{"pathId":"10","length":".5","path":"10,5,0"}] } 
                       ]
           
           }



