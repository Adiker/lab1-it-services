# ai-generated: 100% - Codex implemented the published matching rules and verified the practice set.
"""Compute per-detector defect-level matrices from SARIF and course labels."""
import argparse
import json
import re
import sys
from urllib.parse import unquote

CWES = {
    'secret': [259, 260, 321, 798],
    'injection': [74, 77, 78, 79, 80, 88, 89, 90, 91, 94, 95, 96, 611, 776, 917, 943, 1336],
    'deserialization': [502],
    'weak-crypto': [261, 326, 327, 328, 330, 331, 338, 759, 760, 916],
    'insecure-transport': [295, 297, 319, 322, 757],
    'path-traversal': [22, 23, 35, 36, 73],
    'ssrf': [918],
    'vulnerable-dependency': [937, 1035, 1104, 1395],
    'misconfiguration': [16, 215, 250, 489, 668, 732, 1188],
    'access-control': [284, 285, 639, 862, 863],
}


def obj(value):
    return value if isinstance(value, dict) else {}


def array(value):
    return value if isinstance(value, list) else []


def tool_id(driver):
    name = driver.get('name')
    name = name.strip().lower() if isinstance(name, str) else ''
    if name in {'semgrep', 'semgrep oss', 'semgrep ce', 'semgrep community edition', 'semgrep pro'}:
        return 'semgrep'
    return re.sub(r'[^a-z0-9]+', '-', name).strip('-') or 'unknown'


def tags(value):
    return [t for t in array(obj(obj(value).get('properties')).get('tags')) if isinstance(t, str)]


def classes(result, rule, tool):
    explicit = obj(result.get('properties')).get('class')
    if isinstance(explicit, str) and explicit in CWES:
        return {explicit}
    if tool == 'gitleaks':
        return {'secret'}
    if tool in {'grype', 'osv-scanner'}:
        return {'vulnerable-dependency'}
    if tool == 'trivy':
        mapping = {'vulnerability': 'vulnerable-dependency', 'secret': 'secret', 'misconfiguration': 'misconfiguration'}
        found = {mapping[t.lower()] for t in tags(rule) if t.lower() in mapping}
        if found:
            return found
    numbers = {int(n) for t in tags(result) + tags(rule) for n in re.findall(r'(?<![a-zA-Z0-9])CWE-([0-9]+)', t, re.I)}
    return {kind for kind, codes in CWES.items() if numbers.intersection(codes)} or {'other'}


def normalized_package(name):
    return re.sub(r'[-_.]+', '-', name.lower())


def confusion_matrix(labels, sarif_documents):
    root, defects = labels['set'], labels['defects']
    findings = {}
    for document in sarif_documents:
        for run in array(obj(document).get('runs')):
            if not isinstance(run, dict):
                continue
            driver = obj(obj(run.get('tool')).get('driver'))
            tool = tool_id(driver)
            found, false = findings.setdefault(tool, (set(), set()))
            rules = array(driver.get('rules'))
            for result in array(run.get('results')):
                if not isinstance(result, dict) or result.get('kind') not in (None, 'fail') or result.get('suppressions'):
                    continue
                locations = array(result.get('locations'))
                physical = obj(obj(locations[0]).get('physicalLocation')) if locations else {}
                uri = obj(physical.get('artifactLocation')).get('uri')
                if not isinstance(uri, str) or not uri:
                    continue
                path = re.sub(r'^file://', '', unquote(uri), flags=re.I)
                if path.startswith('./'):
                    path = path[2:]
                parts = path.split('/')
                if root not in parts:
                    continue
                file = '/'.join(parts[len(parts) - 1 - parts[::-1].index(root):])
                region = obj(physical.get('region'))
                start = region.get('startLine')
                start = start if type(start) is int and start >= 1 else None
                end = region.get('endLine')
                end = max(start, end) if start is not None and type(end) is int else start
                rule_id = result.get('ruleId')
                rule_id = rule_id if isinstance(rule_id, str) else None
                rule = next((r for r in rules if isinstance(r, dict) and rule_id is not None and r.get('id') == rule_id), {})
                kinds = classes(result, rule, tool)
                message = obj(result.get('message')).get('text')
                tokens = {normalized_package(t.strip('._-')) for t in re.findall(r'[A-Za-z0-9._-]+', message if isinstance(message, str) else '')}
                matched = set()
                for i, defect in enumerate(defects):
                    kind = defect['class']
                    if defect['file'] != file or kind not in kinds:
                        continue
                    if kind == 'vulnerable-dependency':
                        match = normalized_package(defect['package']) in tokens
                    else:
                        match = start is not None and start <= defect['end_line'] and defect['start_line'] <= end
                    if match:
                        matched.add(i)
                if matched:
                    found.update(matched)
                else:
                    false.add((rule_id, file, start, end))
    output = {}
    for tool, (found, false) in findings.items():
        tp, fp, fn = len(found), len(false), len(defects) - len(found)
        ratio = lambda n, d: round(n / d, 4) if d else None
        output[tool] = {'tp': tp, 'fp': fp, 'fn': fn, 'precision': ratio(tp, tp + fp),
                        'recall': ratio(tp, tp + fn), 'f1': ratio(2 * tp, 2 * tp + fp + fn)}
    return {'set': root, 'defects': len(defects), 'tools': output}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--labels', required=True)
    parser.add_argument('sarif', nargs='+')
    args = parser.parse_args()
    with open(args.labels, encoding='utf-8') as f:
        labels = json.load(f)
    documents = []
    for path in args.sarif:
        with open(path, encoding='utf-8') as f:
            documents.append(json.load(f))
    json.dump(confusion_matrix(labels, documents), sys.stdout, indent=2)
    print()


if __name__ == '__main__':
    main()
