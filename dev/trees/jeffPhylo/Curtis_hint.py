import requests
import json
from collections import namedtuple

LMHOST = "http://lifemapper.org"

def hint(query, maxRet=50):
   """
   @summary: hint method
   """
   SearchHit = namedtuple('SearchHit', ['name', 'id', 'numPoints'])
   if len(query) < 3:
      raise Exception, "Please provide at least 3 characters to hint service"
   
   url = "%s/hint/species/%s" % (LMHOST, query)
   params =  {'maxReturned': maxRet, 'format': 'json'}
   res = requests.get(url,params=params)
   jObj = json.loads(res.text)
   
   try:
      # Old json format
      jsonItems = jObj.get('columns')[0]
   except:
      # New json format
      jsonItems = jObj.get('hits')
      
   items = []
   for item in jsonItems:
      items.append(SearchHit(name=item.get('name'),
                              id=int(item.get('occurrenceSet')),
                              numPoints=int(item.get('numPoints'))))
   if maxRet is not None and maxRet < len(items):
      items = items[:maxRet]
   return items



if __name__ == "__main__":
   
   print hint("Gulo")