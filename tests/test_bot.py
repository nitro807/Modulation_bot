import pytest
from bot import (
    generate_modulation,
    generate_step_for_tonality,
    MAJOR_TONALITIES,
    MINOR_TONALITIES,
    MAJOR_STEPS,
    MINOR_STEPS,
)


def test_generate_modulation_no_step():
    modulation = generate_modulation()
    assert isinstance(modulation, str)
    assert ", " in modulation


@pytest.mark.parametrize("tonality", MAJOR_TONALITIES)
def test_generate_step_for_major_tonality(tonality):
    result = generate_step_for_tonality(tonality)
    assert isinstance(result, str)
    assert tonality in result
    assert any(step in result for step in MAJOR_STEPS)


@pytest.mark.parametrize("tonality", MINOR_TONALITIES)
def test_generate_step_for_minor_tonality(tonality):
    result = generate_step_for_tonality(tonality)
    assert isinstance(result, str)
    assert tonality in result
    assert any(step in result for step in MINOR_STEPS)


def test_generate_step_for_invalid_tonality():
    result = generate_step_for_tonality("Z-dur")
    assert result is None
