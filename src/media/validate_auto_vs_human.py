"""LLM/sääntö vs. ihmiskonsensus: F1 per luokka. Kielto ilman ihmiskultaa."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import ROOT

TABLES = ROOT / "media" / "output" / "tables"
OTOS = TABLES / "koodaus_otos.csv"
OUT = TABLES / "koodaus_llm_vs_ihminen_f1.csv"


def _f1(y_true: pd.Series, y_pred: pd.Series, labels: list[str]) -> pd.DataFrame:
    rivit = []
    for lab in labels:
        tp = int(((y_true == lab) & (y_pred == lab)).sum())
        fp = int(((y_true != lab) & (y_pred == lab)).sum())
        fn = int(((y_true == lab) & (y_pred != lab)).sum())
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec = tp / (tp + fn) if (tp + fn) else float("nan")
        if pd.isna(prec) or pd.isna(rec) or (prec + rec) == 0:
            f1 = float("nan")
        else:
            f1 = 2 * prec * rec / (prec + rec)
        rivit.append(
            {
                "luokka": lab,
                "n_true": int((y_true == lab).sum()),
                "tarkkuus": prec,
                "saanti": rec,
                "f1": f1,
            }
        )
    return pd.DataFrame(rivit)


def aja(*, pred_col: str = "aihe_saanto_v1", gold_col: str = "aihe_konsensus") -> pd.DataFrame:
    df = pd.read_csv(OTOS)
    if gold_col not in df.columns or df[gold_col].notna().sum() < 500:
        # Konsensus syntyy vasta A+B-sovituksen jälkeen
        out = pd.DataFrame(
            [
                {
                    "luokka": "",
                    "n_true": 0,
                    "tarkkuus": float("nan"),
                    "saanti": float("nan"),
                    "f1": float("nan"),
                    "huom": (
                        "ei ajettu: ihmiskonsensus puuttuu "
                        "(vaatii kaksoiskoodauksen + α; MEDIA_PREREGISTRATION)"
                    ),
                }
            ]
        )
        out.to_csv(OUT, index=False)
        print("estetty: ei ihmiskonsensusta →", OUT)
        return out

    if pred_col not in df.columns:
        raise KeyError(pred_col)
    mask = df[gold_col].notna() & df[pred_col].notna()
    y_true = df.loc[mask, gold_col].astype(str)
    y_pred = df.loc[mask, pred_col].astype(str)
    labels = sorted(set(y_true) | set(y_pred))
    out = _f1(y_true, y_pred, labels)
    out["huom"] = f"pred={pred_col} vs gold={gold_col}; n={int(mask.sum())}"
    out.to_csv(OUT, index=False)
    print("kirjoitettu", OUT)
    return out


if __name__ == "__main__":
    aja()
