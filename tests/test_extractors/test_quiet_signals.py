"""Tests for quiet_signals extractor."""
from __future__ import annotations

import pytest

from shaked_wg_agent.extractors.quiet_signals import classify, detect


class TestDetect:

    @pytest.mark.parametrize(
        "text",
        [
            "Wir sind eine ruhige WG und suchen ruhige Mitbewohner.",
            "Ruhige WG in Basel, keine Partys.",
            "Leise und entspannte Atmosphäre – keine Partys bitte.",
            "We are looking for a calm and quiet flatmate.",
            "Das Zimmer ist schallisoliert und bietet viel Ruhe.",
            "Peaceful household, no late-night noise.",
        ],
    )
    def test_detect_true(self, text):
        assert detect(text) is True, f"Expected True for: {text!r}"

    @pytest.mark.parametrize(
        "text",
        [
            "WG-Zimmer Basel, 4056, Tram 14, möbliert.",
            "Wir sind jung und offen für alles!",
            "Helles Zimmer in freundlicher WG, 750 CHF warm.",
            "",
        ],
    )
    def test_detect_false(self, text):
        assert detect(text) is False, f"Expected False for: {text!r}"


class TestClassify:

    def test_classify_empty_string(self):
        result = classify("")
        assert result["is_quiet_friendly"] is False
        assert result["matched_keywords"] == []

    def test_classify_ruhige_wg(self):
        result = classify("Ruhige WG sucht ruhige Person.")
        assert result["is_quiet_friendly"] is True
        assert len(result["matched_keywords"]) >= 1

    def test_classify_no_signal(self):
        result = classify("WG-Zimmer in Basel. Freundliche Mitbewohner.")
        assert result["is_quiet_friendly"] is False

    def test_classify_dict_shape(self):
        result = classify("Quiet and calm household.")
        assert "is_quiet_friendly" in result
        assert "matched_keywords" in result
        assert isinstance(result["matched_keywords"], list)

    def test_classify_multiple_keywords(self):
        text = "Ruhige, leise WG – wir schätzen Stille und Ruhe."
        result = classify(text)
        assert result["is_quiet_friendly"] is True

    def test_classify_english_quiet(self):
        result = classify("We are a quiet and peaceful household.")
        assert result["is_quiet_friendly"] is True

    def test_classify_ruhige_mitbewohner(self):
        result = classify("Wir suchen ruhige Mitbewohner für unser WG.")
        assert result["is_quiet_friendly"] is True

    def test_classify_leise(self):
        result = classify("Bitte leise sein nach 22 Uhr, danke!")
        assert result["is_quiet_friendly"] is True

    def test_classify_schallisoliert(self):
        result = classify("Das Zimmer ist vollständig schallisoliert.")
        assert result["is_quiet_friendly"] is True

    def test_classify_sound_insulated(self):
        result = classify("The apartment is fully sound-insulated.")
        assert result["is_quiet_friendly"] is True
