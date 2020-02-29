import taqu.aio.worker as worker


def test_something():
    assert worker.POLL_INTERVAL == 0.125
