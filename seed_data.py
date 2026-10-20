"""Seed data: target models, trigger keywords, part dictionary, OEM number formats.

Model aliases are regexes matched (case-insensitive) against a thread's
motor-talk car tag first, then its title. Part aliases are word-start
regexes, so "lüftungsgitter" also matches "Lüftungsgitterblende".
"""

# brand, model_name, chassis_code, year_from, year_to, [alias regexes]
MODELS = [
    ("BMW", "3er", "E30", 1982, 1994, [r"\bE ?30\b"]),
    ("BMW", "5er", "E34", 1988, 1996, [r"\bE ?34\b"]),
    ("BMW", "3er", "E36", 1990, 2000, [r"\bE ?36\b"]),
    ("BMW", "5er", "E28", 1981, 1988, [r"\bE ?28\b"]),
    ("BMW", "6er", "E24", 1976, 1989, [r"\bE ?24\b"]),
    ("BMW", "5er", "E39", 1995, 2004, [r"\bE ?39\b"]),
    ("Mercedes", "E-Klasse", "W124", 1984, 1997, [r"\b[WSCA] ?124\b"]),
    ("Mercedes", "190", "W201", 1982, 1993, [r"\bW ?201\b", r"\b190 ?E\b", r"\b190 ?D\b"]),
    ("Mercedes", "S-Klasse", "W126", 1979, 1991, [r"\b[WC] ?126\b"]),
    ("Mercedes", "SL", "R129", 1989, 2001, [r"\bR ?129\b"]),
    ("Mercedes", "S-Klasse", "W140", 1991, 1998, [r"\b[WC] ?140\b"]),
    ("Mercedes", "SL", "R107", 1971, 1989, [r"\b[RC] ?107\b"]),
    ("Audi", "80/90/Coupé/Cabrio", "B3/B4", 1986, 2000, [r"\bB[34]/(89|8C|8A)\b", r"\bAudi (80|90) B ?[34]\b", r"\bAudi (Cabriolet|Coupé|Coupe) (89|8G)\b", r"\bAudi 90\b"]),
    ("Audi", "100/200", "Typ 44", 1982, 1991, [r"\bC3/44\b", r"\bTyp ?44\b", r"\bAudi (100|200) C ?3\b"]),
    ("Audi", "100/A6", "C4", 1990, 1997, [r"\bC4/4A\b", r"\b(A6|100|S4|S6) C ?4\b"]),
    ("Audi", "A4", "B5", 1994, 2001, [r"\bB5/8D\b", r"\b[AS]4 B ?5\b"]),
    ("Audi", "Coupé/Ur-quattro", "Typ 85", 1980, 1991, [r"\b(Typ ?85|Ur-?quattro|Urquattro)\b", r"\bAudi (Coupé|Coupe|quattro) (B2|81|85)\b", r"\bAudi quattro\b"]),
    ("Audi", "A8", "D2", 1994, 2002, [r"\bD2/4D\b", r"\b[AS]8 D ?2\b"]),
    ("Porsche", "944/968", "944/968", 1982, 1995, [r"\b9(44|68)\b"]),
    ("Porsche", "911", "964", 1989, 1994, [r"\b964\b"]),
    ("Porsche", "928", "928", 1977, 1995, [r"\b928\b"]),
    ("Porsche", "911", "993", 1993, 1998, [r"\b993\b"]),
    ("Porsche", "Boxster", "986", 1996, 2004, [r"\b986\b"]),
    ("Porsche", "924", "924", 1976, 1988, [r"\b924\b"]),
    ("VW", "Golf 2/Jetta 2", "Golf 2", 1983, 1992, [r"\b(Golf|Jetta) (2|II)\b(?![.,]\d)", r"\b19E\b", r"\b1G\b"]),
    ("VW", "Corrado", "Corrado", 1988, 1995, [r"\bCorrado\b"]),
    ("VW", "Transporter", "T3", 1979, 1992, [r"\bT ?3\b"]),
    ("VW", "Golf 1/Cabrio", "Golf 1", 1974, 1993, [r"\b(Golf|Jetta) (1|I)\b(?![.,]\d)", r"\(17\b", r"\b155\)"]),
    ("VW", "Golf 3/Vento", "Golf 3", 1991, 1999, [r"\bGolf (3|III)\b(?![.,]\d)", r"\b1H\b", r"\bVento\b"]),
    ("VW", "Scirocco 2", "Scirocco 2", 1981, 1992, [r"\bScirocco (2|II)\b", r"\b53B\b"]),
]

# phrase, lang, kind
KEYWORDS = [
    ("nicht mehr lieferbar", "de", "nla"),
    ("nicht lieferbar", "de", "nla"),
    ("NLA", "en", "nla"),
    ("ersatzlos entfallen", "de", "nla"),
    ("nicht mehr erhältlich", "de", "nla"),
    ("nicht mehr zu bekommen", "de", "nla"),
    ("gibt es nicht mehr", "de", "nla"),
    ("gibt's nicht mehr", "de", "nla"),
    ("gibts nicht mehr", "de", "nla"),
    ("ausgelaufenes teil", "de", "nla"),
    ("no longer available", "en", "nla"),
    ("discontinued", "en", "nla"),
    ("not available anymore", "en", "nla"),
    ("abgebrochen", "de", "broken"),
    ("gebrochen", "de", "broken"),
    ("zerbröselt", "de", "broken"),
    ("porös", "de", "broken"),
    ("gerissen", "de", "broken"),
    ("kaputt", "de", "broken"),
    ("broken", "en", "broken"),
    ("cracked", "en", "broken"),
    ("ersatzteil gesucht", "de", "searching"),
    ("suche", "de", "searching"),
    ("wo bekomme ich", "de", "searching"),
    ("wo bekommt man", "de", "searching"),
    ("bezugsquelle", "de", "searching"),
    ("hat jemand noch", "de", "searching"),
    ("looking for", "en", "searching"),
    ("where to find", "en", "searching"),
]

# canonical_name, category, size S/M/L, visible_surface, safety_relevant, [(alias, lang)]
PARTS = [
    ("Clip / Halteklammer", "clip", "S", 0, 0, [("clip", "de"), ("klammer", "de"), ("halteklammer", "de"), ("spreizniet", "de"), ("befestigungsclip", "de")]),
    ("Halter (allgemein)", "holder", "S", 0, 0, [("halter", "de"), ("halterung", "de"), ("bracket", "en")]),
    ("Lüftungsgitter / Luftdüse", "vent", "M", 1, 0, [("lüftungsgitter", "de"), ("luftdüse", "de"), ("lüftungsdüse", "de"), ("ausströmer", "de"), ("air vent", "en")]),
    ("Schalterblende / Blindstopfen", "cover", "S", 1, 0, [("schalterblende", "de"), ("blindstopfen", "de"), ("blindabdeckung", "de"), ("switch blank", "en")]),
    ("Abdeckung / Blende (allgemein)", "cover", "M", 1, 0, [("abdeckung", "de"), ("blende", "de"), ("abdeckkappe", "de"), ("kappe", "de"), ("cover", "en")]),
    ("Becherhalter / Getränkehalter", "holder", "M", 1, 0, [("becherhalter", "de"), ("getränkehalter", "de"), ("cupholder", "en"), ("cup holder", "en")]),
    ("Aschenbecher", "cover", "M", 1, 0, [("aschenbecher", "de"), ("ashtray", "en")]),
    ("Handschuhfach Scharnier / Schloss", "mechanism", "S", 0, 0, [("handschuhfach", "de"), ("glovebox", "en"), ("glove box", "en")]),
    ("Sonnenblende Halter / Clip", "holder", "S", 0, 0, [("sonnenblende", "de"), ("sun visor", "en")]),
    ("Fensterkurbel", "knob", "S", 1, 0, [("fensterkurbel", "de"), ("window crank", "en")]),
    ("Türöffner / Türgriff innen", "handle", "S", 1, 0, [("türöffner", "de"), ("türgriff", "de"), ("innengriff", "de"), ("door handle", "en")]),
    ("Knopf / Drehknopf / Taste", "knob", "S", 1, 0, [("drehknopf", "de"), ("knopf", "de"), ("taste", "de"), ("knob", "en"), ("button", "en")]),
    ("Schaltknauf / Schaltsack Rahmen", "knob", "S", 1, 0, [("schaltknauf", "de"), ("schaltsack", "de"), ("shift knob", "en")]),
    ("Mittelkonsole Teil", "trim", "L", 1, 0, [("mittelkonsole", "de"), ("center console", "en"), ("centre console", "en")]),
    ("Tachoblende / Kombiinstrument Rahmen", "trim", "M", 1, 0, [("tachoblende", "de"), ("tachorahmen", "de"), ("instrumentenblende", "de"), ("cluster bezel", "en")]),
    ("Zierleiste innen", "trim", "L", 1, 0, [("zierleiste", "de"), ("leiste", "de"), ("trim strip", "en")]),
    ("Verkleidung (allgemein)", "trim", "L", 1, 0, [("verkleidung", "de"), ("trim panel", "en")]),
    ("Kofferraum Abdeckung / Haken", "trim", "M", 0, 0, [("kofferraum", "de"), ("laderaum", "de"), ("trunk", "en")]),
    ("Sitzverstellung Hebel / Abdeckung", "handle", "S", 1, 0, [("sitzhebel", "de"), ("sitzverstellung", "de"), ("seat lever", "en")]),
    ("Kopfstütze Führung", "holder", "S", 0, 0, [("kopfstütze", "de"), ("headrest", "en")]),
    ("Lautsprecherabdeckung", "cover", "M", 1, 0, [("lautsprecherabdeckung", "de"), ("lautsprechergitter", "de"), ("speaker grille", "en")]),
    ("Spiegel Abdeckung / Dreieck innen", "cover", "S", 1, 0, [("spiegeldreieck", "de"), ("spiegelabdeckung", "de"), ("mirror cover", "en")]),
    ("Leuchte Gehäuse innen / Lichtschalter", "cover", "S", 1, 0, [("innenleuchte", "de"), ("lichtschalter", "de"), ("leselampe", "de")]),
    ("Zahnrad / Getriebe klein (Tacho, Klappe)", "mechanism", "S", 0, 0, [("zahnrad", "de"), ("ritzel", "de")]),
    ("Kabelführung / Tülle", "clip", "S", 0, 0, [("kabelführung", "de"), ("tülle", "de"), ("grommet", "en")]),
    ("Radio / Ablagefach Einsatz", "trim", "M", 1, 0, [("ablagefach", "de"), ("ablage", "de"), ("radioblende", "de"), ("storage tray", "en")]),
    ("Emblem / Schriftzug", "exterior", "S", 1, 0, [("emblem", "de"), ("schriftzug", "de"), ("badge", "en")]),
    ("Kühlergrill Teil", "exterior", "L", 1, 0, [("kühlergrill", "de"), ("grill", "de"), ("grille", "en")]),
    ("Stoßstange / Spoiler Teil", "exterior", "L", 1, 0, [("stoßstange", "de"), ("spoiler", "de"), ("bumper", "en")]),
    # Safety relevant: kept so they show up, but printability = 0
    ("Gurtschloss / Gurtteil", "safety", "S", 0, 1, [("gurtschloss", "de"), ("gurt", "de"), ("seatbelt", "en"), ("seat belt", "en")]),
    ("Airbag Abdeckung", "safety", "M", 1, 1, [("airbag", "de")]),
    ("Brems- / Lenkungsteil", "safety", "M", 0, 1, [("brems", "de"), ("lenkung", "de"), ("lenkrad", "de"), ("brake", "en"), ("steering", "en")]),
]

# OEM part number formats per brand
OEM_PATTERNS = {
    "BMW": r"\b\d{2}[ .]?\d{2}[ .]?\d[ .]?\d{3}[ .]?\d{3}\b",
    "Mercedes": r"\b[AN][ .]?\d{3}[ .]?\d{3}[ .]?\d{2}[ .]?\d{2}\b",
    "Audi": r"\b\d[0-9A-Z]{2}[ .-]?\d{3}[ .-]?\d{3}(?:[ .-]?[A-Z]{1,3})?\b",
    "VW": r"\b\d[0-9A-Z]{2}[ .-]?\d{3}[ .-]?\d{3}(?:[ .-]?[A-Z]{1,3})?\b",
    "Porsche": r"\b9\d{2}[ .]?\d{3}[ .]?\d{3}[ .]?\d{2}\b",
}
