import unittest
import json
import os
from unittest.mock import patch, Mock
import runtime
from answer_policy import resolve_source_labels, validate_answer, make_prompt
from public_demo.smoke_test import ROW, reset_state


class SourceLabelsTests(unittest.TestCase):
    def test_resolves_only_explicit_model_references_to_selected_passages(self):
        rows = [ROW, dict(ROW, chunk_id='OTHER::P02C01')]
        self.assertEqual(resolve_source_labels('Dato [F2] [F1]', rows), 'Dato [OTHER::P02C01] ['+ROW['chunk_id']+']')
        self.assertEqual(resolve_source_labels('Dato sin cita', rows), 'Dato sin cita')
        prompt = make_prompt('consulta', rows, 'expanded')
        self.assertIn('"reference": "F1"', prompt)
        self.assertNotIn(ROW['chunk_id'], prompt)

    def test_unknown_or_mixed_labels_are_never_silently_dropped(self):
        for answer in ['Dato [F99]', 'Dato [F1] y otro [F99]', 'Dato [F1] y otro [F1, F99]', 'Dato [F1] y otro [f99]']:
            expanded = resolve_source_labels(answer, [ROW])
            self.assertEqual(validate_answer(expanded, [ROW])[2], 'citation_validation_failed')
        self.assertEqual(validate_answer(resolve_source_labels('Dato [F1]', [ROW]), [ROW])[2], 'answered')

    def test_retry_uses_the_same_validator_as_final_result(self):
        reset_state()
        with runtime.app.test_request_context(), patch.object(runtime, 'original_chat', side_effect=['Dato [F1] y otro [UNKNOWN::P01C01]', 'Dato [F1]']) as model:
            runtime.g.glf_context_rows = [ROW]
            runtime.g.glf_allowed_ids = {ROW['chunk_id']}
            runtime.g.glf_policy_active = True
            answer = runtime.diagnostic_chat('question')
            self.assertEqual(model.call_count, 2)
            self.assertEqual(validate_answer(answer, [ROW])[2], 'answered')
            self.assertIn('[F1]', model.call_args.args[0])

    def test_retries_malformed_reference_even_when_one_valid_id_exists(self):
        reset_state()
        with runtime.app.test_request_context(), patch.object(runtime, 'original_chat', side_effect=['Dato [F1] otro [BAD::P1C1]', 'Dato [F1]']) as model:
            runtime.g.glf_context_rows = [ROW]
            runtime.g.glf_allowed_ids = {ROW['chunk_id']}
            runtime.g.glf_policy_active = True
            answer = runtime.diagnostic_chat('question')
            self.assertEqual(model.call_count, 2)
            self.assertEqual(validate_answer(answer, [ROW])[2], 'answered')

    def test_unknown_reference_stays_blocked_after_failed_retry(self):
        with runtime.app.test_request_context(), patch.object(runtime, 'original_chat', return_value='Dato [F99]') as model:
            runtime.g.glf_context_rows = [ROW]
            runtime.g.glf_allowed_ids = {ROW['chunk_id']}
            runtime.g.glf_policy_active = True
            answer = runtime.diagnostic_chat('question')
            self.assertEqual(model.call_count, 2)
            self.assertEqual(validate_answer(answer, [ROW])[2], 'citation_validation_failed')

    def test_stream_returns_original_identifiers_and_bounded_expanded_mode(self):
        reset_state()
        runtime.upstream._generate_answer = runtime.grounded_answer
        structured = json.dumps({'abstain': False, 'paragraphs': [{'text': 'Dato correctamente respaldado.', 'references': ['F1']}], 'missing': ''})
        payload = {'choices': [{'finish_reason': 'stop', 'message': {'content': structured}}], 'usage': {'prompt_tokens': 100, 'completion_tokens': 20}}
        provider = Mock(status_code=200, ok=True, content=json.dumps(payload).encode())
        provider.json.return_value = payload
        with patch.dict(os.environ, {'HF_TOKEN': 'synthetic'}), patch.object(runtime.requests, 'post', return_value=provider):
            response = runtime.app.test_client().post('/api/ask-stream', json={'query': 'riesgos ambientales', 'answer_mode': 'expanded'}, headers={'X-Demo-Key': 'smoke-secret'})
            events = [json.loads(line) for line in response.get_data(as_text=True).splitlines()]
        data = events[-1]['result']
        self.assertTrue(data['generated'])
        self.assertIn('['+ROW['chunk_id']+']', data['answer'])
        self.assertNotIn('[F1]', data['answer'])
        self.assertEqual(data['sources'][0]['chunk_id'], ROW['chunk_id'])
        self.assertEqual(data['diagnostics']['max_output_tokens'], 1000)
        self.assertEqual(data['diagnostics']['policy_version'], 'glf-grounded-v3.1')
