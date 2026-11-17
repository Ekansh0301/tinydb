from autose import gates

GOOD_SPEC = """# Spec
## Source statements
S1: "x"
## Requirements
- FR-1 [STATED] The system shall return at most limit documents. (S1)
## Acceptance criteria
- AC-1 (FR-1): Given 5 matching documents, when search is called with limit=2, then the list has length 2.
## Assumptions and open questions
- A-1 [ASSUMED] none. Impact if wrong: low.
## Non-goals
- offset
"""


def test_good_spec_passes():
    ok, why = gates.gate_spec(GOOD_SPEC)
    assert ok, why


def test_spec_without_criteria_or_with_vague_outcome_fails():
    ok, why = gates.gate_spec(GOOD_SPEC.replace("- AC-1", "- note"))
    assert not ok and any("no acceptance criteria" in w for w in why)
    ok, why = gates.gate_spec(GOOD_SPEC.replace("the list has length 2", "it is fast"))
    assert not ok and any("vague" in w for w in why)
    ok, why = gates.gate_spec(GOOD_SPEC.replace("Given 5 matching documents, when", "When"))
    assert not ok and any("Given/When/Then" in w for w in why)


def test_requirement_without_criterion_fails():
    ok, why = gates.gate_spec(GOOD_SPEC.replace("## Acceptance", "- FR-2 [ASSUMED] more\n## Acceptance"))
    assert not ok and any("FR-2" in w for w in why)


DESIGN = """# Design
## Approach
x
## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/a.py | f | change signature to `int | None = None` | AC-1 |
## Risks
- none
"""


def test_design_table_with_pipe_in_a_cell(tmp_path):
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "tinydb" / "a.py").write_text("def f():\n    pass\n")
    ok, why = gates.gate_design(DESIGN, GOOD_SPEC, tmp_path)
    assert ok, why


def test_design_names_must_exist_or_be_new(tmp_path):
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "tinydb" / "a.py").write_text("def g():\n    pass\n")
    ok, why = gates.gate_design(DESIGN, GOOD_SPEC, tmp_path)
    assert not ok and any("`f` not found" in w for w in why)
    ok, why = gates.gate_design(DESIGN.replace("tinydb/a.py", "tinydb/zzz.py"), GOOD_SPEC, tmp_path)
    assert not ok and any("does not exist" in w for w in why)
    ok, why = gates.gate_design(DESIGN.replace("tinydb/a.py", "workflow/x.py"), GOOD_SPEC, tmp_path)
    assert not ok and any("not a file you may change" in w for w in why)


def test_design_must_cover_every_criterion(tmp_path):
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "tinydb" / "a.py").write_text("def f():\n    pass\n")
    spec = GOOD_SPEC.replace("## Assumptions", "- AC-2 (FR-1): Given a, when b, then c.\n## Assumptions")
    ok, why = gates.gate_design(DESIGN, spec, tmp_path)
    assert not ok and any("AC-2" in w for w in why)


REVIEW_OK = {"verdict": "APPROVE", "issue_class": None, "summary": "s",
             "checks": [{"claim": "a", "evidence": "ran tests: 235 passed", "result": "pass"},
                        {"claim": "b", "evidence": "tinydb/table.py:300", "result": "pass"}],
             "findings": []}


def test_review_gate_requires_evidence_and_a_command():
    assert gates.gate_review(REVIEW_OK, True)[0]
    ok, why = gates.gate_review(REVIEW_OK, False)
    assert not ok and any("never ran a command" in w for w in why)
    thin = dict(REVIEW_OK, checks=[{"claim": "a", "evidence": "", "result": "pass"}])
    assert not gates.gate_review(thin, True)[0]


def test_review_gate_rejects_approve_with_serious_findings_and_unclassified_rejections():
    bad = dict(REVIEW_OK, findings=[{"severity": "high", "file": "x", "line": 1, "text": "bug"}])
    assert not gates.gate_review(bad, True)[0]
    rc = dict(REVIEW_OK, verdict="REQUEST_CHANGES", findings=[{"severity": "high", "file": "x", "line": 1, "text": "bug"}])
    assert not gates.gate_review(rc, True)[0]                      # no issue_class
    assert gates.gate_review(dict(rc, issue_class="code"), True)[0]
    assert not gates.gate_review("not json", True)[0]


def test_typographic_hyphens_in_ids_are_accepted(tmp_path):
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "tinydb" / "a.py").write_text("def f():\n    pass\n")
    spec = GOOD_SPEC.replace("AC-1", "AC\u20111").replace("FR-1", "FR\u20111")
    assert gates.gate_spec(spec)[0]
    design = DESIGN.replace("AC-1", "AC\u20111")
    ok, why = gates.gate_design(design, spec, tmp_path)
    assert ok, why


def test_failures_are_split_between_wrong_tests_and_wrong_behaviour():
    out = ("tests/test_autose_a.py:13: TypeError\n"
           "tests/test_autose_a.py:30: AssertionError\n"
           "tinydb/table.py:301: ValueError\n")
    tester, impl, library = gates.classify_failures(out)
    assert tester == ["tests/test_autose_a.py:13 TypeError"]
    assert impl == ["tests/test_autose_a.py:30 AssertionError"]
    assert library == ["tinydb/table.py"]


def test_a_test_file_that_cannot_be_collected_is_the_testers_fault():
    out = "ERROR tests/test_autose_x.py\n!!!! Interrupted: 1 error during collection !!!!\n"
    tester, impl, library = gates.classify_failures(out)
    assert tester == ["tests/test_autose_x.py collection error"] and impl == [] and library == []


def test_a_criterion_may_cover_several_requirements():
    spec = GOOD_SPEC.replace("- FR-1 [STATED] The system shall return at most limit documents. (S1)",
                             "- FR-1 [STATED] The system shall return at most limit documents. (S1)\n- FR-2 [STATED] Order is kept. (S1)")
    spec = spec.replace("- AC-1 (FR-1):", "- AC-1 (FR-1 & FR-2):")
    assert gates.gate_spec(spec)[0], gates.gate_spec(spec)[1]
