import os
import cPickle
import simplejson as json
from itertools import combinations
from operator import itemgetter
from NwkToJSON import Parser
import numpy as np
from random import randint


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
      self._lengths = False
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
      self._lengths = lengths
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
   def lengths(self):
      if not self._lengths:
         self.subTrees = self.getTipPaths(self.tree)[2]
      return self._lengths
     
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
   
   
   def makeClades(self, edge):
      
      iNodes = list(set(edge[:,0])) #.sort()  # unique internal nodes from edges
      terminalEdges = [list(r) for r in edge if r[0] > r[1]]
      terminalLookUp = {}
      for row in terminalEdges:
         pt = row[0]
         child = {'pathId':row[1],'path':''}
         if pt not in terminalLookUp:
            terminalLookUp[pt] = {'pathId':pt,'path':'','children':[child]}   
         else:
            terminalLookUp[pt]['children'].append(child)
      print
      #for f in terminalLookUp.items():
      #   print f   
      le = [[x[0],x[1]] for x in edge] 
      le.sort(key=itemgetter(0)) 
      print le
      tree = {'pathId':le[0][0],'path':'','children':[]} 
      if le[0][1] in terminalLookUp:
         tree['children'].append(terminalLookUp[le[0][1]])
      if le[1][1] in terminalLookUp:
         tree['children'].append(terminalLookUp[le[1][1]])
      if le[0][0] in terminalLookUp:
         tree['children'].append(terminalLookUp[le[0][0]]['children'][0])
      
      # here is also needs to check if if child is tip, e.g.   
      # [[8, 1], [8, 9], [9, 10], [9, 12], [10, 2], [10, 11], [11, 3], [11, 4], [12, 5], [12, 13], [13, 6], [13, 7]]
      # {'pathId': 8, 'path': '', 'children': []}
      print tree
      
      def recurse(clade):
         if 'children' in clade:
            if len(clade['children']) == 1:
               pass
            for child in clade:
               recurse(clade)
         else:
            pass
         
         
         
      
      
   def rTree(self, n, rooted=True):
      """
      @note: this is just for <= 4 so far
      """
      def generate(n, pos):
         n1 = randint(1,n-1)
         n2 = n - n1
         po2 = pos + 2 * n1 - 1
         edge[pos][0] = nod['nc']
         edge[po2][0] = nod['nc']
         nod['nc'] = nod['nc'] + 1
         if n1 > 2:
            edge[pos][1] = nod['nc']
            generate(n1, pos+1)
         elif n1 == 2:
            edge[pos+1][0] = nod['nc']
            edge[pos+2][0] = nod['nc']
            edge[pos][1]   = nod['nc']
            nod['nc'] = nod['nc'] + 1
         if n2 > 2:
            edge[po2][1] = nod['nc']
            generate(n2, po2+1)
         elif n2 == 2:
            edge[po2 + 1][0] = nod['nc']
            edge[po2 + 2][0] = nod['nc']
            edge[po2][1]    = nod['nc']
            nod['nc'] = nod['nc'] + 1
         
      nbr = (2 * n) - 3 + rooted
      edge =  np.array(np.arange(0,2*nbr)).reshape(2,nbr).T
      edge.fill(-999)
      nod = {'nc': n + 1}
      generate(n,0)
      print edge
      print
      idx = np.where(edge[:,1]==-999)[0]
      for i,x in enumerate(idx):
         edge[x][1] = i + 1
      print edge
      return edge
      
      
if __name__ == "__main__":
   
   p = "/home/jcavner/Charolettes_Data/Trees/RAxML_bestTree.12.15.14.1548tax.ultrametric.tre"
   to = LMtree.fromFile(p)
   #print to.checkUltraMetric()
   #print len(to.whichNPoly)
   edges = to.rTree(7)
   to.makeClades(edges)
   
   
   
         
   