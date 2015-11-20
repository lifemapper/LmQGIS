import os, sys
import simplejson as json
import numpy as np
import operator

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

def makeInputsForTest():
   # PAM and PIC from text
   I = np.array([[1, 0, 0, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [1, 0, 0, 1, 0, 1],
                 [0, 0, 1, 1, 0, 1],
                 [0, 1, 0, 1, 0, 1],
                 [0, 0, 0, 0, 1, 0],
                 [1, 0, 0, 0, 1, 0],
                 [0, 1, 0, 0, 1, 0]])
   
   P = np.array([[-1.   , -0.5  , -0.25 , -0.125,  0.   ],
                 [ 1.   , -0.5  , -0.25 , -0.125,  0.   ],
                 [ 0.   ,  1.   , -0.5  , -0.25 ,  0.   ],
                 [ 0.   ,  0.   ,  1.   , -0.5  ,  0.   ],
                 [ 0.   ,  0.   ,  0.   ,  0.5  , -1.   ],
                 [ 0.   ,  0.   ,  0.   ,  0.5  ,  1.   ]])
   
   
   E = np.array([[1.3,  13.0, 100.0], 
                 [.78,  12.4, 121.0], 
                 [.85,  1.2,  99.0], 
                 [1.0,  0.98, 1.2], 
                 [4.8,  .45,  .23], 
                 [3.89,  .99,  .11], 
                 [3.97, 1.2,  .01], 
                 [3.23, 1.0,  .12] ])
   
   
   Psig = np.dot(I,P)
   OmegaMtx = np.dot(I.T,I)
   AlphaMtx = np.dot(I,I.T)
   
   return OmegaMtx,P,I,E,AlphaMtx
   
   
def standardizePIC(O=None,P=None,I=None,Ones=None):
   if O is None:
      O,P,I, E, A = makeInputsForTest()
      k1Col = np.array([np.ones(I.shape[1])]).T
   else:
      k1Col = Ones
   recipFill = 1.0/O.trace()
   PoverFill  = P * recipFill
   fillMinusOne = O.trace() -1
   recipFillMinusOne = 1.0/fillMinusOne
   
   #print recipFill * recipFillMinusOne  # we will use this
   #print np.dot(recipFill,recipFillMinusOne) # same thing
   
   try:
      num1 = P - np.dot(np.dot(k1Col*k1Col.T,O),PoverFill) # good
      print "m 1 s ",num1.shape
   except Exception,e:
      print "m 1 e ",str(e)
   #try:
   #   num2 = P - np.dot(k1Col*k1Col.T*O,PoverFill) # second best
   #   print "m 2 s ",num2.shape
   #except Exception,e:
   #   print "m 2 e ",str(e)
   #try:
   #   num = P - k1Col*k1Col.T*O*PoverFill # bad
   #   print "m 3 s ",num.shape
   #except Exception,e:
   #   print "m 3 e ",str(e)   
   #try:
   #   num = P - np.dot(k1Col*k1Col.T,O)*PoverFill # bad
   #   print "m 4 s ",num.shape
   #except Exception,e:
   #   print "m 4 e ",str(e)   
      
   ################
   print
   OneOmegaP1 = np.dot(k1Col.T* O,P)  # returns a matrix
   #print "1 ",OneOmegaP1
   OneOmegaP2 = np.dot(np.dot(k1Col.T, O),P) # returns a vector
   #print
   #print "2 ",OneOmegaP2
   ####################
   
   OneWPP1 = np.dot(np.dot(k1Col.T,O),(P*P)) # vector
   #print OneWPP1
   OneWPP2 = np.dot(k1Col.T*O,(P*P)) # matrix
   #print OneWPP2
   
   ####################
   # can rule out 2 - (1*1), division by zero
   # that leaves, 2 - (2*2) (bad), 1 - (1*1) (bad), 1 - (2*2)
   den = OneWPP1 - np.dot((OneOmegaP2 * OneOmegaP2),np.dot(recipFill,recipFillMinusOne)) 
   sqrtden = den**.5
   maybeden = np.dot(k1Col,sqrtden)

   
   
   std = num1 / maybeden
   print 
   print std
   print
   #print np.dot(I,std)
   return std

def BetaE_regression(PsigStd,Estd,Alpha):
   
   # all
   recip = np.reciprocal(np.dot(np.dot(Estd.T,Alpha),Estd))
   print "shape Alpha ",Alpha.shape
   rightHand = np.dot(np.dot(Estd.T,Alpha),PsigStd)
   BetaEjAll = np.dot(recip,rightHand)
   print BetaEjAll
   
   print
   # for just i
   iEstd = Estd[:,0]
   recip = np.reciprocal(np.dot(np.dot(iEstd.T,Alpha),iEstd))
   rightHand = np.dot(np.dot(iEstd.T,Alpha),PsigStd)
   BetaEji = np.dot(recip,rightHand)
   print "BetaEji"
   print BetaEji
   print
   # minus i
   miEstd = Estd[:,[1,2]]
   recip = np.reciprocal(np.dot(np.dot(miEstd.T,Alpha),miEstd))
   rightHand = np.dot(np.dot(miEstd.T,Alpha),PsigStd)
   BetaEjMinusi = np.dot(recip,rightHand)
   print BetaEjMinusi
   
   YjAll = np.dot(Estd,BetaEjAll)
   YjminusI = np.dot(miEstd,BetaEjMinusi)
   
   
   undersqrLeft = np.trace(np.dot(YjAll.T,YjAll))/np.trace(PsigStd.T*PsigStd.T)
   undersqrRight = np.trace(np.dot(YjminusI.T,YjminusI))/np.trace(PsigStd.T*PsigStd.T)
   num = np.dot(BetaEji,(undersqrLeft-undersqrRight)**.5)
   print
   print "num ",num
   print
   print "DF ",(undersqrLeft-undersqrRight)**.5
   Pji = num/np.absolute(BetaEji)
   print
   print "absolute ",np.absolute(BetaEji)
   print
   print "dSFdSFHP:SDF:DSF"
   print Pji
   
def startHere():
   
   O,P,I,E,A = makeInputsForTest()
   # std P
   Ones = np.array([np.ones(I.shape[1])]).T # column vector
   Pstd = standardizePIC(O, P, I, Ones)
   PsigStd = np.dot(I,Pstd)
   # std E
   Ones = np.array([np.ones(I.shape[0])]).T
   Estd = standardizePIC(A, E, I, Ones)
   
   BetaE_regression(PsigStd,Estd,A)
      
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
# ..........................................   
def initMatrix(rowCnt,colCnt):
   return np.empty((rowCnt,colCnt))

# ..........................................

def getIds(tipsDictList):
   """
   @summary: get tip ids and internal ids
   """
   tipIds = [int(tp["pathId"]) for tp in tipsDictList ]
   total = (len(tipIds) * 2) - 1
   allIds = [x for x in range(0,total)]
   internalIds = list(set(allIds).difference(set(tipIds)))
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
   standardizePIC()
   startHere()
   

   