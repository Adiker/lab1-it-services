# ai-generated: 100% - Codex wrote upstream fault and exactly-once instrumentation regression tests.
"""Run inside the service image: python -m unittest tests.monitoring_regressions."""
import unittest

import httpx
from fastapi.testclient import TestClient
from svcdesk.main import app
from svcdesk.monitoring import REGISTRY


class MonitoringRegressionTests(unittest.TestCase):
    def setUp(self):
        self.context = TestClient(app)
        self.client = self.context.__enter__()
        self.requests = []
        self.response_status = 200
        self.failure = None

        def upstream(request):
            self.requests.append(request)
            if self.failure:
                raise self.failure
            return httpx.Response(self.response_status, json={"hits": [{"id": "kb-1", "score": 0.75}]})

        self.original = app.state.kb_client
        app.state.kb_client = httpx.AsyncClient(transport=httpx.MockTransport(upstream), timeout=3)

    def tearDown(self):
        # TestClient's portal closes this client on the same event loop as the request.
        self.client.portal.call(app.state.kb_client.aclose)
        app.state.kb_client = self.original
        self.context.__exit__(None, None, None)

    def counts(self):
        return {tuple(sorted(s.labels.items())): s.value for metric in REGISTRY.collect()
                for s in metric.samples if s.name == "http_server_request_duration_seconds_count"}

    def test_encoded_query_hits_unchanged_and_no_cache(self):
        query = 'vpn & + / ? żółć'
        for _ in range(2):
            response = self.client.get('/kb/search', params={'q': query})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'query': query, 'hits': [{'id': 'kb-1', 'score': .75}]})
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(self.requests[0].url.params['q'], query)
        self.assertEqual(self.requests[0].url.path, '/search')

    def test_invalid_queries_never_call_upstream(self):
        for params in ({}, {'q': ''}, {'q': 'x'*201}):
            response = self.client.get('/kb/search', params=params)
            self.assertEqual(response.status_code, 422)
            self.assertIn('error', response.json())
        self.assertEqual(self.requests, [])

    def test_non_200_timeout_and_connection_error_have_no_retry(self):
        for status, failure in ((503, None), (200, httpx.ReadTimeout('timeout')),
                                (200, httpx.ConnectError('connection refused'))):
            with self.subTest(status=status, failure=failure):
                self.response_status, self.failure = status, failure
                before = len(self.requests)
                response = self.client.get('/kb/search', params={'q': 'vpn'})
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json()['error']['code'], 'upstream_unavailable')
                self.assertEqual(len(self.requests)-before, 1)

    def test_once_per_response_and_route_templates(self):
        before = self.counts()
        requests = [('/kb/search?q=vpn', '/kb/search', '200'),
                    ('/kb/search', '/kb/search', '422'),
                    ('/tickets/random-ticket-123', '/tickets/{ticket_id}', '404'),
                    ('/unknown-123', 'unmatched', '404')]
        for path, route, status in requests:
            self.assertEqual(self.client.get(path).status_code, int(status))
            key = tuple(sorted({'http_request_method':'GET','http_route':route,
                                'http_response_status_code':status}.items()))
            self.assertEqual(self.counts()[key]-before.get(key, 0), 1)
        after = self.counts()
        response = self.client.get('/metrics', headers={'Accept':'text/plain;version=0.0.4'})
        self.assertTrue(response.headers['content-type'].startswith('text/plain'))
        self.assertEqual(self.counts(), after)
        self.assertNotIn('random-ticket-123', response.text)
        self.assertNotIn('unknown-123', response.text)
