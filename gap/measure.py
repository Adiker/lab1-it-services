# ai-generated: 100% - Codex measured a real Toxiproxy run with the course oha and histogram increment calculation.
"""Run in the itsmlab 0.8.0 image on the lab1-svcdesk_default network.

Docker mounts the repository at /work; run `python /work/gap/measure.py`.
"""
import json
from pathlib import Path
from urllib.request import Request, urlopen

from itsmlab import expfmt, instruments
from itsmlab.labs.lab3 import histo

ROOT = Path(__file__).resolve().parent.parent
TOXIC = {'type': 'latency', 'latency': 100, 'jitter': 10}


def post(path, data):
    with urlopen(Request('http://toxiproxy:8474'+path, data=json.dumps(data).encode(),
                         headers={'Content-Type':'application/json'}, method='POST')) as response:
        return json.load(response)


# Delete only this script's named proxy if rerunning.
try:
    urlopen(Request('http://toxiproxy:8474/proxies/svcdesk', method='DELETE')).close()
except Exception as exc:
    if getattr(exc, 'code', None) != 404:
        raise
post('/proxies', {'name':'svcdesk','listen':'0.0.0.0:8666','upstream':'svcdesk:8080','enabled':True})
post('/proxies/svcdesk/toxics', {'type':'latency','stream':'downstream','toxicity':1,
                               'attributes':{'latency':100,'jitter':10}})
url='http://toxiproxy:8666/kb/search?q=itsmlab'
instruments.oha(url, 5, 40, 64)

def scrape():
    with urlopen('http://svcdesk:8080/metrics') as response:
        return expfmt.parse(response.read().decode())

before = scrape()
result = instruments.oha(url, 60, 40, 64)
after = scrape()
client = result['latencyPercentiles']['p99']
server = histo.quantile_of(histo.delta(histo.route_histogram(before), histo.route_histogram(after)))
output = {'toxic':TOXIC, 'client_p99_seconds':client, 'server_p99_seconds':server,
          'gap_seconds':client-server}
(ROOT/'gap.json').write_text(json.dumps(output,indent=2)+'\n')
(ROOT/'gap'/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(output,indent=2))
