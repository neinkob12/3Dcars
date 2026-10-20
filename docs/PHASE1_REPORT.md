# Phase 1 Report: motor-talk.de test run

Run date: 2026-10-20. 30 models, 20 threads per model, up to 10 listing pages per board.

## TL;DR

* The pipeline works end to end: discovery, polite scraping, extraction, scoring, CSV.
* The **sample is far too small to rank parts.** 443 threads read gave 38 mentions, and only about 8 are real "plastic part is NLA" signals. No part reached 3 mentions.
* The **method is right, the sampling is wrong.** Reading the newest 20 threads per model is mostly noise. Phase 2 should scan *all* listing pages (cheap, 40 threads per request) and only read threads whose title hints at a missing part.
* **Porsche is invisible** on motor-talk: a single shared board dominated by modern Porsches gave 1 to 5 classic threads per model.

## Numbers

| | |
|---|---|
| Requests | 718 + 21 discovery (1 every 5 s) |
| Threads listed (assigned to a model) | 6,144 |
| Threads read | 443 |
| Mentions | 38 |
| Mentions with a recognized part | 16 |
| Real plastic NLA signals (manual check) | about 8 |
| Part/model pairs with 3 or more mentions | 0 (excluding safety parts) |

## Per model (mentions per 1,000 threads read)

Only a direction, not a result: 1 mention = 50 points here.

| Rank | Model | Rate | Note |
|---|---|---|---|
| 1 | Mercedes R129 SL | 350 | Most useful hits: Cliphalter, Handschuhfach, Öldeckel |
| 2 | Audi 80 B3/B4 | 300 | Mostly antenna and fuel system, not printable |
| 3 | VW T3 | 200 | Screws, cables, belts: not printable |
| 4 | BMW E34 | 150 | All brake parts (safety, excluded) |
| 4 | Audi A8 D2 | 150 | Brakes, power steering hose |
| 4 | BMW E36 | 150 | 318is badge |
| 7 | VW Golf 1 | 100 | Dashboard trim, with OEM number |
| ... | 15 models | 0 | Includes all 7 Porsches, E30, E39, W126, B5, C4 |

## Best individual signals

These are exactly the kind of parts the business is about:

1. **R129 SL Cliphalter (clip holders)**: "9 Cliphalter, die genauso gern brechen, und schon lange nicht mehr erhältlich sind, bzw. vereinzelt manchmal als Reproteile aus dem 3D Drucker". Proof that owners already look for printed replacements.
2. **Golf 1 Cabrio dashboard trim (Blende), OEM 155 867 243**: "seit 01.03.2015 ersatzlos entfallen". The OEM number was extracted automatically.
3. **Golf 1 Cabrio Tachoblende / Armaturentafel**: cracked in many places, owner looking for a source.
4. **E36 318is "is" badge**: not available anywhere.
5. **R129 glove box parts** after a break-in: new parts no longer available.

## What worked

* **Model attribution is excellent.** motor-talk tags each thread with an exact chassis ("Audi 100 C3/44", "VW Golf 1 (17, 155)"). After tuning the aliases, all 36 test tags mapped correctly, including 8 untracked models (E21, R230, Golf 4...) that were correctly left out.
* **OEM number extraction** worked on BMW and VW formats in real posts.
* **Privacy**: the cache holds only titles, car tags, post ids, dates and text. No usernames or profile links on disk or in the database.
* **Resumable**: the container restarted mid-run, and the rerun used the cache without refetching anything.
* **Safety filter**: brake, steering and seatbelt mentions are scored 0, as intended.

## Data quality problems

1. **Most NLA talk is not about printable parts.** Antennas, fuel lines, screws, belts, keys, membranes, brake parts. We need a negative list (metal, rubber, electronics, fasteners) or a "material" check.
2. **Weak phrases are noisy.** "gibt es nicht mehr" matched "Diesel gibt es nicht mehr allzu viele" and "den ursprünglichen E36 gibt's nicht mehr". "nicht lieferbar" also catches temporary stock-outs ("gerade nicht lieferbar"). Split phrases into strong (nicht mehr lieferbar, ersatzlos entfallen, NLA) and weak, and weight them.
3. **General complaints** ("viele Ersatzteile gibt es nicht mehr") count as mentions without a part. 22 of 38 mentions have no part.
4. **Prefix part matching** gave false positives: "kurbel" matched "Kurbelgehäuse" (fixed), and "Lenkung" in a title tagged the whole thread as a steering part.
5. **Quotes without markup** repeated posts verbatim and were double-counted (fixed).
6. **Shared boards are thin.** Porsche (one board), E24, E28, Typ 85 and Scirocco 2 got 1 to 8 threads because the newest 400 threads on their shared boards are mostly other models.
7. **Normalization fix**: the approved formula divided by threads *listed*. Mentions only come from threads *read*, so this favored small shared boards. Changed to threads read (equal 20-thread samples). Threads listed is kept as a community size column.

## What Phase 2 needs

1. **Title-filtered deep crawl**: read every listing page of each board (W124 board: 249 pages = about 10,000 threads in about 21 minutes), then read only threads whose title matches part or NLA words. Expect 10 to 50 times more real signals per request.
2. **Second source for Porsche**: pff.de (Porsche Fan Forum) has a clean robots.txt. Its terms still need checking.
3. **Extraction upgrades**: strong vs weak phrases, a non-printable negative list, and part matching on the sentence instead of a ±150 character window.
4. **Optional LLM classification pass**: for each candidate post, ask "is this a plastic part, is it NLA, which part". Precision is the bottleneck, and 40 to 400 posts per run is cheap to classify.
5. **eBay used prices and competitor catalog check**, as already planned.
6. **Permission**: motor-talk's terms (3.4) need consent for commercial use. Before a bigger crawl, a short email to gutefrage is worth considering.
