import sys, json, hashlib
csl = json.load(sys.stdin)
cj = json.dumps(csl, separators=(',', ':'), sort_keys=True).encode('utf-8')
s1 = bytes.fromhex(sys.argv[1])
print(hashlib.sha384(cj + s1).hexdigest())

