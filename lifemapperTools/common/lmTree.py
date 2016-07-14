import os
import cPickle
import simplejson as json
from itertools import combinations
from NwkToJSON import Parser

class LMtree():
   
   NO_BRANCH_LEN = 0
   MISSING_BRANCH_LEN = 1
   HAS_BRANCH_LEN = 2
   JSON_EXT = ".json"
   NHX_EXT = [".nhx",".tre"]
   
   
   def __init__(self,treeDict):
      
      self.tree = treeDict
      self._polytomy = False
      self._numberMissingLengths = 0
      self._subTrees = False
      self.tipPaths = False
      self.whichNPoly = []
      
   @classmethod
   def fromFile(cls,dLoc):
      if os.path.exists(dLoc):
         f,e = os.path.splitext(dLoc)
         if e == cls.JSON_EXT:
            with open(dLoc,'r') as f:
               jsonstr = f.read()
            return cls(json.loads(jsonstr))
         elif e in cls.NHX_EXT:
            phyloDict = cls.convertFromNewick(dLoc) 
            if  isinstance(phyloDict,Exception):
               raise ValueError("Expected an python dictionary "+str(phyloDict))
            else:
               return cls(phyloDict)          
      else:
         pass # ?
      
   @classmethod
   def convertFromNewick(cls,dLoc):
      
      try:
         tree = open(dLoc,'r').read()
         sh = Parser.from_string(tree)
         parser = Parser(sh)
         result,parentDicts = parser.parse()
      except Exception, e:
         result = e
      return result
      
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
               self.whichNPoly.append(int(clade["pathId"]))
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
   
   
   def _truncate(self,f, n):
      """
      @summary: Truncates/pads a float f to n decimal places without rounding
      """
      
      s = '{}'.format(f)
      if 'e' in s or 'E' in s:
         return '{0:.{1}f}'.format(f, n)
      i, p, d = s.partition('.')
      return '.'.join([i, (d+'0'*n)[:n]])
   
   
   def checkUltraMetric(self):
      """
      @summary: check to see if tree is ultrametric, all the way to the root
      """
      tipPaths,treeLengths,subTrees = self.getTipPaths(self.tree)
      toSet = []
      for tip in tipPaths:
         copytipPath = list(tipPaths[tip])
         copytipPath.pop()  # removes internal pathId from path list for root of tree
         toSum = []
         for pathId in copytipPath:
            toSum.append(treeLengths[pathId])
         urs = sum(toSum)
         s = self._truncate(urs, 3)
         toSet.append(s)
      count = len(set(toSet))
      return bool(1//count)
   
   @property
   def polytomies(self):
      if not self.subTrees:
         self.subTrees = self.getTipPaths(self.tree)[2]
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
         self.subTrees = self.getTipPaths(self.tree)[2]  
      return len(self.tipPaths)
      
   @property
   def binary(self):
      return bool(1//(self.tipCount - self.internalCount))
      
   @property
   def branchLengths(self):
      if not self.tipPaths:
         self.subTrees = self.getTipPaths(self.tree)[2] 
      if self._numberMissingLengths == 0:
         return self.HAS_BRANCH_LEN
      else:    
         if self._numberMissingLengths == (self.tipCount + self.internalCount -1):
            return self.NO_BRANCH_LEN
         else:
            return self.MISSING_BRANCH_LEN
      
if __name__ == "__main__":
   
   p = "/home/jcavner/Charolettes_Data/Trees/RAxML_bestTree.12.15.14.1548tax.ultrametric.tre"
   to = LMtree.fromFile(p)
   print to.checkUltraMetric()
   print len(to.whichNPoly)
   
   
   
         
   