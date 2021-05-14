import pytest
from hydra.experimental import initialize, compose

from src.agent import Agent


@pytest.fixture(scope="module")
def config_u_0():
    u_duration = 0
    with initialize(config_path="../hyparam"):
        config = compose(config_name="config.yml", overrides=[f"u_duration={u_duration}"])
    return config


@pytest.fixture(scope="module")
def config_w_0():
    w_duration = 0
    with initialize(config_path="../hyparam"):
        config = compose(config_name="config.yml", overrides=[f"w_duration={w_duration}"])
    return config


def test_produciton(config_u_0, config_w_0):
    """
    1. u_duration を 0 にしたときに kaQta と知覚されるかのテスト
    2. u_duration を 0 u に相当する
    """
    src_phoneme = "kawuta"
    u_idx, w_idx = 1, 3
    u_duration, w_duration = 9, 3
    # u_0
    a_u_0 = Agent(config_u_0)
    _, _, state_idxs_u_0 = a_u_0.production(src_phoneme)
    assert u_idx not in state_idxs_u_0
    # このtestはaだと複数あるため成立しない
    assert len(list(filter(lambda e: e == w_idx, state_idxs_u_0))) == w_duration
    # w_0
    a_w_0 = Agent(config_w_0)
    _, _, state_idxs_w_0 = a_w_0.production(src_phoneme)
    assert len(list(filter(lambda e: e == u_idx, state_idxs_w_0))) == u_duration
    assert w_idx not in state_idxs_w_0
