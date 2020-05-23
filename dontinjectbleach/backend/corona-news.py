from requests import get
from bs4 import BeautifulSoup as BS
from datetime import datetime
import csv

with open("../corona-data/day.txt", "r") as fin:
    prev=fin.read().split("\n")
    prev, other = prev[0], prev[1].split(" ")

now = str(datetime.today()).split(".")[0].split(" ")

if other[0] != now[0] or int(other[1].split(":")[0]) != int(now[1].split(":")[0]):
    with open("../corona-data/day.txt", "w") as fout:
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
        a.append(temp)

    with open("../corona-data/news.csv", "w+") as fout:
        writer = csv.writer(fout)
        l = ['href', 'headline', 'source-href', 'source', 'details', 'publish-date']
        writer.writerow(l)
        for i in a:
            temp = []
            for j in l:
                temp.append(i[j])
            writer.writerow(temp)
        fout.close()