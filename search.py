import qbittorrentapi
import time
from hurry.filesize import size

pp = pprint.PrettyPrinter(indent=4)

qbt_client = qbittorrentapi.Client(host='192.168.1.248:8080', username='admin', password='adminadmin')

try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

#def search(query):
search_job = qbt_client.search.start(pattern='lucifer', category='all', plugins='all')

while (search_job.status()[0].status != 'Stopped'):
    time.sleep(.1)

search_result = qbt_client.search_results(id=search_job.id, limit = 3, offset = 1)

for result in search_result.results:
    i = result.fileUrl.index('&')
    print(f"Name: {result.fileName}\nMagnet: {result.fileUrl[:i]}\nSeeders: {result.nbSeeders}\nSize: {size(result.fileSize)}")

search_job.delete()
