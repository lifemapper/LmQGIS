import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
from csv import reader
import math
import os



#ll = [[1,1,1,0,0,0],[0,1,1,1,0,1],[1,1,1,0,0,0],[1,1,1,0,0,0],
#      [0,1,1,1,1,0],[1,1,1,0,0,1],[1,1,1,1,0,0]]

def buildCovarianceAvgPerCell():
   """
   @summary: this is the average covariance of species in each cell, from a 'virtual'
   covariance matrix using the algebraic definition of the matrix, Sigma species
   """
   #X = np.array(ll)
   X = np.load('/home/jcavner/pam_692.npy')  # this is white bellied rat
   #print X
   N = float(X.shape[0])
   S = float(X.shape[1])
   
   O = np.dot(X.T,X)
   omega = O.diagonal()
   omegaprop = omega/N
   XT = X.T
   covAvgsForSpsinSite = []
   for i,site in enumerate(X):
      
      presPositions = np.where(site==1.0)[0]
      if len(presPositions) > 1:
         rowCov = []   
         for comboIdx,c in enumerate(combinations(presPositions,r=2)):    
            #print i," ",c 
            # omegaprop is actually the avg
            cov = sum((XT[c[0]]-omegaprop[c[0]])*(XT[c[1]]-omegaprop[c[1]]))/N
            
            rowCov.append(cov)
         
         avgCov = sum(rowCov) / (comboIdx+1)
         print avgCov
         covAvgsForSpsinSite.append(avgCov)
      elif len(presPositions) == 1:
         print 0.0
         covAvgsForSpsinSite.append(0.0)
      else:  # this is for full pam, take out for pamsum
         print 0.0
         covAvgsForSpsinSite.append('NULL')

def buildTD_SSCov(X):
   """
   @summary: this is the covariance of taxon distance and Sites Shared by each pair
   of species in a cell
   @param X: full PAM
   """
   # for each site (row) find all combinations of species
   # then find all sites shared by each species combination
   f = open('/home/jcavner/AfricaCovarianceTest/td_ssCov_Pearson.txt','w')
   
   XT = X.T
   for i,site in enumerate(X): #[:45]
      print i
      presencePos = np.where(site==1.0)[0]
      # only do this if there are two or more combinations
      if len(presencePos) > 2:  # in other words 3 presences
         sitesSharedPerSpsCombo = []
         tdPerSpsCombo = []
         comboCount = 0
         for comboIdx,combo in enumerate(combinations(presencePos,r=2)):
            TD = getTaxonDistanceBtweenPair(combo[0],combo[1])
            if TD is not None:
               SS = np.dot(XT[combo[0]],XT[combo[1]])
               tdPerSpsCombo.append(TD)
               sitesSharedPerSpsCombo.append(SS)
               comboCount += 1
            
         if comboCount >= 2:  # test this
            avgSS = sum(sitesSharedPerSpsCombo)/float(comboCount)
            avgTD = sum(tdPerSpsCombo)/float(comboCount)
            # make array of avgs            
            SSAvgs = np.empty(comboCount);SSAvgs.fill(avgSS)
            TDAvgs = np.empty(comboCount);TDAvgs.fill(avgTD)
            
            ssArray = np.array(sitesSharedPerSpsCombo)
            tdArray = np.array(tdPerSpsCombo)
            
            # Deviation
            ssDev = ssArray-SSAvgs
            tdDev = tdArray-TDAvgs           
            # calculate variance
            ssVariance = sum(ssDev * ssDev)/float(comboCount)
            tdVariance = sum(tdDev * tdDev)/float(comboCount)
            # calculate std dev
            ssStdDev = math.sqrt(ssVariance)
            tdStdDev = math.sqrt(tdVariance)
            # calculate covariance
            Sxy = sum(ssDev * tdDev)/float(comboCount)
            # calculate Pearsons
            p = Sxy/(ssStdDev * tdStdDev)
            
            f.write('%s,%s,\n' % (Sxy, p))
         else:
            f.write('0.00,0.00,\n')
      else:
         f.write('0.00,0.00,\n')
         #print 0.0
         
         #cov = sum((XT[c[0]]-omegaprop[c[0]])*(XT[c[1]]-omegaprop[c[1]]))/N  # but different
         #print
         #print "Avg ",sumPerSite/float(comboIdx + 1)
   
   f.close()
   print "FINISHED"

def buildLeaves(clade):
   
   if "pathId" in clade:
      allClades[clade["pathId"]] = dict((k,v) for k,v in clade.items() if k != "children")
   if 'children' in clade:
      for child in clade["children"]:
         bL(child)
   else:
      if "mx" in clade:
         tipPathsDict[int(clade['mx'])] = clade['path']


def getTaxonDistanceBtweenPair(mtrxIdx1,mtrxIdx2):
   
   try:
      sps1PathStr = tipPathsDict[mtrxIdx1]
      sps2PathStr = tipPathsDict[mtrxIdx2]
   except:
      totalLen = None
   else:
      pl1  = sps1PathStr.split(',')
      pl2  = sps2PathStr.split(',')
      pL1  = map(int,pl1)
      pL2  = map(int,pl2)
      pS1  = set(pL1)
      pS2   = set(pL2)
      ancId  = max(set.intersection(pS1,pS2)) # greatest common ancestor pathId
      sp1Len = findLengthToId(pL1, ancId)
      sp2Len = findLengthToId(pL2, ancId)
      totalLen = sp1Len + sp2Len
   
   return totalLen

def findLengthToId(path,ancId):
   """
   @param ancId: common ancestor Id
   """
   totLen = 0
   for pathId in path:
      if pathId > ancId:
         length = float(allClades[str(pathId)]["length"])
         totLen = totLen + length
      else:
         break
   return totLen   
   
def findNearest(matches,pathId):
   
   #print matches," ",pathId
   if len(matches) > 1:
      # have to find the shortest one
      shortestList = []        
      for matchList in matches: # goes through each of the match lists
         compare = 0
         for matchId in matchList:
            
            if matchId > pathId:
               
               length = float(allClades[str(matchId)]["length"])
               compare = compare + length
            else:
               shortestList.append(compare)
               break
      shortest = min(shortestList)                                  
            
   elif len(matches) == 1:
      shortest = 0
      for matchId in matches[0]:
         if matchId > pathId:
            length = float(allClades[str(matchId)]["length"])
            shortest = shortest + length
         else:
            break
   return shortest

  
def calcMNTD(pathsInSite):
   """
   @param pathsInSite: list of path strings
   """
   # need a list of paths of every species in a cell from the tree json   
   
   pathList = []
   for path in pathsInSite:
      pl = path.split(',')  # self.list is model from dockable list?
      m  = map(int,pl)  # whole list, or everything minus itself pl[1:]
      pathList.append(m) # integers
   nearestTaxonLengths = []        
   for path in pathList:
      # builds a a searchIn list that excludes current 
      # path
      index = pathList.index(path)
      searchIn = list(pathList) 
      searchIn.pop(index)
      # end search in       
      # loop through pathids the focus path and find lists with a matching pathId
      # and append to matches
      matches = []
      for pathId in path[1:]:           
         for srchPth in searchIn:
            if pathId in srchPth[1:]:
               matches.append(srchPth)
         if len(matches) > 0:
            try:
               nearestLen = findNearest(matches,pathId)                 
               lengthToPathId = findLengthToId(path,pathId)
            except Exception, e:
               return '0.00'
            else:   
               nearestTaxonLengths.append(nearestLen+lengthToPathId)
               break
   totAllLengths = sum(nearestTaxonLengths)
   meanNearestTaxonDist = totAllLengths/float(len(nearestTaxonLengths))
   return meanNearestTaxonDist 
      
def calculateMNTDPerSite(X):
   
   f = open('/home/jcavner/AfricaCovarianceTest/MNTD_PerSite.txt','w')
   for i,site in enumerate(X):
      print i
      # one-dimensional array of where presences are in matrix, 
      # in other words mx or mtrxIdx
      presencePosinSite = np.where(site==1.0)[0]
      # remember not species in pam are in tree necessarily
      if len(presencePosinSite) > 1:
         allPathsForSite = []
         for presencePos in presencePosinSite:
            if presencePos in tipPathsDict:
               tipPath = tipPathsDict[presencePos]
               allPathsForSite.append(tipPath)
         if len(allPathsForSite) >= 2:
            MNTD = calcMNTD(allPathsForSite)
            f.write('%s,\n' % (MNTD))
         else:
            f.write('0.00,\n')
      else:
         f.write('0.00,\n')
      
   f.close()
      
      

def plotCovarianceAgainstStats(statAgainst,title):
   
   basePath = '/home/jcavner/Pooka8/WhiteBelliedRat_627'
   covReader = reader(open(os.path.join(basePath,'cov_fromShp.csv')),delimiter=',')
   statsReader = reader(open(os.path.join(basePath,'stats_fromShp.csv')),delimiter=',')
   
   covList = list(covReader)[1:]
   statsList = list(statsReader)[1:]
   
   statsVector = []
   covVector = []
   for cov,stats in zip(covList,statsList):
      if stats[statAgainst] != '':
         statistic = float(stats[statAgainst].replace(' ','')) # replace leading zeros
         statsVector.append(statistic)
         covariance = float(cov[8])
         covVector.append(covariance)
   covArray = np.array(covVector)
   statArray = np.array(statsVector)
   plt.scatter(statArray,covArray)
   plt.title(title)
   
   plt.show()


def plot_sstd_rad():
   
   basePath = '/home/jcavner/AfricaCovarianceTest'
   ss_td_mntd_reader = reader(open(os.path.join(basePath,'ss_td_mntd_fromShp.csv')),delimiter=',')
   rad_reader = reader(open(os.path.join(basePath,'rad.csv')),delimiter=',')
   
   ss_tdLL = list(ss_td_mntd_reader)[1:]
   radLL = list(rad_reader)[1:]
   
     
   temprad = list(radLL)
   radLL  = [site for site in temprad if site[3] != '']
   idxToRemove = [i for i,site in enumerate(temprad) if site[3] == '']
   
   tempss = list(ss_tdLL)  
   ss_tdLL = [site for site in tempss if tempss.index(site) not in idxToRemove]
   #ss_tdLL = [site for site in tempss if site[1] != '      0.00000000' and site[2] != '      0.00000000']
      
   
   print "LEN SS ",len(ss_tdLL)
   print "LEN RAD ",len(radLL)
   
   ss_td_a = np.array(ss_tdLL)
   rad_a = np.array(radLL)
   
   radColumns = { 'phi':3, 'richness': 4,  'propSpecDiv':5, 'avgpropRaSize':6 }
   ss_tdColumns = {'td_ssCov':1,'MNTD':2}
   for radItem in radColumns.items():
      for ss_tdItem in ss_tdColumns.items():
         title = 'X: %s Y: %s' % (ss_tdItem[0],radItem[0],)
         ax = plt.figure().add_subplot(111)
         ax.set_title(title)
         
         radCol = rad_a[:,radItem[1]]
         ts_ssCol = ss_td_a[:,ss_tdItem[1]]
         
         rad = map(float,map(lambda x: x.replace(' ',' '),radCol))
         ts_ss = map(float,map(lambda x: x.replace(' ',' '),ts_ssCol))
         ax.scatter(ts_ss, rad) # X axis, Y axis
         
   plt.show()
      
   
   

tjson = """
{
"pathId":"0",
"children":[
              {
              "pathId":"1",
              "path":"1,0",
              "length":"8",
              "children":[
                           {"pathId":"5",
                            "path":"5,1,0",
                            "length":"1",
                            "children":[
                                         {"pathId":"7","path":"7,5,1,0","length":""},
                                         {"pathId":"8","path":"8,5,1,0","length":"2","mx":"1"}
                                       ]
                           },
                           {"pathId":"6",
                           "path":"6,1,0",
                           "length":"4",
                           "children":[
                                         {"pathId":"9","path":"9,6,1,0","length":""},
                                         {"pathId":"10","path":"10,6,1,0","length":"3","mx":"0"}
                                      ]
                           }
                         ]           
              },
              {
              "pathId":"2",
              "path":"2,0",
              "length":"2",
              "children":[
                           {"pathId":"3","path":"3,2,0","length":""},
                           {"pathId":"4","path":"4,2,0","length":"4","mx":"2"}               
                         ]
              }
          ]
}"""





allClades = {}
tipPathsDict = {}
bL = buildLeaves

# need to read in tree that matches pam

#import json
#
#baseUrl = '/home/jcavner/AfricaCovarianceTest/'
#
#treePath = os.path.join(baseUrl,'tree.json')
#tjson = open(treePath,'r').read()
#
#pamPath = os.path.join(baseUrl,'pam_512.npy')
#pam = np.load(pamPath)
#
#treeDict = json.loads(str(tjson))
#buildLeaves(treeDict)
#
##calculateMNTDPerSite(pam)
#buildTD_SSCov(pam)


plot_sstd_rad()

#################

#plotCovarianceAgainstStats(3,'phi')







