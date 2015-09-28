import os
import zipfile
import shutil
import commands


out = "/home/jcavner/TashiASCII_July20_2015/"
zipDir = "/home/jcavner/TashiJuly16_2015Package_Zips/"

res = commands.getoutput('ls %s*.zip' % (zipDir))  
zipPaths = res.split('\n')

count = 0
for zipPath in zipPaths:
   
   zipNameNoExtension = os.path.basename(zipPath).replace(".zip","")
   
   with zipfile.ZipFile(zipPath) as zpf:
      for m in zpf.namelist():
         if "median.asc" in os.path.basename(m):
            src = zpf.open(m)
            tg = file(os.path.join(out,zipNameNoExtension+".asc"),'wb')
            with src,tg:
               shutil.copyfileobj(src,tg)
   count += 1
   
print count       