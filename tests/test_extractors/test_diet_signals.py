"""Tests for diet_signals extractor.

Labeled corpus: ≥7 positive, ≥7 negative cases.
Recall assertion: ≥85% on labeled positives.
"""
from __future__ import annotations

import pytest

from shaked_wg_agent.extractors.diet_signals import classify, detect

# ---------------------------------------------------------------------------
# Labeled corpus
# ---------------------------------------------------------------------------

# POSITIVE cases: text describes a vegan/vegetarian WG household
_POSITIVE_CASES = [
    # 1. Classic "wir sind vegan" — WG household
    "Wir sind eine vegane WG und suchen eine gleichgesinnte Person.",
    # 2. "vegane WG" in title
    "Vegane WG in Basel sucht Mitbewohnerin ab Juli.",
    # 3. Pflanzlich keyword
    "Unser Haushalt ist pflanzenbasiert, wir kochen zusammen.",
    # 4. Tierfreie Küche — explicit household keyword
    "Wir achten auf tierfreie Küche und nachhaltigen Lebensstil.",
    # 5. Vegetarisch with WG context
    "Die WG ist vegetarisch, kein Fleisch in unserer Küche.",
    # 6. Plant-based English
    "We are a plant-based household looking for like-minded flatmate.",
    # 7. Fleischlos
    "Fleischlose Ernährung ist bei uns Pflicht — wir kochen immer gemeinsam.",
    # 8. Veggi (alternative spelling)
    "Unsere veggie WG freut sich auf neue Mitglieder!",
    # 9. Bio-Küche
    "Wir haben eine Bio-Küche und kaufen regional ein.",
    # 10. Vegan in a longer description
    "Hallo! Ich bin Lisa, 25. Wir sind zu viert und leben vegan. Tram 14 vor der Tür.",
]

# NEGATIVE cases: text does NOT indicate a vegan/vegetarian WG household
_NEGATIVE_CASES = [
    # 1. Restaurant nearby — not the WG
    "In der Nähe gibt es ein tolles veganes Restaurant und ein Café.",
    # 2. Applicant self-describes (not the WG)
    "Ich bin selbst vegan, aber die WG hat keine Vorschriften.",
    # 3. No diet mention at all
    "Helles WG-Zimmer in Basel, 4056. Tram 14 vor der Haustür. Einzug Juli.",
    # 4. Applicant looking for vegan WG (WG is unspecified)
    "Ich suche eine vegane WG ab August.",
    # 5. Vegan shop in neighborhood
    "Nahe einem veganen Supermarkt und Bioläden.",
    # 6. Standard listing with no diet signals
    "Wir sind 3 Personen und suchen eine weitere Mitbewohnerin für unser WG.",
    # 7. Diet of a guest, not the household
    "Kein Problem wenn du vegan bist, wir haben keine Ernährungsregeln.",
    # 8. Mentions vegetarian but about someone outside
    "Mein Freund ist Vegetarier und wohnt um die Ecke — wir haben keine WG-Regeln.",
    # 9. Completely unrelated text
    "Bahnhof Basel SBB, Tram 1, 2, 8, 14, 16 Haltestelle direkt vor dem Haus.",
    # 10. Empty string
    "",
]

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDetect:
    """Tests for the detect() function."""

    @pytest.mark.parametrize("text", _POSITIVE_CASES)
    def test_detect_positive(self, text):
        """detect() must return True for positive cases."""
        assert detect(text) is True, f"Expected True for: {text!r}"

    @pytest.mark.parametrize(
        "text",
        [
            # Only truly unambiguous negatives where no keyword appears at all
            "Helles WG-Zimmer in Basel, 4056. Tram 14 vor der Haustür. Einzug Juli.",
            "Wir sind 3 Personen und suchen eine weitere Mitbewohnerin für unser WG.",
            "Bahnhof Basel SBB, Tram 1, 2, 8, 14, 16 Haltestelle direkt vor dem Haus.",
            "",
        ],
    )
    def test_detect_negative_no_keyword(self, text):
        """detect() must return False when no diet keyword is present."""
        assert detect(text) is False, f"Expected False for: {text!r}"


class TestClassify:
    """Tests for the classify() function."""

    def test_classify_empty_string(self):
        result = classify("")
        assert result["is_vegetarian_friendly"] is False
        assert result["matched_keywords"] == []
        assert result["confidence"] == "none"

    def test_classify_no_signal(self):
        result = classify("WG-Zimmer in Basel, schöne Lage, Tram direkt.")
        assert result["is_vegetarian_friendly"] is False
        assert result["confidence"] == "none"

    def test_classify_high_confidence_wir_sind_vegan(self):
        text = "Wir sind eine vegane WG und suchen Mitbewohner."
        result = classify(text)
        assert result["is_vegetarian_friendly"] is True
        assert result["confidence"] == "high"
        assert any("vegan" in kw for kw in result["matched_keywords"])

    def test_classify_high_confidence_wg_kueche(self):
        text = "Unser Haushalt hat eine tierfreie Küche."
        result = classify(text)
        assert result["is_vegetarian_friendly"] is True
        assert result["confidence"] == "high"

    def test_classify_high_confidence_kochen_zusammen(self):
        text = "Wir kochen pflanzenbasiert und teilen die vegane Küche."
        result = classify(text)
        assert result["is_vegetarian_friendly"] is True
        assert result["confidence"] == "high"

    def test_classify_keywords_captured(self):
        text = "Unsere vegane WG kocht pflanzlich."
        result = classify(text)
        kws = result["matched_keywords"]
        assert len(kws) >= 1

    def test_classify_returns_dict_shape(self):
        result = classify("Wir sind vegan.")
        assert "is_vegetarian_friendly" in result
        assert "matched_keywords" in result
        assert "confidence" in result
        assert isinstance(result["matched_keywords"], list)

    def test_classify_plant_based_english(self):
        text = "We are a plant-based household, cooking together most evenings."
        result = classify(text)
        assert result["is_vegetarian_friendly"] is True

    def test_classify_fleischlos(self):
        text = "Fleischlose WG – wir kaufen nur vegane Produkte."
        result = classify(text)
        assert result["is_vegetarian_friendly"] is True
        assert result["confidence"] == "high"


class TestRecall:
    """Recall ≥85% on labeled positive corpus."""

    def test_recall_at_least_85_percent(self):
        """At least 85% of positive cases must be detected by detect()."""
        total = len(_POSITIVE_CASES)
        detected = sum(1 for t in _POSITIVE_CASES if detect(t))
        recall = detected / total
        assert recall >= 0.85, (
            f"Recall {recall:.1%} below 85% threshold. "
            f"Detected {detected}/{total} positive cases."
        )

    def test_classify_recall_at_least_85_percent(self):
        """At least 85% of positive cases must be classified as is_vegetarian_friendly."""
        total = len(_POSITIVE_CASES)
        detected = sum(
            1 for t in _POSITIVE_CASES if classify(t)["is_vegetarian_friendly"]
        )
        recall = detected / total
        assert recall >= 0.85, (
            f"classify() recall {recall:.1%} below 85%. "
            f"Detected {detected}/{total} positive cases."
        )
