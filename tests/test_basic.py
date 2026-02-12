import json
import re
from bulletly import assess_bullet


def test_assess_and_suggest_for_general_bullet():
    res = assess_bullet("Implemented robust data validation pipeline", dry_run=True)
    # This is considered incomplete (missing measurable outcome), so we expect suggestions
    assert res.verdict == "needs_improvement"
    assert len(res.suggestions) >= 1


def test_needs_improvement_and_no_invented_numbers():
    res = assess_bullet("Improved ETL reliability by standardizing schemas", dry_run=True)
    assert res.verdict == "needs_improvement"
    # ensure no numbers were invented
    for s in res.suggestions:
        assert not re.search(r"\d", s), "No digits should be present when original had none"


def test_json_output_valid():
    res = assess_bullet("Built API for ingestion", dry_run=True)
    j = json.dumps(res.to_dict())
    obj = json.loads(j)
    assert obj["original"], "original must exist"
    assert isinstance(obj["suggestions"], list)
