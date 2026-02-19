import csv

from icmplib import ping


domains_to_ping = ["lamoda.ru", "dns-shop.ru", "habr.com",
                   "kinopoisk.ru", "eldorado.ru", "labirint.ru",
                   "ok.ru", "kaggle.com", "google.com", "rt.ru"]

results = [["domain", "min_rtt(ms)", "rtt(ms)", "max_rtt(ms)", "packets_lost"]]

for domain in domains_to_ping:
    host = ping(domain, count=3)
    results.append([domain, round(host.min_rtt, 1), round(host.avg_rtt, 1), round(host.max_rtt, 1), int(host.packet_loss)])

with open('results.csv','w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(results[:])
