# 3D Printed Car Parts: Project Context

Condensed context from the founding chat. Phase 1 kickoff scope lives in `docs/PHASE1_PROPOSAL.md`.

## The idea

A platform for discontinued ("nicht mehr lieferbar", NLA) plastic car parts, made via 3D printing.

* Customers can buy from a catalog of already designed parts.
* Customers can also request any missing part ("tell us what's missing, we'll make it").
* Team for now: founder + Claude + AI-written CAD (CadQuery / OpenSCAD / build123d), plus a freelancer later if needed.

## Why now

* LLMs can now write usable parametric CAD code.
* Opportunities lie in domains that are valuable, verifiable and undertrained. "Does the printed part fit?" is verifiable.
* Existing shops have clunky catalogs and warn about imperfect fit. Better UX plus fit guarantees is a differentiator.
* Distribution is the bottleneck. SEO per OEM part number is the main channel.

## Key decisions so far

* Cars, not appliances or other categories.
* Brand is open. BMW is already crowded, so compare BMW, Mercedes, Audi, Porsche and VW youngtimers/oldtimers by data before committing.
* Shop + platform, both. Catalog plus "we make anything" request intake.
* No public voting. Demand is counted quietly via a waitlist behind the request form.
* Customer price target: mid to upper tier cars. Enthusiast plus tuning overlap.

## Corrected assumptions

* Video game car models are NOT usable for measurements (visual meshes, inaccurate, hidden parts missing, licensed IP).
* Real dimension sources: the customer's broken part (photos next to a ruler, caliper measurements, phone 3D scan), plus OEM parts catalogs (BMW ETK via RealOEM, Mercedes EPC) for exploded diagrams and OEM part numbers.

## Competitors (BMW heavy)

* Treedy Labs (eBay): print-to-order vintage BMW parts.
* DoviWorks (eBay): BMW E30 to E90 clips, cup holders, trim, some VW.
* BimmerWorld / MOD-ing: printed E30 parts around $30, openly warns fit/finish is not 1:1.
* Etsy sellers: e.g. E30 switch blank about $6.
* Free files: MakerWorld, Printables, Cults3D.
* Germany: 3D-Printineer (Adelsdorf), oldtimer parts for Audi, BMW, Jaguar, Ferrari.
* OEMs: Porsche Classic and Mercedes Classic print a small number of parts.

Gap: existing players are fixed-catalog eBay/Etsy shops. Nobody seems to own the "request any missing part" layer, especially in German.

## Business model

* Design once, sell many. The design file is the asset; printing is a commodity.
* Custom request pricing:
  * Exclusive: full design fee, design belongs to customer.
  * Shared (default): lower price, part goes into the public catalog.
* Flywheel: request, design (partly paid), catalog, SEO page per OEM part number, next buyer, more requests.

## Fit guarantee

1. 2 to 3 beta testers per new part (free part in exchange for fit report and photos).
2. "Verified fit by N owners" badge per model/year/variant.
3. Map fit by OEM part number and facelift variant, not just chassis code.
4. One free reprint guarantee, priced in at roughly 10 to 15%.

## Sourcing and pricing

* No own printer at first. Use print marketplaces: Craftcloud (has an API), JLC3DP, PCBWay, Xometry, Protolabs.
* Price = print cost + shipping + design fee spread over expected sales + reprint reserve.
* Materials: interiors get very hot. Use ASA, PETG, or SLS/MJF nylon (PA12). Avoid PLA.

## Risks and boundaries

* No safety-relevant parts (brakes, seatbelt mechanisms, steering, airbag area).
* Large visible surfaces are hard (finish quality).
* Some visible body parts may be design-protected. Check before selling exterior pieces.
* Scraping: respect robots.txt and site terms, rate limit politely, do not store personal data. Store only part, model and counts.

## Funnel (planned)

1. Scrape forums for NLA mentions, build a ranked list of missing parts.
2. Design the top parts, one landing page per OEM part number (SEO + small long-tail search ads).
3. Request form with silent waitlist.
4. Partnerships with oldtimer workshops and model clubs (referral cut).
5. Broad ads only later, never as "we print anything".

## Opportunity scoring (draft)

score ≈ complaint volume × used price signal × not yet solved × printability

* Complaint volume: NLA mentions for the part, normalized by how active the model's community is.
* Used price signal: used eBay prices for the part.
* Not yet solved: not already on Treedy, DoviWorks, Etsy, MakerWorld, Printables.
* Printability: plastic, non-safety, small to medium size, finish not critical.
