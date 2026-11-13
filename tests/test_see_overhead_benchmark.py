from scripts.benchmark_see_overhead import run_benchmark


def test_see_overhead_benchmark_reports_both_modes_and_scope():
    report = run_benchmark(repeats=3, warmups=0)

    assert report["benchmark"] == "SEE-guided MCTS root expansion CPU overhead"
    assert report["aggregate"]["paired_samples"] == 3 * len(report["positions"])
    assert report["aggregate"]["see_disabled_median_ms"] >= 0
    assert report["aggregate"]["see_enabled_median_ms"] >= 0
    assert "not end-to-end search speed" in report["interpretation_limit"]
    assert all(position["legal_moves"] > 0 for position in report["positions"])
    assert all(position["capture_or_promotion_candidates"] >= 0 for position in report["positions"])
