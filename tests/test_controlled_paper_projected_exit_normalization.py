from app.mme_scalpx.services.strategy_family.position_exit_manager import (
    normalize_controlled_paper_projected_exit_side,
)


def test_projected_exit_side_normalizes_to_unknown():
    assert normalize_controlled_paper_projected_exit_side("CONTROLLED_PAPER_PROJECTED") == "UNKNOWN"
    assert normalize_controlled_paper_projected_exit_side("PROJECTED") == "UNKNOWN"
    assert normalize_controlled_paper_projected_exit_side("PAPER_PROJECTED") == "UNKNOWN"


def test_normalization_preserves_flat_and_known_sides():
    assert normalize_controlled_paper_projected_exit_side("FLAT") == "FLAT"
    assert normalize_controlled_paper_projected_exit_side("CALL") == "CALL"
    assert normalize_controlled_paper_projected_exit_side("PUT") == "PUT"


def test_normalization_empty_is_unknown():
    assert normalize_controlled_paper_projected_exit_side("") == "UNKNOWN"
    assert normalize_controlled_paper_projected_exit_side(None) == "UNKNOWN"
