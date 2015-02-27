import json

with open('linrel_topics.json') as f :
    for i in [ k for k,v in json.load(f).iteritems() if 'stat.ML' in v ] :
        print i

