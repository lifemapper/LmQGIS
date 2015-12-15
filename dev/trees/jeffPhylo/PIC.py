import os, sys
import simplejson as json
import numpy as np
import operator
from contextlib import contextmanager
import time


timerDict = {}

class Omega:
   
   def __init__(self,pam):
      """
      @param pam: numpy matrix of the PAM, compressed
      """
      self.pam = pam
      
   def hardWay(self):
      X = self.pam
      omegaMtx = np.dot(X.T,X)
      return omegaMtx

def makeInputsForTest(pam=None):
   # PAM and PIC from text
   if pam is None:
      # incidence matrix fromt the text
      I = np.array([[1, 0, 0, 1, 0, 0],
                    [0, 0, 1, 1, 0, 0],
                    [1, 0, 0, 1, 0, 1],
                    [0, 0, 1, 1, 0, 1],
                    [0, 1, 0, 1, 0, 1],
                    [0, 0, 0, 0, 1, 0],
                    [1, 0, 0, 0, 1, 0],
                    [0, 1, 0, 0, 1, 0]])
   else:
      I = pam
   # P from the text
   P = np.array([[-1.   , -0.5  , -0.25 , -0.125,  0.   ],
                 [ 1.   , -0.5  , -0.25 , -0.125,  0.   ],
                 [ 0.   ,  1.   , -0.5  , -0.25 ,  0.   ],
                 [ 0.   ,  0.   ,  1.   , -0.5  ,  0.   ],
                 [ 0.   ,  0.   ,  0.   ,  0.5  , -1.   ],
                 [ 0.   ,  0.   ,  0.   ,  0.5  ,  1.   ]])
   
   
   
   E = np.array([[1.3,  13.0, 100.0], 
                 [.78,  12.4, 121.0], 
                 [.85,  1.2,  99.0], 
                 [1.0,  0.98, 11.2], 
                 [4.8,  0.45,  21.23], 
                 [3.89, 0.99,  21.11], 
                 [3.97, 1.2,  12.01], 
                 [3.23, 1.0,  10.12] ])
   ########### experimental masks ###############
   # this was based on an idea for zeroing out
   # changes made by standardization
   PMask = np.array([[ 1.   , 1.   , 1. , 1.,  0.   ],
                     [ 1.   , 1.   , 1. , 1.,  0.   ],
                     [ 0.   , 1.   , 1. , 1.,  0.   ],
                     [ 0.   , 0.   , 1. , 1.,  0.   ],
                     [ 0.   , 0.   , 0. , 1. , 1.   ],
                     [ 0.   , 0.   , 0. , 1. , 1.   ]])
   
   PsigMask = np.array([[1,    1,    1,  1,  0   ],
                        [0,    1.,   1 , 1,  0   ],
                        [1,    1,    1,  1,  1   ],
                        [0,    1 ,   1 , 1 , 1   ],
                        [1,    1,    1,  1,  1   ],
                        [0,    0,    0,  1,  1   ],
                        [1,    1,    1,  1,  1   ],
                        [1,    1,    1,  1,  1   ]])
   ############################
   def calculateMarginals():
      
      siteCount = float(I.shape[0])
      siteVector = np.ones(siteCount)
      speciesCount = float(I.shape[1])
      speciesVector = np.ones(speciesCount)
      # range size of each species
      omega = np.dot(siteVector, I)
      # species richness of each site
      alpha = np.dot(I, speciesVector)
      
      Wk = np.diag(omega)
      
      Wn = np.diag(alpha)
      
      return Wk,Wn
      
   Wk, Wn = calculateMarginals()  # should call these something else
   
   #OmegaMtx = np.dot(I.T,I) # sites shared by species
   
   #AlphaMtx = np.dot(I,I.T) # species shared by sites
   
   return Wk,P,I,E,Wn
   
   
def standardizePIC(W=None,P=None,I=None,Ones=None):
   
   
   k1Col = Ones
   
   recipFill = 1.0/W.trace()
   PoverFill  = P * recipFill
   fillMinusOne = W.trace() - 1.0
   recipFillMinusOne = 1.0/fillMinusOne
   
   
   try:
      #num1 = P - np.dot(np.dot(k1Col*k1Col.T,O),PoverFill) # good
      num1 = np.dot(np.dot(k1Col*k1Col.T,W),PoverFill)
      
      #num1 = P - np.dot(k1Col*k1Col.T*O,PoverFill) # second best
      #print "m 1 s ",num1.shape
   except Exception,e:
      print "m 1 e ",str(e)
   
   ################
   print
   OneWP1 = np.dot(k1Col.T * W,P)  # returns a matrix
   #print "1 ",OneWP1
   OneWP2 = np.dot(np.dot(k1Col.T, W),P) # returns a vector
   
   #print
   #print "2 ",OneWP2
   ####################
   
   OneWPP1 = np.dot(np.dot(k1Col.T,W),(P*P)) # vector
   #print OneWPP1
   OneWPP2 = np.dot(k1Col.T*W,(P*P)) # matrix
   #print OneWPP2
   
   ####################
   # can rule out 2 - (1*1), division by zero
   # that leaves, 2 - (2*2) (bad), 1 - (1*1) (bad), 1 - (2*2)
   den = OneWPP1 - (np.dot((OneWP2*OneWP2),np.dot(recipFill,recipFillMinusOne))) 
   sqrtden = den**.5
   
   maybeden = np.dot(k1Col,sqrtden)

   #print "maybeden ",maybeden
   
   std = P - (num1 / maybeden)  
   
   
   return std


def models(PsigStdNode,Estd,Wn,Estd_i=None,Estd_mi=None):
   
   
   def i(myEstd,PsigStdByNode):
      
      # inverse of a matrix
      invX = np.linalg.inv(np.dot(np.dot(myEstd.T,Wn),myEstd))
      rightHand = np.dot(np.dot(myEstd.T,Wn),PsigStdByNode)
      
      return np.dot(invX,rightHand)
   
   
   #PsigStdNode = np.array([PsigStd[:,0]]).T
   # b = (XtX)^-1(Xty)
  
   BetaEjAll = i(Estd,PsigStdNode)  # all   shape - (3,5) without controling for one node
   
   BetaEji = i(np.array([Estd[:,2]]).T,PsigStdNode) # just i, shape - (1,5) without controling for one node
   
   BetaEjMinusi = i(Estd[:,[0,1]],PsigStdNode) # minus i, (2,5) without controling for one node
   
   
   
   return BetaEjAll, BetaEji, BetaEjMinusi

def BetaE_regression(PsigStd,Estd,Wn):
   
   def getPartModel(E):
      
      invX = np.linalg.inv(np.dot(np.dot(E.T,Wn),E))
      rightHand = np.dot(E.T,Wn)
      return np.dot(invX,rightHand)
   
   for i in range(0,Estd.shape[1]):
   
      Estd_i = np.array([Estd[:,i]]).T
      Estd_minus_i = np.delete(Estd,i,1)
      
      BjAll_part = getPartModel(Estd)
      Bji_part = getPartModel(Estd_i)
      Bjminus1_part = getPartModel(Estd_minus_i)
      
      print "column ",i," i"
      print
      
      for x in range(0,PsigStd.shape[1]):  # go through all the nodes/columns
         
         PsigStdNode = np.array([PsigStd[:,x]]).T
         
         #BetaEjAll, BetaEji, BetaEjMinusi = models(PsigStdNode, Estd, Wn)
         BetaEjAll = np.dot(BjAll_part,PsigStdNode)
         BetaEji = np.dot(Bji_part,PsigStdNode)
         BetaEjMinusi = np.dot(Bjminus1_part,PsigStdNode)
         
         
         
         #### estimate Y hat ###
         YjAll = np.dot(Estd,BetaEjAll)
         YjminusI = np.dot(Estd_minus_i,BetaEjMinusi)
         ###############
         
         
         #print "R^2 All ",np.trace(np.dot(YjAll.T,YjAll))/np.trace(np.outer(PsigStd.T,PsigStd.T))
         #print "R^2 minus i ", np.trace(np.dot(YjminusI.T,YjminusI)) / np.trace(np.outer(PsigStd.T,PsigStd.T))
         
         numDiffRsqr = np.trace(np.dot(YjAll.T,YjAll)) - np.trace(np.dot(YjminusI.T,YjminusI))
         
         diffRSqr = numDiffRsqr /  np.trace(np.outer(PsigStd.T,PsigStd.T))#  this wasn't a diagonal matrix - np.trace(PsigStd.T*PsigStd.T)
         
         if diffRSqr >= 0:
         
            num =  BetaEji*((diffRSqr)**.5)
         
            Pji = num/np.absolute(BetaEji)
         
            print "P(j,i), j = %s" % (x)
            print Pji
            print
            #
         else:
            pass
            print "negative R squared, node ",x
            print 
            
def vectorize_regression(PsigStd,Estd,Wn):
   
   def getR(col):
      
      PsigStdNode = np.array([col]).T
      
      #BetaEjAll, BetaEji, BetaEjMinusi = models(PsigStdNode, Estd, Wn)
      BetaEjAll = np.dot(BjAll_part,PsigStdNode)
      BetaEji = np.dot(Bji_part,PsigStdNode)
      BetaEjMinusi = np.dot(Bjminus1_part,PsigStdNode)
      
      
      
      #### estimate Y hat ###
      YjAll = np.dot(Estd,BetaEjAll)
      YjminusI = np.dot(Estd_minus_i,BetaEjMinusi)
      ###############
      
      
      #print "R^2 All ",np.trace(np.dot(YjAll.T,YjAll))/np.trace(np.outer(PsigStd.T,PsigStd.T))
      #print "R^2 minus i ", np.trace(np.dot(YjminusI.T,YjminusI)) / np.trace(np.outer(PsigStd.T,PsigStd.T))
      
      numDiffRsqr = np.trace(np.dot(YjAll.T,YjAll)) - np.trace(np.dot(YjminusI.T,YjminusI))
      
      diffRSqr = numDiffRsqr /  np.trace(np.outer(PsigStd.T,PsigStd.T))#  this wasn't a diagonal matrix - np.trace(PsigStd.T*PsigStd.T)
      
      if diffRSqr >= 0:
      
         num =  BetaEji*((diffRSqr)**.5)
      
         Pji = num/np.absolute(BetaEji)
      
         #print "P(j,i)"
         #print Pji
         #print
      
      else:
         pass
         #print "negative R squared, node "
         #print 
      return diffRSqr
   
   def getPartModel(E):
      
      invX = np.linalg.inv(np.dot(np.dot(E.T,Wn),E))
      rightHand = np.dot(E.T,Wn)
      return np.dot(invX,rightHand)
   
   for i in range(0,Estd.shape[1]):
   
      Estd_i = np.array([Estd[:,i]]).T
      Estd_minus_i = np.delete(Estd,i,1)
      
      BjAll_part = getPartModel(Estd)
      Bji_part = getPartModel(Estd_i)
      Bjminus1_part = getPartModel(Estd_minus_i)
      
      
      np.apply_along_axis(getR, 0, PsigStd)

   
def startHere(Phylo=None,Pam=None):
   
   Wk,P,I,E,Wn = makeInputsForTest(pam=Pam)  # may or may not use these masks
   
   if Phylo is not None and Pam is not None:
      P = Phylo # comment out when not sending PAM from __main__
      I = Pam   # comment out when not sending PAM from __main__
   # std P
   Ones = np.array([np.ones(I.shape[1])]).T # column vector
   Pstd = standardizePIC(Wk, P, I, Ones)
   
   print "Psig non standardized"
   print np.dot(I,P)
   #Pstd = PstdunMasked * PMask # zeroing out changes made during standardization
   
   PsigStd = np.dot(I,Pstd)
   
   # std E
   Ones = np.array([np.ones(I.shape[0])]).T
   Estd = standardizePIC(Wn, E, I, Ones)
   
   BetaE_regression(PsigStd,Estd,Wn)
   
   #st = time.clock()
   #for s in range(0,10000):
   #   vectorize_regression(PsigStd,Estd,Wn)
   #end = time.clock()
   #avg = (end - st)/10000
   #print avg
   #for x in range(0,10000):
   #   with timer('%s' % x):
   #      #vectorize_regression(PsigStd,Estd,Wn)
   #      BetaE_regression(PsigStd,Estd,Wn)
   #sum = 0
   #for k in timerDict.keys():
   #   sum = sum + timerDict[k]
   #print sum
   #avg = sum / 10000   
   #print "AVG ",avg
   
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
   noMx = {'c':0}
   tips = []
   internal = {}
   def buildLeaves(clade):
      if "children" in clade: 
         if len(clade["children"]) > 2:
            print "polytomy ",clade["pathId"]
         internal[clade["pathId"]] = clade["children"][0] 
         for i,child in enumerate(clade["children"]):
            
            buildLeaves(child)
      else: 
         #castClade = clade.copy()
         #castClade["mx"] = int(castClade["mx"]) # if not in PAM, under if statement
         #tips.append(castClade)  # this assumes all tips are in PAM
         if "mx" in clade:  ## might want append to tips under this
            castClade = clade.copy()
            castClade["mx"] = int(castClade["mx"]) # if not in PAM, under if statement
            tips.append(castClade)
         else:
            # pad for tips not in pam
            #noMx['c'] = noMx['c'] + 1
            #print '"'+clade['name']+'",'
            #pass
            castClade = clade.copy()
            castClade['mx'] = 999  # some fake number
            tips.append(castClade)
   buildLeaves(clade)  
   print noMx
   tips.sort(key=operator.itemgetter('mx'))   # what if mx is string, like 
   # in this case 
   
   return tips, internal


# ...............................
def oneSide(internal):
   """
   @summary: takes dict of interal nodes from one side of the phylogeny
   returns dict of lists of ids the descend from parent on that branch,
   key is parent pathId
   """
   negDict = {}
   for k in internal:
      l = negs(internal[k])
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
            #sL.append(child["pathId"])
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
      # this wont work because it's based on tips
      # and the tips come from build tips which is conditioned
      # on mx and therefore presence in pam
      total = (len(tipIds) * 2) - 1 # assumes binary tree
      allIds = [x for x in range(0,total)]
      internalIds = list(set(allIds).difference(set(tipIds)))
   else:
      internalIds = [int(k) for k in internalDict.keys()]
      internalIds.sort()
   return tipIds,internalIds
   

def buildMatrix(emptyMtx, internalIds, tipsDictList, whichSide):
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
   
@contextmanager
def timer(label):
   start = time.clock()
   try:
      yield
   finally:
      end = time.clock()
      #print ('{} : {}'.format(label, end - start))
      timerDict[label] = end - start


if __name__ == "__main__":
   
   jsP = "/home/jcavner/PhyloXM_Examples/"
   #jsP = "/home/jcavner/TASHI_PAM/"
   #fN = "Liebold.json"
   fN = "Liebold_notEverythinginMatrix.json"
   #fN = 'tree.json'
   path = os.path.join(jsP,fN)
   d = loadJSON(path)
   tips,whichSide = buildTips(d)
   negsDict = oneSide(whichSide)
   tipIds,internalIds = getIds(tips,internalDict=whichSide)
   matrix = initMatrix(len(tipIds),len(internalIds))
   m = buildMatrix(matrix,internalIds,tips, negsDict)
   print m.shape
   # loop through cols.of m and check sum
   print
   print m
   print 
   count = 0
   for x in range(0,m.shape[1]):
      s = m[:,x].sum()
      if s <> 0:
         count = count + 1
         #print "not zero ",m[:,x]
         #break
   #print count
                             # this column holds the key
   pam = np.array([[1, 0, 0, 0, 0, 0,],
                   [0, 0, 1, 0, 0, 1,],
                   [1, 0, 0, 0, 0, 0,],
                   [0, 0, 1, 0, 0, 1,],
                   [0, 1, 0, 1, 1, 0,],
                   [0, 0, 0, 0, 0, 0,],
                   [1, 0, 0, 0, 0, 0,],
                   [0, 1, 0, 1, 1, 0,]])
                                   # did this column too
                                # didn't do middle column, how is it working? or is it?
   #[-0.125 -0.25  -0.5    1.     0.   ]
   #[-0.5    1.     0.     0.     0.   ]
   #[ 0.5    0.     0.     0.     1.   ]]
   
   #############
   #pamPath = os.path.join(jsP,'pam_2462.npy')
   #pam = np.load(pamPath)
   
   #m = [[-0.125, -0.25,  -0.5,   -1.,     0.   ],
   #     [-0.25 , -0.5 ,   1. ,    0.,     0.   ],
   #     [ 0.5  ,  0.  ,   0. ,    0.,    -1.   ],
   #     [-0.125, -0.25,  -0.5,    1.,     0.   ],
   #     [-0.5  ,  1.  ,   0. ,    0.,     0.   ],
   #     [ 0.5  ,  0.  ,   0. ,    0.,     1.   ]]
   
   P =  np.dot(pam,m)
   print P
   #startHere(Phylo=m,Pam=pam)
   
   #startHere()
   

   