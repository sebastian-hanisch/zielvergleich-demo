"""Gemeinsame Fixtures: das Handbeispiel, an dem jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zvg_scenario import Instance  # noqa: E402

HAND = ((7.0, 6.0, 7.0, 5.0), (6.0, 4.0, 3.0, 6.0), (8.0, 4.0, 7.0, 2.0), (4.0, 2.0, 2.0, 6.0))


@pytest.fixture
def hand():
    """Handbeispiel n = 4 (Zeile Person, Spalte Aufgabe). Von Hand: Summe 14 mit Plan (0, 2, 3, 1), Quadratsumme 65 mit Plan (1, 2, 3, 0),
    Maximum 5 mit Plan (3, 2, 1, 0)."""
    return Instance(HAND)


@pytest.fixture
def hand_array(hand) -> np.ndarray:
    return hand.array()
