import json
import re
import unittest
from answer_policy import answer_format, render_structured_answer, validate_answer, make_prompt
from public_demo.smoke_test import ROW


class StructuredAnswerTests(unittest.TestCase):
    def valid(self):
        return {'abstain': False, 'paragraphs': [{'text': 'Una condición completa.', 'references': ['F1']}], 'missing': ''}

    def test_renders_complete_claims_with_only_model_selected_sources(self):
        answer = render_structured_answer(json.dumps(self.valid()), [ROW])
        self.assertIn('Una condición completa. ['+ROW['chunk_id']+']', answer)
        self.assertEqual(validate_answer(answer, [ROW])[2], 'answered')

    def test_malformed_or_oversized_json_is_blocked_instead_of_cut(self):
        variants = []
        for change in [{'paragraphs': []}, {'missing': 'x'*241}, {'abstain': 'false'}, {'unexpected': 'x'}]:
            variants.append(dict(self.valid(), **change))
        for paragraph in [{'text': 'x'*701, 'references': ['F1']}, {'text': 'claim', 'references': []}, {'text': 'claim', 'references': ['F99']}]:
            variants.append(dict(self.valid(), paragraphs=[paragraph]))
        variants.append(dict(self.valid(), paragraphs=self.valid()['paragraphs']*6))
        for data in variants:
            self.assertEqual(validate_answer(render_structured_answer(json.dumps(data), [ROW]), [ROW])[2], 'citation_validation_failed')
        for raw in ['{"abstain":', 'unstructured response [F1]', '[]']:
            self.assertEqual(validate_answer(render_structured_answer(raw, [ROW]), [ROW])[2], 'citation_validation_failed')

    def test_schema_bounds_paragraphs_lengths_and_reference_ids(self):
        schema = answer_format([ROW])['json_schema']['schema']
        paragraph = schema['properties']['paragraphs']
        self.assertEqual(paragraph['maxItems'], 4)
        self.assertEqual(paragraph['items']['properties']['text']['maxLength'], 700)
        self.assertEqual(paragraph['items']['properties']['references']['items']['enum'], ['F1'])

    def test_space_before_question_mark_does_not_change_generation_prompt(self):
        self.assertEqual(make_prompt('¿Qué es el PGAS ?', [ROW], 'expanded'), make_prompt('¿Qué es el PGAS?', [ROW], 'expanded'))

    def test_structured_abstention_stays_an_abstention(self):
        data = {'abstain': True, 'paragraphs': [], 'missing': ''}
        self.assertEqual(validate_answer(render_structured_answer(json.dumps(data), [ROW]), [ROW])[2], 'insufficient_context')

    def test_missing_claim_does_not_receive_an_automatic_citation(self):
        data = self.valid()
        data['paragraphs'][0]['references'] = []
        self.assertNotIn(ROW['chunk_id'], render_structured_answer(json.dumps(data), [ROW]))

    def test_unfinished_sentence_is_not_presented_as_a_complete_paragraph(self):
        for text in ['El plan corresponde a las características y', 'El plan corresponde a las características y.']:
            data = self.valid()
            data['paragraphs'][0]['text'] = text
            self.assertEqual(validate_answer(render_structured_answer(json.dumps(data), [ROW]), [ROW])[2], 'citation_validation_failed')

    def test_duplicate_inline_citation_is_removed_only_when_explicitly_selected(self):
        data = self.valid()
        data['paragraphs'][0]['text'] = 'Una condición completa [F1].'
        answer = render_structured_answer(json.dumps(data), [ROW])
        self.assertEqual(answer.count(ROW['chunk_id']), 1)
        data['paragraphs'][0]['text'] = 'Una condición [F99].'
        self.assertEqual(validate_answer(render_structured_answer(json.dumps(data), [ROW]), [ROW])[2], 'citation_validation_failed')

    def test_schema_accepts_normal_prose_and_rejects_punctuation_only(self):
        text_schema = answer_format([ROW])['json_schema']['schema']['properties']['paragraphs']['items']['properties']['text']
        self.assertEqual(text_schema['minLength'], 20)
        for text in ['.', '........................', 'Sí.']:
            data = self.valid()
            data['paragraphs'][0]['text'] = text
            self.assertEqual(validate_answer(render_structured_answer(json.dumps(data), [ROW]), [ROW])[2], 'citation_validation_failed')

    def test_continued_sentence_keeps_every_word_and_model_selected_reference(self):
        data = self.valid()
        data['paragraphs'] = [{'text': 'El plan conserva las características y', 'references': ['F1']}, {'text': 'los riesgos específicos del proyecto.', 'references': ['F1']}]
        rendered = render_structured_answer(json.dumps(data), [ROW])
        self.assertIn('El plan conserva las características y los riesgos específicos del proyecto.', rendered)
        self.assertEqual(rendered.count(ROW['chunk_id']), 1)
        self.assertEqual(validate_answer(rendered, [ROW])[2], 'answered')
