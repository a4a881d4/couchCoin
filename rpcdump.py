#!/usr/lib/python
from jsonrpc import ServiceProxy
import json
import sys

class rpcdump:
	def __init__(self,url):	
		self.s = ServiceProxy("http://%s" % url)
		
	def getHash(self,height):
		return self.s.getblockhash(height)
		
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
	rd = rpcdump(sys.argv[1])
	hash = rd.getHash(int(sys.argv[2]))
	block = rd.getBlock(hash)
	print json.dumps(block, sort_keys=True, indent=2 )		
