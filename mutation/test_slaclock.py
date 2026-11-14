# ai-generated: 100% - Codex wrote behavioral tests from the supplied specification.
from datetime import datetime, timedelta
import pytest
import slaclock as s


def test_priorities():
    expected = [['P1', 'P2', 'P3'], ['P2', 'P3', 'P4'], ['P3', 'P4', 'P4']]
    for i in range(1, 4):
        for j in range(1, 4):
            assert s.priority_of(i, j) == expected[i-1][j-1]
            assert s.priority_of(i, j, True) == min(expected[i-1][j-1], 'P2')
    for bad in (0, 4, True, 2.0, '1'):
        with pytest.raises(ValueError): s.priority_of(bad, 1)
        with pytest.raises(ValueError): s.priority_of(1, bad)


def test_targets_and_states():
    for p, value in [('P1', (15, 240)), ('P2', (60, 480)), ('P3', (240, 1440)), ('P4', (480, 4320))]:
        assert s.targets(p) == value
    for bad in ('p1', ' P1', 'P5'):
        with pytest.raises(ValueError): s.targets(bad)
    for elapsed, target, state in [(0, 100, 'ok'), (74, 100, 'ok'), (75, 100, 'warning'), (100, 100, 'warning'), (101, 100, 'breached'), (11, 15, 'ok'), (12, 15, 'warning')]:
        assert s.sla_state(elapsed, target) == state
    for elapsed, target in [(-1, 1), (0, 0), (1, -1)]:
        with pytest.raises(ValueError): s.sla_state(elapsed, target)


def test_business():
    mon = datetime(2026, 11, 16)
    for day in range(7):
        for hour, minute, inside in [(7, 59, False), (8, 0, True), (15, 59, True), (16, 0, False)]:
            assert s.is_business_time(mon + timedelta(days=day, hours=hour, minutes=minute)) == (inside and day < 5)
    fri = datetime(2026, 11, 20, 15, 30, 44)
    for n, end in [(0, datetime(2026,11,20,15,30)), (30, datetime(2026,11,20,16)), (31, datetime(2026,11,23,8,1)), (510, datetime(2026,11,23,16))]:
        assert s.add_business_minutes(fri, n) == end
        assert s.business_minutes_between(fri, end) == n
    assert s.add_business_minutes(datetime(2026,11,21,12), 0) == datetime(2026,11,23,8)
    assert s.add_business_minutes(datetime(2026,11,16,7), 1) == datetime(2026,11,16,8,1)
    assert s.business_minutes_between(datetime(2026,11,20,7), datetime(2026,11,23,17)) == 960
    with pytest.raises(ValueError): s.add_business_minutes(mon, -1)
    with pytest.raises(ValueError): s.business_minutes_between(mon, mon - timedelta(minutes=1))
    with pytest.raises(ValueError): s.business_minutes_between(mon, mon + timedelta(days=367))
    with pytest.raises(ValueError): s.add_business_minutes(mon, 500000)


def test_escalation():
    for p, base in [('P1',1), ('P2',1), ('P3',0), ('P4',0)]:
        for breach in (False, True):
            for reopens in (0, 1, 2, 3):
                assert s.escalation_tier(p, breach, reopens) == min(3, base + int(breach) + int(breach and p == 'P1') + int(reopens >= 2))
    with pytest.raises(ValueError): s.escalation_tier('P5', False, 0)
    with pytest.raises(ValueError): s.escalation_tier('P1', False, -1)


def test_duration():
    for value, expected in [('90m',90), ('1h30m',90), ('2d',2880), ('1d4h',1680), ('1d0h5m',1445), ('0h60m',60), ('1h59m',119), (' 1m ',1)]:
        assert s.parse_duration(value) == expected
    for value in ('', '0m', '1.5h', '30m1h', '-5m', '1 h', '1h60m', '1d60m', '1H', '1m1m'):
        with pytest.raises(ValueError): s.parse_duration(value)
