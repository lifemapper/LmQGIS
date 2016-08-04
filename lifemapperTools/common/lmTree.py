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
      print "called getTipPaths"
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
      print "in make Paths"
      p = {'c':0}   
      def recursePaths(clade, parent):
         if "children" in clade:
            clade['path'].insert(0,str(p['c']))
            clade['path'] = clade['path'] + parent 
            clade['pathId'] = str(p['c'])
            #clade['name'] = str(p['c'])
            for child in clade["children"]:
               p['c'] = p['c'] + 1
               recursePaths(child,clade['path'])
         else:
            # tips
            clade['path'].insert(0,str(p['c']))
            clade['path'] = clade['path'] + parent
            clade['pathId'] = str(p['c'])
            #clade['name'] = str(p['c'])
            
      def takeOutStrPaths(clade):
         
         if "children" in clade:
            clade["path"] = []
            clade["pathId"] = ''
            for child in clade["children"]:
               takeOutStrPaths(child)
         else:
            clade["path"] = []
            clade["pathId"] = ''
      
      takeOutStrPaths(tree)    
      
      recursePaths(tree,[])
      
      def stringifyPaths(clade):
         if "children" in clade:
            clade['path'] = ','.join(clade['path'])
            for child in clade["children"]:
               stringifyPaths(child)
         else:
            clade['path'] = ','.join(clade['path'])
            
      #stringifyPaths(tree)
      
      
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
      
      
      #treeDir = "/home/jcavner/PhyloXM_Examples/"
      #with open(os.path.join(treeDir,'tree_withoutNewPaths_2.json'),'w') as f:
      #         f.write(json.dumps(tree,sort_keys=True, indent=4))
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
      """
      @summary: recurses a random subtree and returns a list of its tips
      """
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
            
      findTips(rt)
      return tips    
   
   def tempCountPoly(self, tree):
      pc = {'c':0}
      self.internalNo = {'ic':0}
      self.tipCo = {'tc':0}
      tmpPaths = {}
      def recurseCount(clade):
         tmpPaths[clade["pathId"]] = clade["path"]
         if "children" in clade:
            if type(clade) == str:
               print clade
            if len(clade["children"]) > 2:
               pc['c'] = pc['c'] + 1
            self.internalNo['ic'] = self.internalNo['ic'] + 1
            for child in clade["children"]:
               recurseCount(child)
         else:
            self.tipCo['tc'] = self.tipCo['tc'] + 1
      recurseCount(tree)
      return pc, tmpPaths
      
   def resolvePoly(self):
      st_copy = self.subTrees.copy()
      
      # want resolve in order polytomies (keys in self.polyPos
     
      print len(self.whichNPoly)
      for k in self.polyPos.keys():
         pTips =  self.polyPos[k]['desc'].items()  # these are integers
         n = len(pTips)          
         rt = self.rTree(n)
         tips = self._getRTips(rt)
         for pt, t in zip(pTips,tips):
            #print pt," ",t
            t['pathId'] = str(pt[0])  # might not need this
            t['length'] = pt[1]
            if str(pt[0]) not in self.tipPaths:
               t['children'] = self.subTrees[pt[0]]
            else:
               t['name'] = self.tipPaths[str(pt[0])][1]
               print pt," ",t
         # now at this level get the two childrend of the random root
         c1 = rt['children'][0]
         c2 = rt['children'][1]
         
         st_copy[int(k)] = []
         st_copy[int(k)].append(c1)
         st_copy[int(k)].append(c2)
      print "finihsed loop"   
      # needs to recurse whole tree and replace paths with empty lists, probably in makePaths
      
      def replaceInTree(clade):
         if "children" in clade:
            if clade["pathId"] in self.polyPos.keys():
               clade["children"] = st_copy[int(clade["pathId"])]
            for child in clade["children"]:
               replaceInTree(child)
               
      t = self.tree.copy()
      replaceInTree(t)  
      #self.makePaths(t)
      #pc, tmpPaths = self.tempCountPoly(t)
      
      #print pc
      #print "BINARY ", bool(1//(self.tipCo['tc'] - self.internalNo['ic']))
      #
      #for k in tmpPaths:
      #   l = [x for x in tmpPaths[k].split(',')]
      #   if '' in l:
      #      #print tmpPaths[k]
      #      print l
      #      break
      
      #self._subTrees = False
      #print "poly ",self.polytomies
      #print len(self.whichNPoly)
      #self.tree = t  
      #print self.tempCountPoly(self.tree)
         # now assign desc tip ids to pathId of rt
         # now get two sides of rt
        
      
   def rTree(self, n, rooted=True):
      """
      @summary: given the number of tips generate a random binary tree by randomly splitting edges, 
      equal to foo branch in ape's rtree
      @param n: number of tips
      @note: this is just for >= 4 so far, but not be a problem
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
   
   #rt = to.rTree(125)
   #to.makePaths(to.tree)
   #to._subTrees = False
   #print to.polytomies   
   
   to.resolvePoly()
   
   
   treeDir = "/home/jcavner/PhyloXM_Examples/"
   with open(os.path.join(treeDir,'tree_withoutNewPaths_2.json'),'w') as f:
      f.write(json.dumps(to.tree,sort_keys=True, indent=4))
         
   