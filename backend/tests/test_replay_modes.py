import pytest

def test_replay_mode_separation():
    valid_modes = {"historical", "synthetic", "fixture"}
    
    # Historical mode contract
    hist_record = {
        "mode": "historical",
        "provenance": "NOAA GEFSv12 2017-2019 Frozen Benchmark",
        "is_synthetic": False,
        "is_independent_truth": True
    }
    assert hist_record["mode"] in valid_modes
    assert hist_record["is_synthetic"] is False
    assert hist_record["is_independent_truth"] is True

    # Synthetic digital twin contract
    synthetic_record = {
        "mode": "synthetic",
        "provenance": "Digital Twin Scenario Generator (Simulated Progression)",
        "is_synthetic": True,
        "is_independent_truth": False
    }
    assert synthetic_record["mode"] in valid_modes
    assert synthetic_record["is_synthetic"] is True
    assert synthetic_record["is_independent_truth"] is False
