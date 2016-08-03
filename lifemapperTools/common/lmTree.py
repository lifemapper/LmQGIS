import os
import cPickle
import simplejson as json
from itertools import combinations
from operator import itemgetter
#from lifemapperTools.common.NwkToJSON import Parser
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
      self.polyPos = {}
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
               polydesc = {}
               for p in clade["children"]:
                  if 'length' in p:
                     polydesc[int(p["pathId"])] = p['length']
                  else:
                     polydesc[int(p["pathId"])] = ''
               self.polyPos[clade["pathId"]] = {'path':clade["path"],"desc":polydesc}
            for child in clade["children"]:
               recurseClade(child)
         else:
            # tip
            if "length" not in clade:
               self._numberMissingLengths +=1
            else:
               lengths[int(clade["pathId"])] = float(clade["length"]) 
            tipPaths[clade["pathId"]] = ([int(x) for x in clade["path"].split(',')],clade["name"])
              
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
      self._subTrees = subTrees
      
      if self.branchLengths == self.HAS_BRANCH_LEN:
         toSet = []
         for tip in tipPaths:
            copytipPath = list(tipPaths[tip][0])
            copytipPath.pop()  # removes internal pathId from path list for root of tree
            toSum = []
            for pathId in copytipPath:
               toSum.append(treeLengths[pathId])
            urs = sum(toSum)
            s = self._truncate(urs, 3)
            toSet.append(s)
         count = len(set(toSet))
         return bool(1//count)
      else:
         return self.NO_BRANCH_LEN  # need to think about this
   
   @property
   def polytomies(self):
      #if not self.subTrees:
      self.subTrees = self.getTipPaths(self.tree)[2]
      return self._polytomy
   
   @property
   def internalCount(self):
      if not self.subTrees:
         self.subTrees = self.getTipPaths(self.tree)[2]
      return len(self.subTrees)   
   
   @property
   def subTrees(self):
      if not self._subTrees:
         self.checkUltraMetric()
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
   
   
   def makePaths(self, tree):
      """
      @summary: makes paths by recursing tree and appending parent to new pathId
      """
      p = {'c':0}   
      def recursePaths(clade, parent):
         if "children" in clade:
            clade['path'].insert(0,str(p['c']))
            clade['path'] = clade['path'] + parent 
            clade['pathId'] = str(p['c'])
            clade['name'] = str(p['c'])
            for child in clade["children"]:
               p['c'] = p['c'] + 1
               recursePaths(child,clade['path'])
         else:
            # tips
            clade['path'].insert(0,str(p['c']))
            clade['path'] = clade['path'] + parent
            clade['pathId'] = str(p['c'])
            clade['name'] = str(p['c'])
            
      recursePaths(tree,[])
      
      def stringifyPaths(clade):
         if "children" in clade:
            clade['path'] = ','.join(clade['path'])
            for child in clade["children"]:
               stringifyPaths(child)
         else:
            clade['path'] = ','.join(clade['path'])
      stringifyPaths(tree)
      
   def _makeCladeFromEdges(self, edge, n):
      tips = range(1,n+1)
      iNodes = list(set(edge[:,0]))
      m = {}
      for iN in iNodes:
         dx = np.where(edge[:,0]==iN)[0]
         le = list(edge[dx][:,1])
         m[iN] = le
      #print m
      #m = {k[0]:list(k) for k in edge }
      tree = {'pathId':str(n+1),'path':[],'children':[],"name":str(n+1),"length":"0"}
      def recurse(clade,l):
         for x in l:
            if 'children' in clade:
               nc = {'pathId':str(x),'path':[],"name":str(x),"length":'0'}
               if x not in tips:
                  nc['children'] = []
               clade['children'].append(nc)
               if x not in tips:
                  recurse(nc,m[x])
      recurse(tree,m[n+1])
      #self.makePaths(tree)
      
      
      treeDir = "/home/jcavner/PhyloXM_Examples/"
      with open(os.path.join(treeDir,'tree_withoutNewPaths_2.json'),'w') as f:
               f.write(json.dumps(tree,sort_keys=True, indent=4))
      return tree
      
   def makeClades(self, edge):
      """
      @deprecated: false start but has some good ideas in it
      """
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
      
      le = [[x[0],x[1]] for x in edge] 
      le.sort(key=itemgetter(0)) 
      print le
   
   def _getRTips(self,rt):
      
      tips = []
      def findTips(clade):
         if 'children' in clade:
            clade['name'] = ''
            for child in clade['children']:
               findTips(child)
         else:
            # tips
            clade['name'] = ''
            tips.append(clade)
            #clade["pathId"] = t[0]
            #clade["length"] = t[1]
            # if not in sef.tree tips
            # asign childrent from sub tree
      findTips(rt)
      return tips    
      #for t in tips:
      #   findTips(rt)
      
   def resolvePoly(self):
      st = self.subTrees
         #self.getTipPaths(self.tree)  
      # want resolve in order polytomies (keys in self.polyPos
      print len(self.polyPos.keys())
      print len(self.whichNPoly)
      for k in [self.polyPos.keys()[0]]:
         pTips =  self.polyPos[k]['desc'].items()  # these are integers
         n = len(pTips)          
         rt = self.rTree(n)
         tips = self._getRTips(rt)
         for pt, t in zip(pTips,tips):
            #print pt," ",t
            t['pathId'] = pt[0]
            t['length'] = pt[1]
            if str(pt[0]) not in self.tipPaths:
               print "in here"
               t['children'] = self.subTrees[pt[0]]
            else:
               t['name'] = self.tipPaths[str(pt[0])][1]
         # now at this level get the two childrend of the random root
         c1 = rt['children'][0]
         c2 = rt['children'][1]
         self._subTrees[int(k)][0] = c1
         self._subTrees[int(k)][1] = c2
         
      # needs to recurse whole tree and replace paths with empty lists, probably in makePaths
      self.makePaths(self.tree)
      #print
      #print rt
      print len(self.polytomies)  # temp modified self.polytomies to rebuild tipPaths
         # now assign desc tip ids to pathId of rt
         # now get two sides of rt
         
      
   def rTree(self, n, rooted=True):
      """
      @summary: given the number of tips generate a random binary tree by randomly splitting edges
      @param n: number of tips
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
     
      idx = np.where(edge[:,1]==-999)[0]
      for i,x in enumerate(idx):
         edge[x][1] = i + 1
         
      rt = self._makeCladeFromEdges(edge, n)
      return rt
      
      
if __name__ == "__main__":
   
   p = "/home/jcavner/Charolettes_Data/Trees/RAxML_bestTree.12.15.14.1548tax.ultrametric.tre"
   to = LMtree.fromFile(p)
   #print to.checkUltraMetric()
   #print len(to.whichNPoly)
   #edges = to.rTree(5)
   #to._makeCladeFromEdges(edges,5)
   
   to.resolvePoly()
   
   
   
         
   