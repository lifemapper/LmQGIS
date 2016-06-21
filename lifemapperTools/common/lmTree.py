import os
import cPickle
import simplejson as json
from itertools import combinations

class LMtree():
   
   NO_BRANCH_LEN = 0
   MISSING_BRANCH_LEN = 1
   HAS_BRANCH_LEN = 2
   
   def __init__(self,treeDict):
      
      self.tree = treeDict
      self._polytomy = False
      self._numberMissingLengths = 0
   
   def getTipPaths(self,clade):
      """
      @summary: performs one recursion for all tree info objects
      """
      tipPaths = {}
      lengths =  {}
      subTrees = {}
      def recurseClade(clade):
         if "children" in clade:
            # do stuff in here
            if "length" in clade:  # to control for pathId 0 not having length
               lengths[int(clade["pathId"])] = float(clade["length"])
            else:
               if int(clade['pathId']) != 0:
                  self._numberMissingLengths +=1
            subTrees[int(clade['pathId'])] = clade["children"]
            if len(clade["children"]) > 2:
               self._polytomy = True
            for child in clade["children"]:
               recurseClade(child)
         else:
            # tip
            if "length" not in clade:
               self._numberMissingLengths +=1
            else:
               lengths[int(clade["pathId"])] = float(clade["length"]) 
            tipPaths[clade["pathId"]] = [int(x) for x in clade["path"].split(',')]
              
      recurseClade(clade)
      self.tipPaths = tipPaths
      self.lengths = lengths
      return tipPaths, lengths, subTrees
   
   
   def checkUltraMetric(self):
      """
      @summary: check to see if tree is ultrametric, all the way to the root
      """
      tipPaths,treeLengths,subTrees = self.getTipPaths(self.tree)
      toSet = []
      for tip in tipPaths:
         path = tipPaths[tip].pop()  # removes internal pathId from path list for root of tree
         toSum = []
         for pathId in path:
            toSum.append(treeLengths[pathId])
         s = sum(toSum)
         toSet.append(s)
      count = len(set(toSet))
      return bool(1//count)
   
   @property
   def polytomies(self):
      if not self.subTrees:
         self.getTipPaths(self.tree)
      return self._polytomy
   
   @property
   def internalCount(self):
      if not self.subTrees:
         self.subTrees = self.getTipPaths(self.tree)[2]
      return len(self.subTrees)   
   @property
   def subTrees(self):
      return self._subTrees
         
   @subTrees.setter  
   def subTrees(self, subTrees):
      self._subTrees = subTrees      
      
   @property
   def tipCount(self):
      if not self.tipPaths:
         self.getTipPaths(self.tree)  
      return len(self.tipPaths)
      
   @property
   def binary(self):
      return bool(1//(self.tipCount - self.internalCount))
      
   @property
   def branchLengths(self):
      if not self.tipPaths:
         self.getTipPaths(self.tree) 
      if self._numberMissingLengths == 0:
         return self.HAS_BRANCH_LEN
      else:    
         if self._numberMissingLengths == (self.tipCount + self.internalCount -1):
            return self.NO_BRANCH_LEN
         else:
            return self.MISSING_BRANCH_LEN
      
      
   