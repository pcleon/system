#encoding:utf-8

import sys

f=sys.argv[1]
log = open(f,"r")
result_dict = {}
useful_req = {}

useful_req = {  "us":{"count":0,"time":0},
                "ms":{"count":0,"time":0},
                "s":{"count":0,"time":0}
            }

for line in log.readlines():
    line = line.rstrip("\n")
    if not line: continue
    linelog = line.split('\t')
    if len(linelog) != 12: continue

    try:
        http_code = int(linelog[4].lstrip('[').rstrip(']'))
        if http_code > 399 :
            if (http_code == 400 or http_code == 408) and linelog[7] == '[-]' and linelog[8] == '[-]':
                continue
            print line
        else :
            req_time = float( linelog[-1].lstrip('[').rstrip(']') )
            if ( req_time == 0.000 ):
                useful_req["us"]["count"] += 1
                useful_req["us"]["time"] += req_time
            elif ( req_time > 0.000 and req_time < 1.0 ):
                useful_req["ms"]["count"] += 1
                useful_req["ms"]["time"] += req_time
            else :
                useful_req["s"]["count"] += 1
                useful_req["s"]["time"] += req_time

    except ValueError:
        print line
        continue

    http_code = str(http_code)
    cost_time = 0.0
    try:
        cost_time = float(linelog[-1].lstrip('[').rstrip(']'))
    except ValueError:
        pass

    if http_code not in result_dict:
        result_dict[http_code] = {}
        result_dict[http_code]['count'] = 1
        result_dict[http_code]['time'] = cost_time
    else:
        result_dict[http_code]['count'] += 1
        result_dict[http_code]['time'] += cost_time
else:
#    print "\n"
    print "#======================================"
    print "#status\tcount\tavg_time"
    print "#======================================"
    for key,value in result_dict.iteritems():
        count = value.get('count')
        time = value.get('time')
        avg = time/count
        print "%s\t%d\t%f" %(key,count,avg)
    print "#======================================"
    print "#nomal request"
    print "#======================================"
    print "us_count: %s\ttotal_time: %s" %(useful_req["us"]["count"],useful_req["us"]["time"])
    print "ms_count: %s\ttotal_time: %s" %(useful_req["ms"]["count"],useful_req["ms"]["time"])
    print "s_count: %s\ttotal_time: %s" %(useful_req["s"]["count"],useful_req["s"]["time"])
