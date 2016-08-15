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
      self.internalPaths = False
      self.labels = False
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
      internalPaths = {}
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
            internalPaths[clade['pathId']] = [int(x) for x in clade["path"].split(',')]
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
      self.internalPaths = internalPaths
      self._lengths = lengths
      self.labelIds = np.array(sorted([int(tl) for tl in self.tipPaths.keys()],reverse=True))
      # this makes certain that labels are in in the order ape phy$labels presents them (bottom up)
      self.labels = np.array([self.tipPaths[str(li)][1] for li in self.labelIds])
      
      return tipPaths, lengths, subTrees
   
   def dropTips(self, tips ):
      """
      @param tips: list or array of tip names to be removed
      """
      
      edge = self._getEdges()
      
      tips = ['A','C','D']
      edge = np.array([[ 7,    8],
                      [ 8,    1], 
                      [ 8,    2], 
                      [ 8,    9], 
                      [ 9,    3], 
                      [ 9,    4], 
                      [ 7,   10], 
                      [10,    5], 
                      [10,    6]] )
      
      self.labels = np.array(["A","B","C","D","L","Z"])
      self.labelIds = np.array([1,2,3,4,5,6])
      self.internalPaths = ['7','8','9','10']
      
      
      # HAVE TO REORDER HERE CLADEWISE, note: don't know if want edge before or after
      # though eges might already be ordered cladewise
      
      nTips = len(self.labels) #Ntip
      nInternal = self.internalCount # Nnode
      nEdge = edge.shape[0]
      NEWROOT = ROOT = nTips + 1
      edge_1 = edge[:,0] 
      edge_2 = edge[:,1]
      
      #keep[match(tip, edge2)] <- FALSE
      labelmask = np.in1d(self.labels,tips)
      tips = self.labelIds[labelmask]
      tips = np.where(np.in1d(edge_2,tips))
      print tips
      keep =  np.ones(nEdge,dtype=bool)
      keep[tips] = False 
      print keep
      
      int_edge2 = [x for x in edge_2 if str(x) in self.internalPaths]
      ints = np.in1d(edge_2,int_edge2)
      print ints
      
      e1Keep = edge_1[keep]
      e2WithE1Keep_not =  np.logical_not(np.in1d(edge_2,e1Keep))
      
      while True:
         sel = reduce(np.logical_and,(e2WithE1Keep_not,ints,keep))
         if not(sum(sel)):
            break
         keep[sel] = False
      newEdges = edge[keep]
      print "new keep ",keep
      print 
      print newEdges
      
      # find which in newEdges[:,1] are terminal, build boolean
      terms = []
      for n in newEdges[:,1]:
         if str(n) in self.tipPaths:
            terms.append(True)
         else:
            terms.append(False)
      TERMS = np.array(terms)
      print 
      #print TERMS
      
      # now want to stash old ids of terms
      #oldNo.ofNewTips <- phy$edge[TERMS, 2]
      oldIdOfNewTips = newEdges[:,1][TERMS]
      # n <- length(oldNo.ofNewTips)
      n = len(oldIdOfNewTips)
      #phy$edge[TERMS, 2] <- rank(phy$edge[TERMS, 2])  # this changes the numbering
      #phy$tip.label <- phy$tip.label[-tip]
      
      ### for testing build list of tips in new edges
      
      t = [2,5,6]
      #######
      
      tree = self._makeCladeFromEdges_tips(newEdges, lengths=True,tips=t)  # this relies on old data structures
      ## so only want it to put in lengths and names?
      #
      treeDir = "/home/jcavner/PhyloXM_Examples/"
      with open(os.path.join(treeDir,'test_dropTips.json'),'w') as f:
         f.write(json.dumps(tree,sort_keys=True, indent=4))
      
         
   def _getEdges(self):
      """
      @summary: makes a (2 * No. internal Nodes) x 2 matrix representation of the tree 
      """
      st = self.subTrees
      if self.tipPaths:
         
         edgeDict = {}

         def recurseEdge(clade):
            if "children" in clade:
               childIds = [int(c['pathId']) for c in clade['children']]
               if int(clade['pathId']) not in edgeDict:
                  edgeDict[int(clade['pathId'])] = childIds
               for child in clade["children"]:
                  recurseEdge(child)        
         recurseEdge(self.tree)
         
         edge_ll = []
         for e in edgeDict.items():
            for t in e[1]:
               edge_ll.append([e[0],t])
         edge = np.array(edge_ll)
         print edge
         return edge
   
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
   
# .........................................................................   
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
            clade['name'] = str(p['c'])
            for child in clade["children"]:
               p['c'] = p['c'] + 1
               recursePaths(child,clade['path'])
         else:
            # tips
            clade['path'].insert(0,str(p['c']))
            clade['path'] = clade['path'] + parent
            clade['pathId'] = str(p['c'])
            #clade['name'] = str(p['c'])  #take this out for real
            
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
            
      stringifyPaths(tree)
   
# .........................................................................   
   def _makeCladeFromEdges(self, edge, lengths=False):
      """
      @summary: MORE GENERIC VERSION,makes a tree dict from a (2 * No. internal node) x 2 numpy matrix
      @param edge: numpy array of edges (integers)
      @param lengths: boolean for adding lengths
      """
      sT = self.subTrees
      tips = self.tipPaths.keys()
      iNodes = list(set(edge[:,0]))
      m = {}  # key is internal node, value is list of terminating nodes
      for iN in iNodes:
         dx = np.where(edge[:,0]==iN)[0]
         le = list(edge[dx][:,1])
         m[iN] = le
      #print m
      #m = {k[0]:list(k) for k in edge }
      tree = {'pathId':str(0),'path':"0",'children':[],"name":str(0)}  # will take out name for internal after testing
      def recurse(clade,l):
         for x in l:
            if 'children' in clade:
               nc = {'pathId':str(x),'path':[],"name":str(x)} # will take out name for internal after testing
               if lengths:
                  nc["length"] = self.lengths[x]
               if str(x) not in tips:
                  nc['children'] = []
                  nc["path"] = ','.join([str(pI) for pI in self.internalPaths[str(x)]])
               else:
                  nc["name"] = self.tipPaths[str(x)][1]
                  nc["path"] = ','.join([str(pI) for pI in self.tipPaths[str(x)][0]])
               clade['children'].append(nc)
               if str(x) not in tips:
                  recurse(nc,m[x])
      recurse(tree,m[0])
      
      return tree
# .........................................................................
   def _makeCladeFromEdges_tips(self, edge, lengths=False,tips=False):
      """
      @summary: MORE GENERIC VERSION,makes a tree dict from a (2 * No. internal node) x 2 numpy matrix
      @param edge: numpy array of edges (integers)
      @param lengths: boolean for adding lengths
      """
      sT = self.subTrees
      
      self.internalPaths = {
                            '7':[7],
                            '10':[10,7],
                            '8':[8,7],
                            '9':[9,8,7]
                            }
      self.tipPaths = {
                       '6':[6,10,7],
                       '5':[5,10,7],
                       '4':[4,9,8,7],
                       '3':[3,9,8,7],
                       '2':[2,8,7],
                       '1':[1,8,7]
                       }
      #tips = self.tipPaths.keys()
      iNodes = list(set(edge[:,0]))
      m = {}  # key is internal node, value is list of terminating nodes
      for iN in iNodes:
         dx = np.where(edge[:,0]==iN)[0]
         le = list(edge[dx][:,1])
         m[iN] = le
      print m
      #m = {k[0]:list(k) for k in edge }
      tree = {'pathId':str(0),'path':"7",'children':[],"name":str(0)}  # will take out name for internal after testing
      def recurse(clade,l):
         for x in l:
            if 'children' in clade:
               nc = {'pathId':str(x),'path':[],"name":str(x)} # will take out name for internal after testing
               if lengths:
                  #nc["length"] = self.lengths[x]
                  pass
               if x not in tips:
                  nc['children'] = []
                  nc["path"] = ','.join([str(pI) for pI in self.internalPaths[str(x)]])
               else:
                  #nc["name"] = self.tipPaths[str(x)][1]
                  nc["path"] = ','.join([str(pI) for pI in self.tipPaths[str(x)]])
                  pass
               clade['children'].append(nc)
               if x not in tips:
                  recurse(nc,m[x])
      recurse(tree,m[7])
      
      return tree
   
# .........................................................................        
   def _makeCladeFromRandomEdges(self, edge, n):
      """
      @summary: makes a tree dict from a (2 * No. internal node) x 2 numpy matrix
      @param edge: numpy array of edges
      @param n: number of tips
      """
      tips = range(1,n+1)  # based on numbering convention in R
      iNodes = list(set(edge[:,0]))
      m = {}  # key is internal node, value is list of terminating nodes
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
      
      
      #self.makePaths(self.tree)
      self._subTrees = False
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
               #print pt," ",t
         # now at this level get the two childrend of the random root
         c1 = rt['children'][0]
         c2 = rt['children'][1]
         
         st_copy[int(k)] = []
         st_copy[int(k)].append(c1)
         st_copy[int(k)].append(c2)
      print "finihsed loop"   
      # needs to recurse whole tree and replace paths with empty lists, probably in makePaths
      removeList = list(self.polyPos.keys())
      def replaceInTree(clade):
         if "children" in clade:
            #if clade["pathId"] in self.polyPos.keys():
            if clade["pathId"] in removeList:
               idx = removeList.index(clade['pathId'] )
               del removeList[idx]
            #if clade["pathId"] == polyKey:
               clade["children"] = st_copy[int(clade["pathId"])]
               #return
            for child in clade["children"]:
               replaceInTree(child)
         else:
            pass    
         
      
      #newTree = {'pathId':'0','path':[],'children':st_copy[0]}
           
      newTree = self.tree.copy()
      
      replaceInTree(newTree)  
      self.makePaths(newTree)
      pc, tmpPaths = self.tempCountPoly(newTree)
      self.tree = newTree  
      #print pc
      #print "***"
      #print self.internalNo
      #print self.tipCo
      #print "***"
      #print "BINARY ", bool(1//(self.tipCo['tc'] - self.internalNo['ic']))
      
      return newTree
        
      
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
         
      rt = self._makeCladeFromRandomEdges(edge, n)
      return rt
      
      
if __name__ == "__main__":
   
   p = "/home/jcavner/Charolettes_Data/Trees/RAxML_bestTree.12.15.14.1548tax.ultrametric.tre"
   
   p = "/home/jcavner/PhyloXM_Examples/test_poly.json"
   
   to = LMtree.fromFile(p)
   
   #print "first tips ", to.tipCount
   #print "first internal ",to.internalCount
   #print
   
   #treeDir = "/home/jcavner/PhyloXM_Examples/"
   #with open(os.path.join(treeDir,'Charolettetree_withPoly_2.json'),'w') as f:
   #   f.write(json.dumps(to.tree,sort_keys=True, indent=4))
   
   #rt = to.rTree(125)
   #to.makePaths(to.tree)
   #to._subTrees = False
   #print to.polytomies   
   
   #######################
   #to.resolvePoly()
   
   #to.subTrees = False
   #st = to.subTrees
   #####################
   
   #edges = to._getEdges()
   #tree = to._makeCladeFromEdges(edges,lengths=True)
   
   to.dropTips(['B','D','H','I','J','K']) # 'A','C','D' # 'B','D'
   
   #treeDir = "/home/jcavner/PhyloXM_Examples/"
   #with open(os.path.join(treeDir,'tree_fromEdges.json'),'w') as f:
   #   f.write(json.dumps(tree,sort_keys=True, indent=4))
   #   
   #to2 = LMtree.fromFile(os.path.join(treeDir,'tree_withoutNewPaths_2_YES.json'))
   
   #print "after tips ", to.tipCount
   #print "after internal ",to.internalCount
   
         
   