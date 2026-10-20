import json

import pytest

import db
import extract
import motortalk
import seed
from seed_data import OEM_PATTERNS


@pytest.fixture
def conn(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.sqlite")
    seed.main()
    return db.connect()


def part_names(conn, results):
    names = []
    for _, pid, _ in results:
        names.append(None if pid is None else conn.execute("SELECT canonical_name FROM parts WHERE id = ?", (pid,)).fetchone()[0])
    return names


def run(conn, text, title="", brand="BMW"):
    return extract.post_mentions(text, title, extract.compile_keywords(conn), extract.compile_parts(conn), OEM_PATTERNS[brand])


def test_nla_with_specific_part_drops_generic(conn):
    res = run(conn, "Die Schalterblende links ist leider nicht mehr lieferbar, die Abdeckung auch.")
    assert part_names(conn, res) == ["Schalterblende / Blindstopfen"]
    assert res[0][0] == "nicht mehr lieferbar"


def test_nla_without_part_falls_back_to_title(conn):
    res = run(conn, "Das Teil ist bei BMW nicht mehr lieferbar.", title="Lüftungsgitter Mitte gesucht")
    assert part_names(conn, res) == ["Lüftungsgitter / Luftdüse"]


def test_nla_unknown_part_is_kept_as_none(conn):
    assert part_names(conn, run(conn, "Leider NLA bei Mercedes.")) == [None]


def test_nla_is_case_sensitive(conn):
    assert run(conn, "Die Anlage nla ist kaputt") == []


def test_broken_needs_search_and_part(conn):
    assert run(conn, "Motor kaputt, suche Werkstatt") == []
    res = run(conn, "Becherhalter abgebrochen, wo bekomme ich einen neuen?")
    assert part_names(conn, res) == ["Becherhalter / Getränkehalter"]


def test_bmw_oem_number_extracted(conn):
    res = run(conn, "Clip 51 41 1 916 287 ist nicht mehr lieferbar")
    assert res[0][2] == "51411916287"


def test_mercedes_oem_number_extracted(conn):
    res = run(conn, "A 124 680 12 34 gibt es nicht mehr", brand="Mercedes")
    assert res[0][2] == "A1246801234"


def test_scrub_drops_usernames():
    html = """<html><body><div class="CarTag"><span class="Tag-text">BMW 3er (E30)</span></div>
    <h1 class="DiscussionThreadHeader-headline">Titel</h1>
    <section class="Post" id="post1"><div class="PostHeader"><a class="PostHeader-nickName" href="/nutzer/max">max</a></div>
    <meta itemprop="datePublished" content="2025-01-02T10:00:00+01:00">
    <div class="PostBody"><blockquote>Zitat von max</blockquote><p>Blende nicht mehr lieferbar</p></div></section>
    </body></html>"""
    data = json.loads(motortalk.scrub(html))
    assert data["car_tag"] == "BMW 3er (E30)"
    assert data["posts"] == [{"id": "post1", "date": "2025-01-02", "text": "Blende nicht mehr lieferbar"}]
    assert "max" not in json.dumps(data)


def test_resolve_model_uses_title_only_for_vague_tags(conn):
    import scrape_motortalk
    models = scrape_motortalk.compile_models(conn)["BMW"]
    e30 = conn.execute("SELECT id FROM models WHERE chassis_code = 'E30'").fetchone()[0]
    assert scrape_motortalk.resolve_model(models, "BMW 3er E30", "") == e30
    assert scrape_motortalk.resolve_model(models, "BMW", "E30 Blende gesucht") == e30
    assert scrape_motortalk.resolve_model(models, "BMW 3er E21", "Teile vom E30 passen?") is None
