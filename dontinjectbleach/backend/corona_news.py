from requests import get
from bs4 import BeautifulSoup as BS
from datetime import datetime
import csv


def updateCoronaNews():
    def match(a, b):
        a,b = a.split(" "), b.split(" ")
        temp = 0
        for i in range(min(len(a), len(b))):
            if a[i] == b[i]:
                temp += 1
        if temp/max(len(a), len(b)) > 0.8:
            return True
    
    with open("dontinjectbleach/corona-data/day.txt", "r") as fin:
        prev=fin.read().split("\n")
        prev, other = prev[0], prev[1].split(" ")

    now = str(datetime.today()).split(".")[0].split(" ")

    if other[0] != now[0] or int(other[1].split(":")[0]) != int(now[1].split(":")[0]):
        with open("dontinjectbleach/corona-data/day.txt", "w") as fout:
            fout.write(prev + "\n" + " ".join(now))
        URL = "https://visualizenow.org/corona-news"
        r = get(URL)
        bs = BS(r.content, "html.parser")
        a = []
        for i in bs.find_all("div", attrs={"class": "col-md-4"})[1:]:
            temp = {}
            cnt = 0
            for j in i.findChildren(href=True):
                if cnt == 0:
                    temp['href'], temp['headline'] = j['href'], j.get_text().strip()
                    cnt += 1
                elif cnt == 1:
                    temp['source-href'], temp['source'] = j['href'], j.get_text().strip()
                    break
            
            temp["details"], temp["publish-date"] = [o.replace("...", "").strip() for o in i.get_text().split("\n") if o.replace("...", "").strip() !=
                                                    "" and o.strip() != "View details"][-1], [o.replace("...", "").strip() for o in i.get_text().split("\n") if o.replace("...", "").strip() !=
                                                                                            "" and o.strip() != "View details"][-2]
            if temp["publish-date"][-1] != "." and temp["publish-date"][-1] != "!" and temp["publish-date"][-1] != ")" and temp["publish-date"][-1] != "?":
                temp["publish-date"] = temp["publish-date"] + "..."
            if not any(match(temp['headline'], i['headline']) for i in a):
                a.append(temp)

        with open("dontinjectbleach/corona-data/news.csv", "w+") as fout:
            writer = csv.writer(fout)
            l = ['href', 'headline', 'source-href', 'source', 'details', 'publish-date']
            writer.writerow(l)
            for i in a:
                temp = []
                for j in l:
                    temp.append(i[j])
                writer.writerow(temp)
            fout.close()