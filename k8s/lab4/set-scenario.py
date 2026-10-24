# ai-generated: 100% - Codex wrote an explicit scenario patcher for the two supported flags and alternative resource hypotheses.
"""Read flagd-config JSON on stdin, emit a ConfigMap merge patch; no cluster access."""
import argparse
import json
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('resource', choices=['emailMemoryLeak', 'recommendationCacheFailure'])
a = p.parse_args()
cm = json.load(sys.stdin)
flags = json.loads(cm['data']['demo.flagd.json'])
# Chosen variants are experiment assumptions, not decoded ground truth.
for name in ['paymentFailure', 'loadGeneratorFloodHomepage', 'emailMemoryLeak', 'recommendationCacheFailure']:
    flags['flags'][name]['defaultVariant'] = 'off'
flags['flags']['paymentFailure']['defaultVariant'] = '25%'
flags['flags']['loadGeneratorFloodHomepage']['defaultVariant'] = 'on'
flags['flags'][a.resource]['defaultVariant'] = '100x' if a.resource == 'emailMemoryLeak' else 'on'
json.dump({'data': {'demo.flagd.json': json.dumps(flags)}}, sys.stdout)
