import os, sys
import simplejson as json
import numpy as np
import operator
import collections
from contextlib import contextmanager
import time


timerDict = {}

def makeInputsForTest():
   
   # incidence matrix fromt the text
   I = np.array([[1, 0, 0, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [1, 0, 0, 1, 0, 1],
                 [0, 0, 1, 1, 0, 1],
                 [0, 1, 0, 1, 0, 1],
                 [0, 0, 0, 0, 1, 0],
                 [1, 0, 0, 0, 1, 0],
                 [0, 1, 0, 0, 1, 0]])
   
   # P from the text
   P = np.array([[-1.   , -0.5  , -0.25 , -0.125,  0.   ],
                 [ 1.   , -0.5  , -0.25 , -0.125,  0.   ],
                 [ 0.   ,  1.   , -0.5  , -0.25 ,  0.   ],
                 [ 0.   ,  0.   ,  1.   , -0.5  ,  0.   ],
                 [ 0.   ,  0.   ,  0.   ,  0.5  , -1.   ],
                 [ 0.   ,  0.   ,  0.   ,  0.5  ,  1.   ]])
   
   ############################
   
   return P,I,

def getEnvMatrix():

   E = np.array([[1.3,  13.0, 100.0], 
                 [.78,  12.4, 121.0], 
                 [.85,  1.2,  99.0], 
                 [1.0,  0.98, 11.2], 
                 [4.8,  0.45,  21.23], 
                 [3.89, 0.99,  21.11], 
                 [3.97, 1.2,  12.01], 
                 [3.23, 1.0,  10.12] ])
   return E

def calculateMarginals(I):
      
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
   

def stdMtx(W,M,OnesCol,I):
   
   TotalSum = I.sum()
   SiteWeights = W
   sPred = np.dot(np.dot(OnesCol.T,SiteWeights),M)
   sPred2 = np.dot(np.dot(OnesCol.T,SiteWeights),(M*M))
   MeanWeightedPred = sPred/TotalSum
   StdDevWeightedPred = ((sPred2-(sPred**2/TotalSum))/(TotalSum))**.5
   Std = ((np.dot(OnesCol,StdDevWeightedPred))**-1) * (M-np.dot(OnesCol,MeanWeightedPred))
   
   
   return Std
   
def standardizeMatrix(W=None,M=None,OnesCol=None):
   
   """
   @summary: standardizes matrix M (phylo encoding) or Env Mtx
   @param OnesCol: column vector of ones, either k or n, k=No.Sps,n=No.Sites
   @param M: phylo encoding mtx or env mtx
   @param W: Wk or Wn diag mtx with diag sums from PAM (I)
   """
   
   #recipFill = 1.0/W.trace()
   #PoverFill  = M * recipFill
   totalSum = W.trace()
   MeanWeighted  = M / totalSum
   #fillMinusOne = W.trace() - 1.0
   #recipFillMinusOne = 1.0/fillMinusOne
   
   #OneByOne = OnesCol*OnesCol.T
  
   
   diagonal = np.diagonal(W)  # what we call alpha for env, omega for phylo
   
   OneOneTW = np.repeat(diagonal[np.newaxis,:], M.shape[0], axis = 0) # replaces np.dot(OnesCol*OnesCol.T,W)
   
   #OneOneTW = np.dot(OneByOne,W)
  
   
   #numerator = np.dot(np.dot(OnesCol*OnesCol.T,W),PoverFill)
   numerator_part = np.dot(OneOneTW,MeanWeighted)
   
   
   ################
   
   OneW = np.dot(OnesCol.T, W)
   
   #OneWP1 = np.dot(OnesCol.T * W,M)  # returns a matrix
   #OneWP = np.dot(np.dot(OnesCol.T, W),M) # returns a vector
   OneWM = np.dot(OneW,M) # returns a vector
   
   ####################
   
   #OneWPP = np.dot(np.dot(OnesCol.T,W),(M*M)) # vector
   OneWMM = np.dot(OneW,(M*M)) # vector
   #OneWPP2 = np.dot(OnesCol.T*W,(M*M)) # matrix
   
   
   ####################
   # can rule out 2 - (1*1), division by zero
   # that leaves, 2 - (2*2) (bad), 1 - (1*1) (bad), 1 - (2*2)
   #den = OneWPP - (np.dot((OneWP*OneWP),np.dot(recipFill,recipFillMinusOne))) # doesn't match Leibold
   test = (OneWMM - ((OneWM**2)  / totalSum))
   print np.where(OneWMM == 0)
   print np.where(M == 0)
   print "Cosby"
   print np.where(OneWM == 0)
   print (OneWM**2).min()
   print test.min()
   StdDevWeighted_Squared = (OneWMM - ((OneWM**2)  / totalSum)) / (totalSum)  # matches Leibold
   # StdDevWeighted_Squared = (OneWPP - ((OneWP**2)  / totalSum)) / (totalSum -1)  # from equation in non code supplemental
   print StdDevWeighted_Squared.min()
   StdDevWeighted = StdDevWeighted_Squared**.5
   print StdDevWeighted.min()
   denominator = np.dot(OnesCol,StdDevWeighted)
   print "min denominator ",denominator.min()
   denominator_recip = denominator**-1
   std = denominator_recip * (M - numerator_part)  #running into division by zero for Tashi's data
   #std = (M - numerator_part) / denominator  # running into division by for Tashi's data
   #print "my denominator ",denominator
   #print "my numerator ",(M - numerator)
  
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
      """
      @summary: since associative can compute these parts
      without having to repeat across nodes
      """
      invX = np.linalg.inv(np.dot(np.dot(E.T,Wn),E))
      rightHand = np.dot(E.T,Wn)
      return np.dot(invX,rightHand)
   
   for i in range(0,Estd.shape[1]):
      # loops through columns in Env mtx
      Estd_i = np.array([Estd[:,i]]).T
      Estd_minus_i = np.delete(Estd,i,1)
      
      # standard way of calc B in mtx form, # B = (XtX)^-1(XtY)
      # where Y is response matrix
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
            
            if BetaEji != 0:
               Pji = num/np.absolute(BetaEji)
            else:
               Pji = 0.
            print "P(j,i), j = %s" % (x)
            print Pji
            print
            #
         else:
            pass
            print "negative R squared, node ",x
            print 
# ........................................ 
            
def semiPartCorrelation(PsigStd,Estd,Wn):
   
   def getP(col):
      """
      @summary: gets applied along columns of PsigStd, each column is a internal node of tree
      @param col: column (internal node of tree) of PsigStd
      """
      PsigStdNode = np.array([col]).T
      
      #BetaEjAll, BetaEji, BetaEjMinusi = models(PsigStdNode, Estd, Wn)
      BetaEjAll = np.dot(BjAll_part,PsigStdNode)
      BetaEji = np.dot(Bji_part,PsigStdNode)
      BetaEjMinusi = np.dot(Bjminus1_part,PsigStdNode)
      
      #### estimate Y hat ###
      YjAll = np.dot(Estd,BetaEjAll)
      YjminusI = np.dot(Estd_minus_i,BetaEjMinusi)
      ###############
      
      numDiffRsqr = np.trace(np.dot(YjAll.T,YjAll)) - np.trace(np.dot(YjminusI.T,YjminusI))
      
      diffRSqr = numDiffRsqr /  diffRSqrDen# next was unnec. getting repeated -np.trace(np.outer(PsigStd.T,PsigStd.T))#  this wasn't a diagonal matrix - np.trace(PsigStd.T*PsigStd.T)
      
      if diffRSqr >= 0:
      
         num =  BetaEji*((diffRSqr)**.5)
         
         if BetaEji != 0:
            Pji = num/np.absolute(BetaEji)
         else:
            Pji = np.array([[0.0]])
              
      else:
         Pji = np.array([[0.0]])
      #print "done node"   
      return Pji
   #.................
   def getPartModel(E):
      """
      @summary: since associative can compute these parts of regression model
      without having to repeat across nodes
      """
      invX = np.linalg.inv(np.dot(np.dot(E.T,Wn),E))
      rightHand = np.dot(E.T,Wn)
      return np.dot(invX,rightHand)
   #.................
   # main #
   #diffRSqrDen = np.trace(np.outer(PsigStd.T,PsigStd.T))   # serious memory problems, with anything of any size
   diffRSqrDen = np.sum(PsigStd**2)
   #print "done diffRSqrDen"
   rl = []
   for i in range(0,Estd.shape[1]):
      # for each variable (column) in Env mtx
      print "env col ",i
      Estd_i = np.array([Estd[:,i]]).T
      Estd_minus_i = np.delete(Estd,i,1)
      
      BjAll_part = getPartModel(Estd)
      Bji_part = getPartModel(Estd_i)
      Bjminus1_part = getPartModel(Estd_minus_i)
      
      
      r = np.apply_along_axis(getP, 0, PsigStd)
      #if isinstance(r[0],np.ndarray):
      rl.append(r[0])
      #print "done env col ",i
      #else:
      #   rl.append(r)
      
   coefMtx = np.array(rl).T
   #print "min ",coefMtx.min()
   #print "max ",coefMtx.max()
   #print "shape coeffMtx ",coefMtx.shape
   return coefMtx
# ..................................
def clock():
   pass
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
# ........................................
def makeP(treeDict,I,layersPresent=None):
   """
   @summary: encodes phylogeny into matrix P and checks
   for sps in tree but not in PAM (I), if not in PAM, returns
   new PAM (I) in addition to P
   """
   ######### make P ###########
   tips, internal, tipsNotInMtx = buildTips(treeDict,I.shape[1],layersPresent=layersPresent)
   negsDict = processInternalNodes(internal)
   tipIds,internalIds = getIds(tips,internalDict=internal)
   matrix = initMatrix(len(tipIds),len(internalIds))
   P = buildPMatrix(matrix,internalIds,tips, negsDict)
   
   if len(tipsNotInMtx) > 0:
      I = processTipNotInMatrix(tipsNotInMtx, internal, I)
      
   return P, I
# ........................................
def startHere(testWithInputsFromPaper=False,shiftedTree=False):
   """
   @param shiftedTree: this means using a tree with same topology
   of Liebold example but with tips shifted around according to 
   how mx's are likely to appear in a real tree
   """
      
   # Env Matrix
   E = getEnvMatrix()
   
   #######################
   if not testWithInputsFromPaper:
      #### load tree json ######
      #jsP = "/home/jcavner/PhyloXM_Examples/"
      jsP = "/home/jcavner/TASHI_PAM/"
      #fN = "Liebold_notEverythinginMatrix.json"
      fN = 'tree.json'
      path = os.path.join(jsP,fN)
      d = loadJSON(path)
      ##############
      I = np.array([[1, 0, 0], 
                    [0, 0, 1],  
                    [1, 0, 0],  
                    [0, 0, 1],  
                    [0, 1, 0],  
                    [0, 0, 0],  
                    [1, 0, 0],  
                    [0, 1, 0]])
      ##### Tashi's pam #####
      pamPath = os.path.join(jsP,'pam_2462.npy')
      I = np.load(pamPath)
      #### Tashi's layers present ####
      import cPickle
      lP = cPickle.load(open(os.path.join(jsP,'indices_2462.pkl')))['layersPresent']
      ### compresss rows, experimental ###
      bs = np.any(I,axis=1)  # bolean selection row-wise logical OR
      delRowPos = np.where(bs == False)[0]  # position of deletes
      I = np.delete(I,delRowPos,axis=0)
      ##### compress columns, experimental ###
      bs = np.any(I,axis=0)  # bolean selection cloumn-wise logical OR
      delColPos = np.where(bs == False)[0]  # position of deletes
      I = np.delete(I,delColPos,axis=1)
      ### Tashi's Env Mtx ###
      r, c = I.shape[0], 5
      E = np.random.random_sample((r, c))
      #E = np.random.uniform(1,123,(I.shape[0],5))
      #E1 = np.append(np.random.uniform(3,1300,(5000,4)),np.random.uniform(23,343,(5000,9)),axis=1)
      #E2 = np.append(np.random.uniform(1700,3200,(700,4)),np.random.uniform(111,578,(700,9)),axis=1)
      #E3 = np.append(np.random.uniform(1700,1718,(15058-5700,4)),np.random.uniform(700,1705,(15058-5700,9)),axis=1)
      #Esub = np.append(E1,E2,axis=0)
      #E = np.append(Esub,E3,axis=0)
      #print "new E shape ",E.shape
      #######################
      P,I = makeP(d,I,layersPresent=lP)
      
   else:
      # inputs from Liebold paper
      P,I = makeInputsForTest()
     
      # two ways of  testing Liebold paper ?
      if shiftedTree:
         #### load tree json or use paper provided P ######
         jsP = "/home/jcavner/PhyloXM_Examples/"
         fN = "Liebold.json"
         path = os.path.join(jsP,fN)
         d = loadJSON(path)
         P,I = makeP(d,I)
         
      
        
          
   Wk,Wn = calculateMarginals(I)
   
   # std P
   Ones = np.array([np.ones(I.shape[1])]).T # column vector
   Pstd = standardizeMatrix(Wk, P, Ones)
   #
   ## calc Psig
   #PsigStd = np.dot(I,Pstd)
   
   
   # std E
   #Ones = np.array([np.ones(I.shape[0])]).T
   #Estd = standardizeMatrix(Wn, E, Ones)
   #test = stdMtx(Wn, E, Ones, I)
   
   #print Estd
   #print
   #print test
   
   #BetaE_regression(PsigStd,Estd,Wn)
   #C = semiPartCorrelation(PsigStd,Estd,Wn)
   #print C
   #print
   #print C.min()
   #print C.max()
   #print C.shape
   
   
# ........................................   
def loadJSON(path):
   
   with open(path,'r') as f:
      jsonstr = f.read()
   return json.loads(jsonstr)

# ........................................    
   
def buildTips(clade, noColPam, layersPresent=None ): 
   """
   @summary: flattens to tips and return list of tip clades(dicts)
   unsure how calculations would reflect/change if more tips in tree
   than in PAM.  If it does it needs to check for matrix key
   """ 
   lPItems = layersPresent.items()
   lPItems.sort(key=operator.itemgetter(0)) # order lyrs present by mtx idx
   #orderedLyrsPresent = collections.OrderedDict(lPItems)
   print "LEN ITEMS ",len(lPItems)
   noMx = {'c':noColPam}  # needs to start with last sps in pam
   test = []
   tips = []
   tipsNotInMatrix = []
   internal = {}
   def buildLeaves(clade):
   
      if "children" in clade: 
         #### just a check, probably take out 
         #if len(clade["children"]) > 2:
         #   print "polytomy ",clade["pathId"]
         ############   
         #internal[clade["pathId"]] = clade["children"][0] 
         internal[clade["pathId"]] = clade["children"] # both sides
         for child in clade["children"]:  
            buildLeaves(child)
      else: 
         if "mx" in clade:  
            if layersPresent[int(clade['mx'])]: #this is experimental
               castClade = clade.copy()
               # sum([x[1] for x in lPItems[:5] if x[1]])
               #castClade["mx"] = int(castClade["mx"]) 
               castClade["mx"] = sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])  # number of trues before mx
               print sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])  #DOESN"T FIX PROBLEM WITH take in processTipNotinMatrix!!
               test.append(castClade["mx"])
               tips.append(castClade)
            else:
               print "not in pam ",int(clade['mx'])
         else:
            castClade = clade.copy()
            castClade['mx'] = noMx['c']  # assigns a mx starting at end of pam
            tips.append(castClade)
            tipsNotInMatrix.append(castClade)
            noMx['c'] = noMx['c'] + 1
   buildLeaves(clade)  
   tips.sort(key=operator.itemgetter('mx'))   
   tipsNotInMatrix.sort(key=operator.itemgetter('mx'))
   return tips, internal, tipsNotInMatrix


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
            mx.append(int(clade["mx"]))
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
                  mxMapping[int(tip['mx'])] = [int(sibling['mx'])]
               else:
                  mxMapping[int(tip['mx'])] = 0
   la = [] # list of arrays              
   for k in sorted(mxMapping.keys()):
      if isinstance(mxMapping[k],list):
         print 'k ',mxMapping[k]
         t = np.take(pam,np.array(mxMapping[k]),axis = 1)
         b = np.any(t,axis = 1)  #returns bool logical or
      else:
         print "does it get in here?"
         #b = np.zeros(pam.shape[0],dtype=np.int)
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
   
   
   startHere(testWithInputsFromPaper=False,shiftedTree=False)
   

   