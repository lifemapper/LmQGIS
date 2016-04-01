import csv
import os,sys
import cPickle
import numpy

base = "/home/jcavner/PAMBrowser"

pamLL = list(csv.reader(open(os.path.join(base,'JoinedPAM.csv'))))

pD = cPickle.load(open("/home/jcavner/WorkshopWS/AfricaMammals_1055/sitesPresent.pkl"))
lyrsP = pD[1438]['layersPresent']

lpKeys = [k for k in lyrsP.keys() if lyrsP[k]]  # now use index trick?
lpKeys.sort()

#print len(pamLL[0])
#print len(pamLL)
print pamLL[0]
print pamLL[1]
print pamLL[0][9:]

def truncate(f, n):
   '''Truncates/pads a float f to n decimal places without rounding'''
   s = '{}'.format(f)
   if 'e' in s or 'E' in s:
      return '{0:.{1}f}'.format(f, n)
   i, p, d = s.partition('.')
   return '.'.join([i, (d+'0'*n)[:n]])

rll_1 = numpy.array(pamLL[1:],dtype=numpy.dtype(float))
#print pamLL[1][3+9] # add 9 , yes
rll = rll_1[:,9:]
print len(pamLL[0])
print rll.shape

mxsCSV = pamLL[0][9:]  # just header

coordByMx = {}
for c in mxsCSV:
   mx = int(c.split('_')[2])
   colIdx = mx #+ 9
   lcoordTuples = []
   if sum(rll[:,colIdx]) > 0:
      rowIdx = 0
      for site in rll[:,colIdx]:     
         if int(site):
            x = truncate(float(pamLL[rowIdx+1][0]),4)
            y = truncate(float(pamLL[rowIdx+1][1]),4)
            lcoordTuples.append([x,y])
         rowIdx += 1 
      coordByMx[mx] = lcoordTuples

cPickle.dump(coordByMx,open("/home/jcavner/PAMBrowser/coordByMtx.pkl","wb"))
cBm = cPickle.load(open("/home/jcavner/PAMBrowser/coordByMtx.pkl"))  
#print coordByMx[6]  
wr = csv.writer(open("/home/jcavner/PAMBrowser/presence-data_sps6.csv",'w'))
nl = list(cBm[56])
for l in nl:
   l.extend(['z','z','z'])
nl.insert(0,['lon','lat','code','city','country'])   
wr.writerows(nl)