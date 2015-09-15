import os, sys
import csv
sys.path.append('/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/LmShared')
configPath = '/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/config/config.ini'
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath

from LmClient.lmClientLib import LMClient
client =  LMClient(userId='HuwPrice', pwd='HuwPrice')

#res = client.sdm.postExperiment('ATT_MAXENT',32,4395448,prjScns=[32],
#                                mdlMask=1569,prjMask=1569)
#print res
#print res.id

#
pam = client.rad.getPamCsv(529,651,headers=True,filePath='/home/jcavner/csvTest/birds.csv')
print "done"
#pamiter = csv.reader(pam.splitlines(),delimiter=',')
#pamL = list(pamiter)
#print pamL[0]
#
#c = 0
#for y in pamL:
#   l =  y[3:]
#   lInt = map(int,l)
#   
#   if sum(lInt) > 0:
#      print "not empty"
#      c = c + 1
#print c