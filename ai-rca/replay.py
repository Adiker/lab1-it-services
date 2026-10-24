# ai-generated: 100% - Codex wrote a standard-library replay of the two scored ledgers against the served snapshot.
"""Replay all predictions at incident time and exactly five minutes before onset."""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BASELINE = (datetime.fromisoformat('2026-10-12T06:36:23+00:00') - timedelta(minutes=5)).isoformat()


def query(base, expr, at):
    with urlopen(base.rstrip('/') + '/api/v1/query?' + urlencode({'query': expr, 'time': at}), timeout=30) as response:
        body = json.load(response)
    if body.get('status') != 'success':
        raise RuntimeError(body)
    return body['data']['result']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:19090')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    results = {}
    count = 0
    for filename in ['ai-rca-eval.json', 'ai-rca-eval-2.json']:
        ledger = json.loads((ROOT / filename).read_text())
        results[filename] = {}
        for h in ledger['hypotheses']:
            if h['verdict'] == 'unfalsifiable':
                assert h['predicts'] is None and h['at'] is None and h['result'] is None
                continue
            incident = query(args.url, h['predicts'], h['at'])
            baseline = query(args.url, h['predicts'], BASELINE)
            if bool(incident) != h['result']:
                raise RuntimeError(f"{filename} {h['id']}: declared result differs from replay")
            if h['verdict'] in {'correct', 'partially_correct'} and (not incident or baseline):
                raise RuntimeError(f"{filename} {h['id']}: prediction must hold only in the fault")
            if h['verdict'] == 'hallucinated' and incident:
                raise RuntimeError(f"{filename} {h['id']}: hallucinated prediction must be contradicted")
            results[filename][h['id']] = {'at': h['at'], 'incident': incident, 'baseline_at': BASELINE, 'baseline': baseline}
            count += 1
    if args.out:
        args.out.write_text(json.dumps(results, indent=2) + '\n')
    print(f'Lab 4 ledger replay: {count} predictions passed')


if __name__ == '__main__':
    main()
