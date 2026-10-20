"""Score (part, model) pairs and write ranked_parts.csv plus model_summary.csv.

volume       = (mentions + mentions_recent) / threads_scanned * 1000
printability = 0 if safety relevant, else size factor * (0.7 if visible surface)
score        = volume * price_signal * unsolved * printability
price_signal and unsolved stay 1.0 until Phase 2.

Usage: python score.py [min_mentions]   (default 3)
"""

import sys
from datetime import date

import pandas as pd

import db

SIZE_FACTOR = {"S": 1.0, "M": 0.8, "L": 0.4}
RECENT_YEARS = 5


def printability(row):
    if row["is_safety_relevant"]:
        return 0.0
    return SIZE_FACTOR.get(row["size_class"], 0.8) * (0.7 if row["visible_surface"] else 1.0)


def main(min_mentions=3):
    conn = db.connect()
    today = date.today()
    cutoff = today.replace(year=today.year - RECENT_YEARS).isoformat()
    models = pd.read_sql("SELECT id AS model_id, brand, chassis_code FROM models", conn)
    scanned = pd.read_sql(
        "SELECT model_id, COUNT(*) AS threads_scanned, SUM(http_status = 200) AS threads_read"
        " FROM threads_scanned WHERE model_id IS NOT NULL GROUP BY model_id", conn)
    mentions = pd.read_sql("SELECT url, post_date, model_id, part_id, oem_pn_found FROM mentions", conn)
    parts = pd.read_sql("SELECT id AS part_id, canonical_name AS part, oem_part_number, is_safety_relevant,"
                        " size_class, visible_surface FROM parts", conn)

    # Per model summary: answers "which brand/model has most unmet demand"
    summary = models.merge(scanned, on="model_id", how="left").fillna({"threads_scanned": 0, "threads_read": 0})
    per_model = mentions.groupby("model_id").agg(
        mentions=("url", "nunique"),
        mentions_recent=("post_date", lambda d: int((d >= cutoff).sum())),
        with_part=("part_id", lambda p: int(p.notna().sum())),
    ).reset_index()
    summary = summary.merge(per_model, on="model_id", how="left").fillna(0)
    summary["mentions_per_1000_threads"] = (summary["mentions"] / summary["threads_scanned"].where(summary["threads_scanned"] > 0) * 1000).round(1)
    summary.sort_values("mentions_per_1000_threads", ascending=False).drop(columns="model_id").to_csv("model_summary.csv", index=False)

    known = mentions.dropna(subset=["part_id"])
    if known.empty:
        print("no mentions with a recognized part yet")
        pd.DataFrame().to_csv("ranked_parts.csv", index=False)
        return
    known = known.astype({"part_id": int})
    grouped = known.groupby(["part_id", "model_id"]).agg(
        mentions=("url", "count"),
        mentions_recent=("post_date", lambda d: int((d >= cutoff).sum())),
        oem_numbers=("oem_pn_found", lambda s: ", ".join(sorted(set(s.dropna())))[:120]),
        example_urls=("url", lambda u: " ".join(list(u)[:3])),
    ).reset_index()
    df = grouped.merge(parts, on="part_id").merge(models, on="model_id").merge(scanned, on="model_id")
    df["volume"] = (df["mentions"] + df["mentions_recent"]) / df["threads_scanned"] * 1000
    df["printability"] = df.apply(printability, axis=1)
    df["price_signal"] = 1.0
    df["unsolved"] = 1.0
    df["score"] = df["volume"] * df["price_signal"] * df["unsolved"] * df["printability"]

    conn.execute("DELETE FROM scores")
    now = today.isoformat()
    conn.executemany(
        "INSERT INTO scores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(int(r.part_id), int(r.model_id), int(r.mentions), int(r.mentions_recent), int(r.threads_scanned),
          float(r.volume), r.price_signal, r.unsolved, float(r.printability), float(r.score), now)
         for r in df.itertuples()],
    )
    conn.commit()

    ranked = df[df["mentions"] >= min_mentions].sort_values("score", ascending=False)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    cols = ["rank", "brand", "chassis_code", "part", "oem_part_number", "oem_numbers", "mentions", "mentions_recent",
            "threads_scanned", "volume", "printability", "price_signal", "unsolved", "score", "example_urls"]
    ranked[cols].round(2).to_csv("ranked_parts.csv", index=False)
    print(f"{len(df)} part/model pairs, {len(ranked)} with >= {min_mentions} mentions -> ranked_parts.csv")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
