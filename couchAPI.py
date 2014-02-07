import couchdb
import sys
import json

class couchAPI:
	def __init__(self,USERNAME,PASSWORD,url):
		self.couch = couchdb.Server(url)
		self.couch.resource.credentials = (USERNAME, PASSWORD)
		self.db = None
		
	def setDB(self,db):
		self.db=self.couch[db]
	
	def createDB(self,db):
		self.couch.create(db)
		
	def save(self,doc):
		if not '_rev' in doc:
			if doc['_id'] in self.db:
				previousDoc = self.db[doc['_id']]
				doc['_rev']=previousDoc['_rev']
		doc_id,doc_rev = self.db.save(doc)
		return doc_id
		
	def get(self,doc_id):
		return self.db[doc_id]
		
	def has(self,doc_id):
		return doc_id in self.db
		
	

if __name__=='__main__':
	with open(sys.argv[1]) as json_data:
		conf = json.load(json_data)
		json_data.close()
	couch = couchAPI(conf['cloudantuser'],conf['cloudantpass'],conf['cloudanturl'])
	couch.createDB('coinbase')
