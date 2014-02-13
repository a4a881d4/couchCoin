#!/usr/lib/python
from jsonrpc import ServiceProxy
import json
import sys

class rpcdump:
	def __init__(self,url):	
		self.s = ServiceProxy("http://%s" % url)
		self.set2Begin()
		
	def set2Begin(self):
		self.current=self.getHash(0)
		return self.current
		
	def next(self):
		self.current=self.nextBlock(self.current)
		return self.current
		
	def previous(self):
		self.current=self.previousBlock(self.current)
		return self.current
		
	def set2End(self):
		self.current=self.getHash(self.getTop())
		return self.current
	
	def getTop(self):
		info = self.s.getinfo()
		return info['blocks']-1
		
	def getHash(self,height):
		return self.s.getblockhash(height)
	
	def nextBlock(self,h):
		block = self.getBlock(h)
		if 'nextblockhash' in block:
			return block['nextblockhash']
		else:
			return None
		
	def previousBlock(self,h):
		block = self.getBlock(h)
		if 'previousblockhash' in block:
			return block['previousblockhash']
		else:
			return None
		
	def getBlock(self,h):
		block = self.s.getblock(h)
		dump = {}
		for key in ['previousblockhash','nextblockhash','tx','time','height']:
			if key in block:
				dump[key]=block[key]
		dump['type']='block'
		dump['_id']=block['hash']
		return dump
		
	def getTx(self,txid):
		try:
			txraw = self.s.getrawtransaction(txid)
			tx = self.s.decoderawtransaction(txraw)
			dump = {}
			dump['type']='tx'
			dump['_id']=tx['txid']
			dump['vin']=[]
			for x in tx['vin']:
				y={}
				for key in ['coinbase','txid','vout']:
					if key in x:
						y[key]=x[key]
				dump['vin'].append(y)
			dump['vout']=tx['vout']
			for x in dump['vout']:
				if 'scriptPubKey' in x:
					for key in ['asm','hex','reqSigs']:
						if key in x['scriptPubKey']:
							del x['scriptPubKey'][key]
			return dump
		except:
			pass
		return None

if __name__=='__main__':
	from couchAPI import *
	with open(sys.argv[1]) as json_data:
		conf = json.load(json_data)
		json_data.close()
	db = couchAPI(conf['couchdbuser'],conf['couchdbpass'],conf['couchdburl'])	
	db.setDB('coinbase')
	
	url = "%s:%s@127.0.0.1:%d" % (conf['rpcuser'],conf['rpcpass'],conf['rpcport'])
	rd = rpcdump(url)
	
	hash = rd.next()
	while( hash!=None ):
		if db.has(hash):
			print hash, " OK"
		else:
			print hash, " miss"
			break
		hash = rd.next()