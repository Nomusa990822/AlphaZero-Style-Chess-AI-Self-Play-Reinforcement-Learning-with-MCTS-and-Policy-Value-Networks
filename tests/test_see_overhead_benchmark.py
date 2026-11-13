from scripts.benchmark_see_overhead import run_benchmark


def test_see_overhead_benchmark_reports_both_modes_and_scope():
    report = run_benchmark(repeats=3, warmups=0, batch_size=2)

    assert report["benchmark"] == "SEE-guided MCTS root expansion CPU overhead"
    assert report["aggregate"]["paired_batches_per_position"] == 3
    assert report["aggregate"]["total_expansions_per_mode"] == 3 * 2 * len(report["positions"])
    assert report["aggregate"]["see_disabled_median_ms_per_expansion"] >= 0
    assert report["aggregate"]["see_enabled_median_ms_per_expansion"] >= 0
    assert "Batched microbenchmark only" in report["interpretation_limit"]
    assert all(position["batch_size_expansions"] == 2 for position in report["positions"])
    assert all(position["timed_batches_per_mode"] == 3 for position in report["positions"])
    assert all(position["legal_moves"] > 0 for position in report["positions"])
    assert all(position["capture_or_promotion_candidates"] >= 0 for position in report["positions"])
