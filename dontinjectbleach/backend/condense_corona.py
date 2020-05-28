from requests import get
from bs4 import BeautifulSoup as BS
from datetime import timedelta, datetime
import csv, json

def condense_corona():
    total = {}
    for i in range(1, 1000):
        try:
            today = datetime.utcnow().date()
            yesterday = str(today - timedelta(days=i)).split("-")
            yesterday = "-".join([yesterday[1],yesterday[2],yesterday[0]])

            this_day = {}
            with open("dontinjectbleach/corona-data/data" + yesterday + ".csv", "r") as fin:
                l = fin.readline()
                for row in fin.read().split("\n")[:-2]:
                    try:
                        temp = {}
                        r = []
                        i = 0
                        for j in range(len(row)):
                            if j == len(row)-1:
                                r.append(row[i:j+1])
                            elif row[j] == "," and row[j+1] != " ":
                                r.append(row[i:j])
                                i = j+1
                        temp["dead"], temp["confirmed"] = r[-4], r[-5]
                        if r[-1][0] == "\"":
                            z = r[-1][1:-1]
                        else:
                            z = r[-1]
                        for i in range(len(z.split(", "))):
                            if ", ".join(z.split(", ")[i:]) not in this_day.keys():
                                this_day[", ".join(z.split(", ")[i:])] = temp
                            else:
                                prev = this_day[", ".join(z.split(", ")[i:])]
                                a = False
                                try:
                                    new = {}
                                    new["dead"] = str(int(temp["dead"]) + int(prev["dead"]))
                                    new["confirmed"] = str(int(temp["confirmed"]) + int(prev["confirmed"]))
                                except:
                                    a = True
                                if not a:
                                    this_day[", ".join(z.split(", ")[i:])] = new
                                    
                    except:
                        pass
            for k,v in this_day.items():
                if k not in total.keys():
                    total[k] = v
                    total[k]["times"] = yesterday
                    for k2, v2 in total[k].items():
                        total[k][k2] = [v2]
                else:
                    total[k]["times"].append(yesterday)
                    for k1, v1 in v.items():     
                        total[k][k1].append(v1)
        except:
            break
                    

    with open("dontinjectbleach/corona-data/json_corona.json", "w+") as fin:
        fin.write(json.dumps(total, indent=3))

    # with open("dontinjectbleach/corona-data/corona_condensed1.txt", "w+") as fin:
    #     fin.write(str(total)[:10000000])
    # with open("dontinjectbleach/corona-data/corona_condensed2.txt", "w+") as fin:
    #     fin.write(str(total)[10000000:])
        
        
