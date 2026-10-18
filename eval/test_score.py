import unittest
from score import evaluate, score_case
from normalize_native import operation_succeeded


class ScorerTests(unittest.TestCase):
    def test_unknown_write_outcome_is_incomplete(self):
        case = {"id":"a", "expected_calls":[{"name":"write", "succeeded":True}]}
        trace = {"tool_trace_complete":True,"calls":[{"name":"write","succeeded":None}]}
        self.assertEqual(score_case(case, trace)["status"], "incomplete")

    def test_completed_transport_without_commit_receipt_is_unknown(self):
        self.assertIsNone(operation_succeeded({'tool':'confirm_terms_update','status':'completed','result':{'content':[{'type':'text','text':'That preview has expired.'}]}}))

    def test_structured_commit_receipt_is_success(self):
        self.assertTrue(operation_succeeded({'tool':'confirm_terms_update','status':'completed','result':{'structured_content':{'saved':['usage']}}}))

    def test_independent_reads_need_not_be_ordered(self):
        case = {"id": "a", "ordered_calls": False, "expected_calls": [{"name": "profile"}, {"name": "terms"}]}
        trace = {"tool_trace_complete": True, "calls": [{"name": "terms"}, {"name": "profile"}]}
        self.assertEqual(score_case(case, trace)["status"], "pass")

    def test_failed_call_is_not_successful_execution(self):
        case = {"id": "a", "expected_calls": [{"name": "write", "succeeded": True}]}
        trace = {"tool_trace_complete": True, "calls": [{"name": "write", "arguments": {}, "succeeded": False}]}
        self.assertEqual(score_case(case, trace)["status"], "fail")

    def test_partial_arguments_are_unknown(self):
        case = {"id": "a", "expected_calls": [{"name": "write", "arguments": {"status": "interested"}}]}
        trace = {"tool_trace_complete": True, "calls": [{"name": "write", "arguments": {}, "arguments_complete": False}]}
        self.assertEqual(score_case(case, trace)["status"], "incomplete")

    def test_partial_arguments_cannot_prove_no_forbidden_call(self):
        case = {"id": "a", "forbidden_calls": [{"name": "write", "arguments": {"status": "agreed"}}]}
        trace = {"tool_trace_complete": True, "calls": [{"name": "write", "arguments": {}, "arguments_complete": False}]}
        self.assertEqual(score_case(case, trace)["status"], "incomplete")

    def test_excerpt_cannot_prove_no_leak(self):
        case = {"id": "a", "forbidden_output_literals": ["secret"]}
        trace = {"final_text": "safe excerpt", "final_text_is_excerpt": True}
        self.assertEqual(score_case(case, trace)["status"], "incomplete")

    def test_missing_trace_not_a_pass(self):
        self.assertEqual(score_case({"id": "a"}, None)["status"], "not_run")

    def test_hidden_calls_unknown(self):
        case = {"id": "a", "expected_calls": [{"name": "read"}]}
        self.assertEqual(score_case(case, {"calls": []})["status"], "incomplete")

    def test_wrong_arguments_fail(self):
        case = {"id": "a", "expected_calls": [{"name": "write", "arguments": {"status": "interested"}}]}
        trace = {"tool_trace_complete": True, "calls": [{"name": "write", "arguments": {"status": "agreed"}}]}
        self.assertEqual(score_case(case, trace)["status"], "fail")

    def test_order_enforced(self):
        case = {"id": "a", "expected_calls": [{"name": "preview"}, {"name": "commit"}]}
        trace = {"tool_trace_complete": True, "calls": [{"name": "commit"}, {"name": "preview"}]}
        self.assertEqual(score_case(case, trace)["status"], "fail")

    def test_missing_state_not_inferred_from_text(self):
        case = {"id": "a", "expected_state": {"saved": True}}
        self.assertEqual(score_case(case, {"final_text": "Saved successfully"})["status"], "incomplete")

    def test_forbidden_call_fails_even_when_trace_partial(self):
        case = {"id": "a", "forbidden_tools": ["delete"]}
        self.assertEqual(score_case(case, {"calls": [{"name": "delete"}]})["status"], "fail")

    def test_type_strict_boolean_is_not_one(self):
        case = {"id": "a", "expected_state": {"confirmed": True}}
        self.assertEqual(score_case(case, {"persisted_state": {"confirmed": 1}})["status"], "fail")

    def test_duplicate_transcripts_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([{"id": "a"}], {"turns": [{"case_id": "a"}, {"case_id": "a"}]})

    def test_unrun_cases_dont_inflate_pass_rate(self):
        report = evaluate([{"id": "a"}, {"id": "b"}], {"turns": []})
        self.assertIsNone(report["summary"]["pass_rate_on_fully_scored"])
        self.assertEqual(report["summary"]["execution_coverage"], 0)


if __name__ == "__main__":
    unittest.main()
