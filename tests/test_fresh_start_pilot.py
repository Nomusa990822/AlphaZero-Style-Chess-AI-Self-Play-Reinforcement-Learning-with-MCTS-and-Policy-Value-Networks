from fresh_start_pilot import build_pilot_config


def test_fresh_start_pilot_is_bounded_and_explicit():
    move_encoding, encoder, network_config, config = build_pilot_config()

    assert move_encoding.action_size > 0
    assert encoder is not None
    assert network_config.input_channels == 20
    assert network_config.num_filters == 64
    assert config.device == "cpu"
    assert config.iterations == 1
    assert config.self_play_games_per_iteration == 4
    assert config.self_play_max_moves == 80
    assert config.train_mcts_simulations == 8
    assert config.eval_mcts_simulations == 8
    assert config.training_epochs == 1
    assert config.gating_games == 2
    assert config.resume_best_model is True
    assert config.best_model_checkpoint.endswith("fresh_pilot/best_model.pt")
    assert config.latest_candidate_checkpoint.endswith("fresh_pilot/latest_candidate.pt")
