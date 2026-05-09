from tracegraph.evaluation.metrics import compute_metrics, exact_match_score, f1_score, normalize_answer


def test_normalize_answer():
    assert normalize_answer("The, Cat!") == "cat"


def test_exact_match():
    assert exact_match_score("Yes", "yes") == 1.0


def test_f1():
    assert f1_score("retain logs 24 months", "logs retained for 24 months") > 0


def test_compute_metrics():
    m = compute_metrics("a", "b")
    assert set(m.keys()) == {"em", "f1"}
