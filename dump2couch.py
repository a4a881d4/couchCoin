from couchAPI import *
from rpcdump import *
import json
import sys

class dump2couch:
	def __init__(self,conf):
		self.conf=conf
		url = "%s:%s@127.0.0.1:%d" % (conf['rpcuser'],conf['rpcpass'],conf['rpcport'])
		print "connect rpc :",url
		self.rd = rpcdump(url)
		self.db = couchAPI(conf['couchdbuser'],conf['couchdbpass'],conf['couchdburl'])	
		self.db.setDB('coinbase')
	
	def getHash(self,height):
		return self.rd.getHash(height)
		
	def submit(self,hash):
		block=self.rd.getBlock(hash)
		block['cointype']=self.conf['coin']
		print json.dumps(block, sort_keys=True, indent=2 )
		self.db.save(block)
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
						
							
if __name__=='__main__':
	with open(sys.argv[1]) as json_data:
		conf = json.load(json_data)
		json_data.close()
	worker = dump2couch(conf)
	start=int(sys.argv[2])
	end=int(sys.argv[3])
	for height in range(start,end):
		hash=worker.getHash(height)
		print "Hash(",height,"): ",hash
		worker.submit(hash)
		