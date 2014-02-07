from couchAPI import *
from rpcdump import *
import json
import sys

if __name__=='__main__':
	with open(sys.argv[1]) as json_data:
		conf = json.load(json_data)
		json_data.close()
	url = "%s:%s@127.0.0.1:%d" % (conf['rpcuser'],conf['rpcpass'],conf['rpcport'])
	print "connect rpc :",url
	rd = rpcdump(url)
	db = couchAPI(conf['cloudantuser'],conf['cloudantpass'],conf['cloudanturl'])	
	db.setDB('coinbase')
	
	start=int(sys.argv[2])
	end=int(sys.argv[3])
	for height in range(start,end):
		hash=rd.getHash(height)
		print "Hash(",height,"): ",hash
		block=rd.getBlock(hash)
		block['cointype']=conf['coin']
		print json.dumps(block, sort_keys=True, indent=2 )
		db.save(block)
		txids = block['tx']
		for txid in txids:
			tx=rd.getTx(txid)
			if tx!=None:
				tx['cointype']=conf['coin']
				for v in tx['vout']:
					v['spend']=False	
				print json.dumps(tx, sort_keys=True, indent=2 )
				db.save(tx)
				for v in tx['vin']:
					if 'txid' in v:
						previousTx=db.get(v['txid'])
						for txout in previousTx['vout']:
							if v['vout']==txout['n']:
								txout['spend']=True
						db.save(previousTx)
						print "======update previousTx============"
						print json.dumps(previousTx, sort_keys=True, indent=2 )

