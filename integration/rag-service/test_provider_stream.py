import json
import unittest
from unittest.mock import Mock, patch
import requests
import runtime


class ProviderStreamTests(unittest.TestCase):
    def response(self, events):
        response = Mock(headers={'Content-Type': 'text/event-stream'})
        response.iter_lines.return_value = iter([b'data: ' + (json.dumps(e, ensure_ascii=False).encode() if isinstance(e, dict) else e) for e in events])
        return response

    def delta(self, text='', finish=None):
        return {'choices': [{'index': 0, 'delta': {'content': text}, 'finish_reason': finish}]}

    def test_accumulates_unicode_and_usage_without_exposing_partial_text(self):
        response = self.response([self.delta('Según la fuente: '), self.delta('Gestión [ID::P01C01]'), self.delta(finish='stop'), {'choices': [], 'usage': {'prompt_tokens': 23, 'completion_tokens': 12}}, b'[DONE]'])
        with patch.object(runtime.logging.getLogger('gunicorn.error'), 'info') as log:
            metadata, body = runtime.provider_metadata(response, runtime.time.monotonic() + 50)
        self.assertEqual(json.loads(body), metadata)
        self.assertEqual(metadata['choices'][0]['message']['content'], 'Según la fuente: Gestión [ID::P01C01]')
        self.assertEqual(metadata['choices'][0]['finish_reason'], 'stop')
        self.assertEqual(metadata['usage']['completion_tokens'], 12)
        self.assertNotIn('Gestión', repr(log.call_args_list))
        response.close.assert_called_once()

    def test_incomplete_stream_is_not_accepted_as_a_completed_answer(self):
        for events in [[self.delta('Partial')], [self.delta('Partial'), b'[DONE]']]:
            response = self.response(events)
            with self.assertRaises(requests.ConnectionError):
                runtime.provider_metadata(response, runtime.time.monotonic() + 50)
            response.close.assert_called_once()

    def test_truncation_marker_is_preserved_for_existing_validator(self):
        response = self.response([self.delta('Partial', 'length'), b'[DONE]'])
        metadata, _ = runtime.provider_metadata(response, runtime.time.monotonic() + 50)
        self.assertEqual(metadata['choices'][0]['finish_reason'], 'length')
        self.assertEqual(runtime.validate_answer('Partial', [], 'length')[2], 'response_truncated')

    def test_continuous_tokens_cannot_bypass_overall_deadline(self):
        response = self.response([self.delta('Partial')])
        with patch.object(runtime.time, 'monotonic', side_effect=[0, 51]):
            with self.assertRaises(requests.Timeout):
                runtime.provider_metadata(response, 50)
        response.close.assert_called_once()

    def test_error_event_and_malformed_payload_never_publish_text(self):
        for event, error in [({'error': {'message': 'PRIVATE'}}, requests.ConnectionError), (b'{bad', ValueError)]:
            response = self.response([self.delta('Partial'), event])
            with self.assertRaises(error):
                runtime.provider_metadata(response, runtime.time.monotonic() + 50)
            response.close.assert_called_once()
