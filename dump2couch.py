from couchAPI import *
from rpcdump import *
import json
import sys
import getopt

class dump2couch:
	def __init__(self,conf):
		self.conf=conf
		url = "%s:%s@127.0.0.1:%d" % (conf['rpcuser'],conf['rpcpass'],conf['rpcport'])
		print "connect rpc :",url
		self.rd = rpcdump(url)
		self.db = couchAPI(conf['couchdbuser'],conf['couchdbpass'],conf['couchdburl'])	
		self.db.setDB('coinbase')
		hash = self.rd.set2Begin()
		if not self.db.has(hash):
			self.submit(hash)
		self.breakhash=None

	def setBreak(self,h):
		self.breakhash=self.rd.getHash(h)
		
	def setCurrent(self,h):
		self.rd.setCurrent(h)
			
	def getHash(self,height):
		return self.rd.getHash(height)
	
	def getHeight(self,hash):
		block = self.rd.getBlock(hash)
		if block['type']=='block':
			return int(block['height'])
		else:
			return -1
			
	def rebuild(self):
		hash = self.rd.next()
		while( hash!=None and hash!=self.breakhash ):
			if self.db.has(hash):
				print hash, " OK"
			else:
				print "Hash( %8d )" % self.getHeight(hash), hash, " submit"
				self.submit(hash)
			hash = self.rd.next() 	

	def sync(self):
		hash = self.rd.getCurrent()
		while( not self.db.has(hash) ):
			print "Hash( %8d )" % self.getHeight(hash), hash, " miss"
			hash = self.rd.previous()
			if hash==None:
				hash = self.rd.set2Begin()
				break
		self.rebuild() 	

		
	def submit(self,hash):
		block=self.rd.getBlock(hash)
		block['cointype']=self.conf['coin']
		print json.dumps(block, sort_keys=True, indent=2 )
		txids = block['tx']
		for txid in txids:
			tx=self.rd.getTx(txid)
			if tx!=None:
				tx['cointype']=self.conf['coin']
				for v in tx['vout']:
					v['spend']=False	
				print json.dumps(tx, sort_keys=True, indent=2 )
				self.db.save(tx)
				for v in tx['vin']:
					if 'txid' in v:
						previousTx=self.db.get(v['txid'])
						for txout in previousTx['vout']:
							if v['vout']==txout['n']:
								txout['spend']=True
						self.db.save(previousTx)
						print "======update previousTx============"
						print json.dumps(previousTx, sort_keys=True, indent=2 )
		self.db.save(block)
		
						
							
if __name__=='__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'c:s:e:', ['dump', 'check'])
	except getopt.GetoptError as err:
		print >> sys.stderr, str(err)
		sys.exit(1)
	
	for opt, arg in opts:
		if opt == '-c':
			with open(arg) as json_data:
				conf = json.load(json_data)
				json_data.close()
				worker = dump2couch(conf)
				worker.rd.set2End()
		if opt == '-s':
			worker.setCurrent(int(arg))
		if opt == '-e':
			worker.setBreak(int(arg))
		if opt == '--dump':
			worker.sync()
	