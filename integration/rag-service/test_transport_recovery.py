import unittest
from unittest.mock import Mock, patch
from urllib.request import Request
from urllib.error import URLError
import runtime


class TransportRecovery(unittest.TestCase):
    def request(self):
        return Request('https://router.huggingface.co/v1/chat/completions', data=b'{}')

    def good(self):
        result = Mock(status_code=200, ok=True, content=b'{}')
        result.json.return_value = {}
        return result

    def test_transient_connection_recovers_without_leaking_exception(self):
        with runtime.app.test_request_context(), patch.object(runtime.requests, 'post', side_effect=[runtime.requests.ConnectionError('PRIVATE'), self.good()]) as post, patch.object(runtime.logging.getLogger('gunicorn.error'), 'warning') as log:
            runtime.g.glf_mode = 'brief'
            runtime.g.glf_generation_deadline = runtime.time.monotonic() + 50
            self.assertEqual(runtime.provider_urlopen(self.request(), timeout=35).read(), b'{}')
            self.assertEqual(post.call_count, 2)
            self.assertEqual(runtime.g.glf_provider_attempts, 2)
            self.assertGreater(post.call_args_list[0].kwargs['timeout'], 14)
            self.assertNotIn('PRIVATE', repr(log.call_args_list))

    def test_timeout_near_deadline_never_starts_another_generation(self):
        with runtime.app.test_request_context(), patch.object(runtime.requests, 'post', side_effect=runtime.requests.Timeout('PRIVATE')) as post, patch.object(runtime.time, 'monotonic', side_effect=[0, 0, 0, 45]):
            runtime.g.glf_mode = 'brief'
            runtime.g.glf_generation_deadline = 50
            with self.assertRaises(URLError):
                runtime.provider_urlopen(self.request(), timeout=35)
            self.assertEqual(post.call_count, 1)

    def test_transport_retry_respects_global_attempt_count(self):
        with runtime.app.test_request_context(), patch.object(runtime.requests, 'post', side_effect=runtime.requests.ConnectionError()) as post:
            runtime.g.glf_mode = 'brief'
            runtime.g.glf_provider_attempts = 1
            runtime.g.glf_generation_deadline = runtime.time.monotonic() + 50
            with self.assertRaises(URLError):
                runtime.provider_urlopen(self.request(), timeout=35)
            self.assertEqual(post.call_count, 1)


if __name__ == '__main__':
    unittest.main()


