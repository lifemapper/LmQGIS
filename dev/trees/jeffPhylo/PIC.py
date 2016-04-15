import os, sys
import simplejson as json
import numpy as np
import operator
import collections
from contextlib import contextmanager
import time
import warnings   #  for divide by zero
warnings.filterwarnings('error')
np.seterr(all='warn')  # for divide by zero 


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
   """
   @summary: marginals similar to RAD marginals
   @param I: Incidence mtx, PAM
   """   
   siteCount = I.shape[0]
   siteVector = np.ones(siteCount)
   speciesCount = I.shape[1]
   speciesVector = np.ones(speciesCount)
   # range size of each species
   omega = np.dot(siteVector, I)
   # species richness of each site
   alpha = np.dot(I, speciesVector)
   
   Wk = np.diag(omega)
   
   Wn = np.diag(alpha)
   
   return Wk,Wn
   

def stdMtx(W,M,OnesCol,I):
   """
   @param W: diagonal mtx
   @param M: mtx to be std
   @param OnesCol: column vector of ones, sites (n) or species (k)
   @param I: Incidence mtx, PAM 
   """
   TotalSum = I.sum()
   
   SiteWeights = W
   
   sPred = np.dot(np.dot(OnesCol.T,SiteWeights),M)
   sPred2 = np.dot(np.dot(OnesCol.T,SiteWeights),(M*M))
   #try:
   MeanWeightedPred = sPred/TotalSum
   #except Warning:
   #   print Warning
   #try:
   StdDevWeightedPred = ((sPred2-(sPred**2/TotalSum))/(TotalSum))**.5
   #except Warning:
   #   print "Warning 2 ",str(Warning)
   #try:
   t = np.dot(OnesCol,StdDevWeightedPred)
      #print np.where(t == 0)
   Std = ((np.dot(OnesCol,StdDevWeightedPred))**-1) * (M-np.dot(OnesCol,MeanWeightedPred))
   #except Warning:
   #   print "Warning 3 ",Warning
      
   
   
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
   MOverFill  = M / totalSum  # ????????, this was POverFill
   #fillMinusOne = W.trace() - 1.0
   #recipFillMinusOne = 1.0/fillMinusOne
   
   #OneByOne = OnesCol*OnesCol.T
  
   
   diagonal = np.diagonal(W)  # what we call alpha for env, omega for phylo
   
   OneOneTW = np.repeat(diagonal[np.newaxis,:], M.shape[0], axis = 0) # replaces np.dot(OnesCol*OnesCol.T,W)
   
   #OneOneTW = np.dot(OneByOne,W)
  
   
   #numerator = np.dot(np.dot(OnesCol*OnesCol.T,W),PoverFill)
   numerator_part = np.dot(OneOneTW,MOverFill)  # equals ones(NumberSites,1)*MeanWeigthedPred
   # where MeansWeigthedPred =  sPred(OneWM)/totalSum
   
   
   ################
   
   OneW = np.dot(OnesCol.T, W)
   #print "OneW "
   #print np.where(OneW == 0)
   #print
   #OneWP1 = np.dot(OnesCol.T * W,M)  # returns a matrix
   #OneWP = np.dot(np.dot(OnesCol.T, W),M) # returns a vector
   OneWM = np.dot(OneW,M) # returns a vector, equals sPred in Matlab code
   
   #  I think this was the problem
   
   
   ####################
   
   #OneWPP = np.dot(np.dot(OnesCol.T,W),(M*M)) # vector
   OneWMM = np.dot(OneW,(M*M)) # vector
   #OneWPP2 = np.dot(OnesCol.T*W,(M*M)) # matrix
   
   
   ####################
   # can rule out 2 - (1*1), division by zero
   # that leaves, 2 - (2*2) (bad), 1 - (1*1) (bad), 1 - (2*2)
   #den = OneWPP - (np.dot((OneWP*OneWP),np.dot(recipFill,recipFillMinusOne))) # doesn't match Leibold
   #print np.where(OneWMM == 0)
   #print np.where(M == 0)
   #
   #print np.where(OneWM == 0)
   #print (OneWM**2).min()
   #print test.min()
   StdDevWeighted_Squared = (OneWMM - ((OneWM**2)  / totalSum)) / (totalSum)  # matches Leibold
   # StdDevWeighted_Squared = (OneWPP - ((OneWP**2)  / totalSum)) / (totalSum -1)  # from equation in non code supplemental
   #print StdDevWeighted_Squared.min()
   StdDevWeighted = StdDevWeighted_Squared**.5
   #print StdDevWeighted.min()
   denominator = np.dot(OnesCol,StdDevWeighted)
   #print "min denominator ",denominator.min()
   denominator_recip = denominator**-1
   std = denominator_recip * (M - numerator_part)  #running into division by zero for Tashi's data
   #std = (M - numerator_part) / denominator  # running into division by for Tashi's data
   #print "my denominator ",denominator
   #print "my numerator ",(M - numerator)
  
   return std


def models(PsigStdNode,Estd,Wn,Estd_i=None,Estd_mi=None):
   """
   @deprecated: maybe
   """
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
   """
   @deprecated: maybe
   """
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
def semiPartCorrelation_Leibold_Vectorize(I,PredictorMtx,NodeMtx): 
   """
   @summary: so far this is the most recent, follows Pedro's matlab code as far as loops
   that are necessary for treating nodes individually. Exceptions are mathematical changes
   for effeciency, and corrections for sps in tree but not in PAM, also fault checks.
   """
   # NodeMtx = P
   IncidenceMtx = I
   NumberNodes = NodeMtx.shape[1]
   VectorProbRsq = np.array([np.ones(NumberNodes)]) 
   NumberPredictors = PredictorMtx.shape[1]
   MatrixProbSemiPartial = np.ones((NumberNodes,NumberPredictors))  
   iDictPred = {}
   iDictNode = {'y':0}
   
   # put results here
   resultSemiPartialMtx = np.zeros((NumberNodes,NumberPredictors))
   resultFSemiPartialMtx = np.zeros((NumberNodes,NumberPredictors))
   resultRsqAdjMtx = np.array([np.zeros(NumberNodes)]).T
   resultRsqMtx = np.array([np.zeros(NumberNodes)]).T
   resultFGlobalMtx = np.array([np.zeros(NumberNodes)]).T                       
  
  
   def predictors(predictorCol, **kwargs):
      """
      @summary: applied across column axis for predictor matrix.
      predictor matrix can be either env or hist biogeography
      """
      try:
         # needs the node number
         Predictors = kwargs['Predictors']
         swDiagonoal = kwargs['swDiagonoal']
         StdPSum  = kwargs['StdPSum']
         resultRsq = kwargs['resultRsq']
         TotalPSumResidual = kwargs['TotalPSumResidual']
         
         nodeNumber = kwargs['nodeNumber']
         predNumber = iDictPred['x']  # 'x' axis of results
         
         
         IthPredictor = np.array([predictorCol]).T
         WithoutIthPredictor = np.delete(Predictors,predNumber,axis=1)  
         
         # % slope for the ith predictor, Beta, regression coefficient
         Q,R = np.linalg.qr(np.dot(np.einsum('ij,j->ij',IthPredictor.T,swDiagonoal),IthPredictor))
         
         RdivQT = np.linalg.lstsq(R,Q.T)[0]
         
         IthsSlope_part = np.dot(RdivQT,IthPredictor.T)
         IthsSlope_second_part = np.einsum('ij,j->ij',IthsSlope_part,swDiagonoal)
         IthSlope = np.dot(IthsSlope_second_part,StdPSum)
         
         
         # % regression for the remaining predictors
         Q,R = np.linalg.qr(np.dot(np.einsum('ij,j->ij',WithoutIthPredictor.T,swDiagonoal),WithoutIthPredictor))
         RdivQT_r = np.linalg.lstsq(R,Q.T)[0]
         WithoutPredRQ_r = np.dot(WithoutIthPredictor,RdivQT_r)
         H_part = np.dot(WithoutPredRQ_r,WithoutIthPredictor.T)
         H = np.einsum('ij,j->ij',H_part,swDiagonoal)
         Predicted = np.dot(H,StdPSum)
         RemainingRsq = np.sum(Predicted**2)/np.sum(StdPSum**2)
         
         if (resultRsq - RemainingRsq) >= 0:
            resultSP = IthSlope * ((resultRsq - RemainingRsq)**.5) / np.absolute(IthSlope)
         else:
            resultSP = np.array([0.0])
            
         FSemiPartial = (resultRsq - RemainingRsq)/TotalPSumResidual
         resultFSemiPartialMtx[predNumber][nodeNumber] = FSemiPartial
         
         iDictPred['x'] += 1
      except Exception, e:
         resultSP = np.array([0.0])
         
         
      
      
      return resultSP
   
   def nodes(nodeCol):
      """
      @summary: operation to be performed on each node
      """
      
      iDictPred['x'] = 0
      
      SpeciesPresentAtNode = np.where(nodeCol != 0)[0]
      Incidence = IncidenceMtx[:,SpeciesPresentAtNode]  # might want to use a take here
      
      # added Jeff, find if any of the columns in sliced Incidence are all zero
      bs = np.any(Incidence, axis=0)
      emptyCol = np.where(bs == False)[0]
      #############
      
     
      ###########
      # find rows in Incidence that are all zero
      bs = np.any(Incidence,axis=1)  # bolean selection row-wise logical OR
      EmptySites = np.where(bs == False)[0]  # position of deletes
      Incidence = np.delete(Incidence,EmptySites,0)  # delete rows
      
      if Incidence.shape[0] > 1:# and len(emptyCol) == 0: # might not need this last clause, get more good nodes for Tashi without it
         
         #print "node number ",NodeNumber
         Predictors = PredictorMtx
         Predictors = np.delete(Predictors,EmptySites,0) # delete rows
         NumberSites = Incidence.shape[0]
         #######################
         
         if NumberPredictors > (NumberSites -2):  # or is it, <
            pass
         
         TotalSum = np.sum(Incidence)
         SumSites = np.sum(Incidence,axis = 1)  # sum of the rows, alpha
         SumSpecies = np.sum(Incidence,axis = 0)  # sum of the columns, omega
         NumberSpecies = Incidence.shape[1]
         SiteWeights = np.diag(SumSites)   # Wn
         SpeciesWeights = np.diag(SumSpecies) # Wk
         
         try:
            # standardize Predictor, in this case Env matrix
            Ones = np.array([np.ones(NumberSites)]).T
            StdPredictors = stdMtx(SiteWeights, Predictors, Ones, Incidence)
            
            ## P standardize 
            Ones = np.array([np.ones(NumberSpecies)]).T
            StdNode = stdMtx(SpeciesWeights, nodeCol[SpeciesPresentAtNode], Ones, Incidence)
              
         except:
            result = np.array([np.zeros(NumberPredictors)])
         else:
            
            # PsigStd
            StdPSum = np.dot(Incidence,StdNode)  
            
            # regression #############3
            Q,R = np.linalg.qr(np.dot(np.dot(StdPredictors.T,SiteWeights),StdPredictors))
           
            RdivQT = np.linalg.lstsq(R,Q.T)[0]
            
            StdPredRQ = np.dot(StdPredictors,RdivQT)
            
            
            swDiagonoal = np.diagonal(SiteWeights)
            
            # H is BetaAll
            #H = np.dot(np.dot(StdPredRQ,StdPredictors.T),SiteWeights)  # WON'T SCALE!!
            H_first = np.dot(StdPredRQ,StdPredictors.T)
            H = np.einsum('ij,j->ij',H_first,swDiagonoal)
            
            Predicted =  np.dot(H,StdPSum)
            TotalPSumResidual = np.sum((StdPSum-Predicted)**2)
            
            StdPSumSqrs = np.sum(StdPSum**2)
            if  StdPSumSqrs != 0:
               resultRsq = np.sum(Predicted**2)/StdPSumSqrs  
               resultRsqMtx[iDictNode['y']] = resultRsq
               ################################################3
               
               #% adjusted Rsq  (classic method) should be interpreted with some caution as the degrees of
               #% freedom for weighted models are different from non-weighted models
               #% adjustments based on effective degrees of freedom should be considered
               
               FGlobal = np.sum(Predicted**2)/TotalPSumResidual
               if NumberSites-NumberPredictors-1 > 0:                  
                  RsqAdj = 1 - np.dot(((NumberSites-1)/(NumberSites-NumberPredictors-1)),(1-resultRsq))   
               else:
                  RsqAdj = -999
               resultRsqAdjMtx[iDictNode['y']] = RsqAdj
               resultFGlobalMtx[iDictNode['y']] = FGlobal
               # semi partial correlations 
               d =  {'Predictors' :Predictors,'swDiagonoal': swDiagonoal, 
                     'StdPSum':StdPSum,'resultRsq':resultRsq,'TotalPSumResidual':TotalPSumResidual,
                     'nodeNumber':iDictNode['y']}
               # sending whole Predictor mtx to predictors func, and feeding it to apply_along_axis, feeds one col. at a time, 0 axis
               # 3 significance done: resultRsq, RsqAdj,FGlobal
               
               result = np.apply_along_axis(predictors, 0, Predictors, **d)
               
                  
            else:
               result = np.array([np.zeros(NumberPredictors)])
      else:
         result = np.array([np.zeros(NumberPredictors)])  # if here, row of zeros's (because isnt' a good node?)
      
      resultSemiPartialMtx[iDictNode['y']] = result[0]
      
      iDictNode['y'] += 1    
        
      return np.array([])      
   
   np.apply_along_axis(nodes, 0, NodeMtx)
   
   #### results
   
   print;print "FINAL Correlations"
   print resultSemiPartialMtx
   #bs = np.any(resultSemiPartialMtx,axis=1)
   #print
   #print "good nodes ",len(np.where(bs == True)[0])
   
   print 
   print "resultRsqAdjMtx"
   print resultRsqAdjMtx
   print
   print "resultFSemiPartialMtx"
   print resultFSemiPartialMtx
   
# ........................................
def semiPartCorrelation_Leibold(I,PredictorMtx,NodeMtx): 
   # NodeMtx = P
   IncidenceMtx = I
   NumberNodes = NodeMtx.shape[1]
   VectorProbRsq = np.array([np.ones(NumberNodes)]) # supposed to column vector?, not sure where this is being used right now, looks like might be row vector
   NumberPredictors = PredictorMtx.shape[1]
   MatrixProbSemiPartial = np.ones((NumberNodes,NumberPredictors))  # holder array for results?
   print NodeMtx
   print
   # put results here
   resultSemiPartial = np.array((NumberNodes,NumberPredictors))
   faster = slower = 0
   skippedNodes = 0
   for NodeNumber in range(0,NumberNodes):
      
      SpeciesPresentAtNode = np.where(NodeMtx[:,NodeNumber] != 0)[0]
      Incidence = IncidenceMtx[:,SpeciesPresentAtNode]  # might want to use a take here
      
      # added Jeff, find if any of the columns in sliced Incidence are all zero
      bs = np.any(Incidence, axis=0)
      emptyCol = np.where(bs == False)[0]
      #############
      
     
      ###########
      # find rows in Incidence that are all zero
      bs = np.any(Incidence,axis=1)  # bolean selection row-wise logical OR
      EmptySites = np.where(bs == False)[0]  # position of deletes
      Incidence = np.delete(Incidence,EmptySites,0)  # delete rows
      
      if len(emptyCol) == 0 and Incidence.shape[0] > 1:
         print;print
         print "node number ",NodeNumber
         Predictors = PredictorMtx
         Predictors = np.delete(Predictors,EmptySites,0) # delete rows
         NumberSites = Incidence.shape[0]
         #######################
         
         if NumberPredictors > (NumberSites -2):  # or is it, <
            pass
         
         TotalSum = np.sum(Incidence)
         SumSites = np.sum(Incidence,axis = 1)  # sum of the rows, alpha
         SumSpecies = np.sum(Incidence,axis = 0)  # sum of the columns, omega
         NumberSpecies = Incidence.shape[1]
         SiteWeights = np.diag(SumSites)   # Wn
         SpeciesWeights = np.diag(SumSpecies) # Wk
         
         try:
            
            # standardize Predictor, in this case Env matrix
            Ones = np.array([np.ones(NumberSites)]).T
            StdPredictors = stdMtx(SiteWeights, Predictors, Ones, Incidence)
            #print "STD PRED!!"
            ## P standardize 
            Ones = np.array([np.ones(NumberSpecies)]).T
            
            StdNode = stdMtx(SpeciesWeights, NodeMtx[SpeciesPresentAtNode,NodeNumber], Ones, Incidence)
            #print "STD NODE!!"
            
         except:
            print "COULD NOT STD FOR NODE ",NodeNumber
         else:
            
            # PsigStd
            StdPSum = np.dot(Incidence,StdNode)  
            
            # regression #############3
            Q,R = np.linalg.qr(np.dot(np.dot(StdPredictors.T,SiteWeights),StdPredictors))
            print "done QR"
            
            
            
            RdivQT = np.linalg.lstsq(R,Q.T)[0]
            print "done left division"
            #print RdivQT
            
            StdPredRQ = np.dot(StdPredictors,RdivQT)
            # H is BetaAll
            
            swDiagonoal = np.diagonal(SiteWeights)
            
            #st = time.clock()
            #H = np.dot(np.dot(StdPredRQ,StdPredictors.T),SiteWeights)  # WON'T SCALE!!
            H_first = np.dot(StdPredRQ,StdPredictors.T)
            H = np.einsum('ij,j->ij',H_first,swDiagonoal)
            #et = time.clock()
            #tt_dot = et - st
            
            
            
            #st = time.clock()
            #H_first = np.dot(StdPredRQ,StdPredictors.T)
            #H = np.apply_along_axis(lambda x : x*swDiagonoal, 1, H_first)
            #et = time.clock()
            #tt_apply = et -st
            
            # try this too
            # np.einsum('ij,j->ij',A,b)
            
           
            Predicted =  np.dot(H,StdPSum)
            
            
            # TotalPSumResidual=trace((StdPSum-Predicted)'*(StdPSum-Predicted));
            #TotalPSumResidual = np.trace(np.dot((StdPSum-Predicted).T,(StdPSum-Predicted)))  # error for trace not 2 dimensional
            
            # result.Rsq(NodeNumber,1)=trace(Predicted'*Predicted)/trace(StdPSum'*StdPSum);
            # want to assign this an element in an array ????
            StdPSumSqrs = np.sum(StdPSum**2)
            if  StdPSumSqrs != 0:
               resultRsq = np.sum(Predicted**2)/StdPSumSqrs  # if  zero in denom , error obviously,
               ################################################3
               
               #% adjusted Rsq  (classic method) should be interpreted with some caution as the degrees of
               #% freedom for weighted models are different from non-weighted models
               #% adjustments based on effective degrees of freedom should be considered
               #result.RsqAdj(NodeNumber,1)=1-((NumberSites-1)/(NumberSites-NumberPredictors-1))*(1-result.Rsq(NodeNumber,1));
               #result.FGlobal(NodeNumber,1)=trace(Predicted'*Predicted)/TotalPSumResidual;
               
               # semi partial correlations 
               for i in range(0,NumberPredictors):
                  print "predictor no. ",i
                  IthPredictor = np.array([Predictors[:,i]]).T
                  WithoutIthPredictor = np.delete(Predictors,i,axis=1)
                  
                  # % slope for the ith predictor, Beta, regression coefficient
                  # [Q,R]=qr(IthPredictor'*SiteWeights*IthPredictor);
                  #Q,R = np.linalg.qr(np.dot(np.dot(IthPredictor.T,SiteWeights),IthPredictor)) # original
                  Q,R = np.linalg.qr(np.dot(np.einsum('ij,j->ij',IthPredictor.T,swDiagonoal),IthPredictor))
                  #IthSlope=(R\Q')*IthPredictor'*SiteWeights*StdPSum;
                  RdivQT = np.linalg.lstsq(R,Q.T)[0]
                  
                  IthsSlope_part = np.dot(RdivQT,IthPredictor.T)
                  IthsSlope_second_part = np.einsum('ij,j->ij',IthsSlope_part,swDiagonoal)
                  IthSlope = np.dot(IthsSlope_second_part,StdPSum)
                  #IthSlope = np.dot(np.dot(np.dot(RdivQT,IthPredictor.T),SiteWeights),StdPSum)  # original
                  
                  # % regression for the remaining predictors
                  #Q,R = np.linalg.qr(np.dot(np.dot(WithoutIthPredictor.T,SiteWeights),WithoutIthPredictor)) #original
                  Q,R = np.linalg.qr(np.dot(np.einsum('ij,j->ij',WithoutIthPredictor.T,swDiagonoal),WithoutIthPredictor))
                  RdivQT_r = np.linalg.lstsq(R,Q.T)[0]
                  WithoutPredRQ_r = np.dot(WithoutIthPredictor,RdivQT_r)
                  H_part = np.dot(WithoutPredRQ_r,WithoutIthPredictor.T)
                  H = np.einsum('ij,j->ij',H_part,swDiagonoal)
                  #H = np.dot(np.dot(WithoutPredRQ_r,WithoutIthPredictor.T),SiteWeights) #original
                  Predicted = np.dot(H,StdPSum)
                  #RemainingRsq = np.trace(np.dot(Predicted.T,Predicted))/np.trace(np.dot(StdPSum.T,StdPSum))
                  RemainingRsq = np.sum(Predicted**2)/np.sum(StdPSum**2)
                  if (resultRsq - RemainingRsq) >= 0:
                     resultSemiPartial = IthSlope * ((resultRsq - RemainingRsq)**.5) / np.absolute(IthSlope)
                  else:
                     #print "nothing"
                     resultSemiPartial = 0
                  print "SEMI ",resultSemiPartial;print
            else:
               print "division by zero"
               
   
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
      
      numDiffRsqr = np.trace(np.dot(YjAll.T,YjAll)) - np.trace(np.dot(YjminusI.T,YjminusI))  # thise are just sum of the squares too
      
      diffRSqr = numDiffRsqr /  diffRSqrDen # next was unnec. getting repeated -np.trace(np.outer(PsigStd.T,PsigStd.T))#  this wasn't a diagonal matrix - np.trace(PsigStd.T*PsigStd.T)
      
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
      I = processTipNotInMatrix(tipsNotInMtx, internal, I,layersPresent=layersPresent)
      
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
      jsP = "/home/jcavner/PhyloXM_Examples/"
      #jsP = "/home/jcavner/TASHI_PAM/"
      fN = "Liebold_notEverythinginMatrix.json"
      #fN = 'tree.json'
      path = os.path.join(jsP,fN)
      d = loadJSON(path)
      ##############
      I = np.array([[1, 0, 0],   #[1, 0, 0], # original
                    [0, 1, 1],   #[0, 1, 1],  
                    [0, 1, 0],   #[0, 0, 0],  
                    [0, 0, 1],   #[0, 0, 1],  
                    [0, 1, 0],   #[0, 0, 0],  
                    [0, 1, 0],   #[0, 0, 0],  
                    [1, 0, 0],   #[1, 0, 0],  
                    [0, 0, 0]])  #[0, 0, 0]]
      bs = np.any(I,axis=0)  # bolean selection cloumn-wise logical OR
      delColPos = np.where(bs == False)[0]
      #I = np.delete(I,delColPos,axis=1)
      bs = np.any(I,axis = 1)
      delRowPos = np.where(bs == False)[0]
      #I = np.delete(I,delRowPos,axis=0)
      lP = {0:True,1:False,2:True}
      lP = None
      ####### Tashi's pam #####
      #pamPath = os.path.join(jsP,'pam_2462.npy')
      #I = np.load(pamPath)
      ##### Tashi's layers present ####
      #import cPickle
      #lP = cPickle.load(open(os.path.join(jsP,'indices_2462.pkl')))['layersPresent']
      #lP = None
      #### compresss rows, experimental ###
      #bs = np.any(I,axis=1)  # bolean selection row-wise logical OR
      #delRowPos = np.where(bs == False)[0]  # position of deletes
      ##I = np.delete(I,delRowPos,axis=0)
      ###### compress columns, experimental ###
      #bs = np.any(I,axis=0)  # bolean selection cloumn-wise logical OR
      #delColPos = np.where(bs == False)[0]  # position of deletes
      ##I = np.delete(I,delColPos,axis=1)
      #### Tashi's Env Mtx ###
      #r, c = I.shape[0], 5
      #E = np.random.random_sample((r, c))
      ##
      #######################
      P,I = makeP(d,I,layersPresent=lP)
      print I
      print 
      #P[0][3] = -1.0  # this is the key
      #P[1][4] = 0.0   # this is the key
      print "shape P ",P.shape
      print "shape I ",I.shape
      print 
      print P
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
         
      
   colSumTest = np.sum(P,axis=0)
   notZero = np.where(colSumTest != 0)[0]
   #print "doesn't sum to zero ",len(notZero)
   #P = np.delete(P,notZero,axis=1)
   #print "shape P after del ",P.shape
   #print
   #print np.sum(P[:,notZero],axis=0)     
          
   #Wk,Wn = calculateMarginals(I)
   #
   ## std P
   #Ones = np.array([np.ones(I.shape[1])]).T # column vector
   #Pstd = standardizeMatrix(Wk, P, Ones)
   ###
   #### calc Psig
   #PsigStd = np.dot(I,Pstd)
   #
   #
   ## std E
   #Ones = np.array([np.ones(I.shape[0])]).T
   #Estd = standardizeMatrix(Wn, E, Ones)
   #Estd = stdMtx(Wn, E, Ones, I)  # Leibold std procedure
   
   #print Estd
   #print
   #print test
   
   #BetaE_regression(PsigStd,Estd,Wn)
   #C = semiPartCorrelation(PsigStd,Estd,Wn)
   #semiPartCorrelation_Leibold(I,E,P)
   semiPartCorrelation_Leibold_Vectorize(I,E,P)
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
   @param noColPam: at what point does this arg get set/sent, compression to consider !!!!!!!
   """ 
   if layersPresent is not None:
      lPItems = layersPresent.items()
      lPItems.sort(key=operator.itemgetter(0)) # order lyrs present by mtx idx
      #orderedLyrsPresent = collections.OrderedDict(lPItems)
   
   noMx = {'c':noColPam}  # needs to start with last sps in pam
   #test = []
   tips = []
   tipsNotInMatrix = []
   internal = {}
   def buildLeaves(clade):
   
      if "children" in clade: 
         #### just a check, probably take out 
         if len(clade["children"]) > 2:
            print "polytomy ",clade["pathId"]
         ############   
         #internal[clade["pathId"]] = clade["children"][0] 
         internal[clade["pathId"]] = clade["children"] # both sides
         for child in clade["children"]:  
            buildLeaves(child)
      else: 
         if "mx" in clade: 
            castClade = clade.copy()
            if layersPresent is not None:
               if layersPresent[int(clade['mx'])]:
                  castClade["mx"] = sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])
                  tips.append(castClade)
               else:
                  pass
            else:
               castClade["mx"] = int(castClade["mx"])
               tips.append(castClade)
               
            ############################################
            #if layersPresent[int(clade['mx'])]: #this is experimental, need to fix this key error
            #   castClade = clade.copy()
            #   
            #   if layersPresent is None:
            #      castClade["mx"] = int(castClade["mx"]) # this was just casting allready present mx
            #   else:
            #      castClade["mx"] = sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])  # number of trues before mx
            #   
            #   tips.append(castClade)
            #else:
            #   pass
            #   #print "not in pam ",int(clade['mx'])
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
def getSiblingsMx(clade,layersPresent=None):
   """
   @summary: gets all tips that are siblings that are in PAM, (have 'mx')
   """
   if layersPresent is not None:
      lPItems = layersPresent.items()
      lPItems.sort(key=operator.itemgetter(0))
   mx = []
   def getMtxIds(clade):
      if "children" in clade:
         for child in clade['children']:
            getMtxIds(child)
      else:
         if "mx" in clade:
            if layersPresent is None:
               mx.append(int(clade["mx"]))
            else:
               compressedMx = sum([x[1] for x in lPItems[:int(clade["mx"])] if x[1]])
               mx.append(compressedMx)
   getMtxIds(clade)
   return mx
# ..........................
def processTipNotInMatrix(tipsNotInMtx,internal,pam,layersPresent=None):
   """
   @param tipsNotInMtx: list of tip dictionaries
   @param internal: list of internal nodes made in buildTips
   """  
   if layersPresent is not None:   
      lPItems = layersPresent.items()
      lPItems.sort(key=operator.itemgetter(0))
   mxMapping = {} 
   for tip in tipsNotInMtx:
      parentId = [x for x in tip["path"].split(",")][1]  
      parentsChildren = internal[parentId]#['children']  
      for sibling in parentsChildren:
         if tip['pathId'] != sibling['pathId']:
            # not itself
            if 'children' in sibling:
               # recurse unitl it get to tips with 'mx'
               mxs = getSiblingsMx(sibling,layersPresent=layersPresent)
               mxMapping[int(tip['mx'])] = mxs
            else:
               if "mx" in sibling:
                  if layersPresent is None:
                     mxMapping[int(tip['mx'])] = [int(sibling['mx'])]
                  else:
                     mxMapping[int(tip['mx'])] = sum([x[1] for x in lPItems[:int(sibling["mx"])] if x[1]])
               else:
                  mxMapping[int(tip['mx'])] = 0
   la = [] # list of arrays              
   for k in sorted(mxMapping.keys()):
      if isinstance(mxMapping[k],list):
         
         t = np.take(pam,np.array(mxMapping[k]),axis = 1)
         b = np.any(t,axis = 1)  #returns bool logical or
      else:
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
   

   