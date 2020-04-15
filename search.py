import qbittorrentapi
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

qbt_client = qbittorrentapi.Client(host='', username='', password='')

try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

search = input("search for: ")
limit = input("No. of torrents: ")

search_job = qbt_client.search.start(pattern=search, category='all', plugins='all')

while (search_job.status()[0].status != 'Stopped'):
    time.sleep(.1)

search_result = qbt_client.search_results(id=search_job.id, limit = limit, offset = 1)

for result in search_result.results:
    #print(f"Name: {result.fileName}\nSeeders: {result.nbSeeders}\nSize: {result.fileSize}")
    #print(f"\nMagnet: {result.fileUrl}")
    pp.pprint(result)

search_job.delete()
