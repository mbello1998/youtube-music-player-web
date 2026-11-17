from reorganize_playlist import set_track_category, DEFAULT_CATEGORY_ORDER


def test_default_categories_defined():
    assert "Eletrônica" in DEFAULT_CATEGORY_ORDER
    assert "Sertanejo & Forró" in DEFAULT_CATEGORY_ORDER
    assert "Funk & Mega Funk" in DEFAULT_CATEGORY_ORDER


def test_set_track_category_updates_catalog(tmp_path, monkeypatch):
    catalog = [
        {"id": "1", "title": "Song A", "artist": "Artist X", "category": "Eletrônica", "video_id": "v1"},
        {"id": "2", "title": "Song B", "artist": "Artist Y", "category": "Sertanejo & Forró", "video_id": "v2"},
    ]
    test_file = tmp_path / "test_cats.json"
    monkeypatch.setattr("reorganize_playlist.CATEGORIES_FILE", test_file)

    set_track_category(catalog, "Song A", "Funk & Mega Funk")
    assert catalog[0]["category"] == "Funk & Mega Funk"
