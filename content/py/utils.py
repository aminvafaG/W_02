
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple, Optional, List, Dict, Any

import numpy as np
import pandas as pd

# --------------------------
# Data loading
# --------------------------
def load_units(json_path: str, /) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Positional-only json_path.
    Returns (df, orientations) where df has list-like columns 'control' and 'laser'.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ori = np.array(data["orientations"], dtype=float)
    rows = []
    for u in data["units"]:
        rows.append(u)
    df = pd.DataFrame(rows)
    # Ensure list columns are Python lists (for pyodide/json)
    df["control"] = df["control"].apply(list)
    df["laser"] = df["laser"].apply(list)
    return df, ori

# --------------------------
# "arguments"-like pattern using dataclasses
# --------------------------
@dataclass
class FilterArgs:
    layers: Optional[Sequence[str]] = None          # e.g., ["SG","G"]
    group: Optional[str] = None                     # "MUL" or "MXH"
    osi: Tuple[float, float] = (0.0, 1.0)           # (min, max)
    hbw: Tuple[float, float] = (0.0, 180.0)         # (min, max)
    ids: Optional[Sequence[int]] = None             # explicit unit ids

# Keyword-only args (MATLAB name-value style)
def filter_units(df: pd.DataFrame, /, *, layers: Optional[Sequence[str]] = None,
                 group: Optional[str] = None, osi: Tuple[float, float] = (0.0, 1.0),
                 hbw: Tuple[float, float] = (0.0, 180.0), ids: Optional[Sequence[int]] = None
                 ) -> pd.DataFrame:
    """
    Example of positional-only (df) and keyword-only (filters).
    """
    out = df.copy()
    if layers:
        out = out[out["layer"].isin(layers)]
    if group and group in {"MUL","MXH"}:
        out = out[out["group"] == group]
    if ids:
        out = out[out["id"].isin(ids)]
    lo, hi = osi
    out = out[(out["osi_control"]>=lo) & (out["osi_control"]<=hi)]
    lhbw, hhbw = hbw
    # Some HBWs can be missing (None); drop NAs before compare
    out = out.dropna(subset=["hbw_control"])
    out = out[(out["hbw_control"]>=lhbw) & (out["hbw_control"]<=hhbw)]
    return out

def summarize(df: pd.DataFrame, /, *, group_by: str, stat: str = "mean") -> pd.DataFrame:
    """
    Keyword-only group_by and stat; validates options (like MATLAB arguments block).
    """
    if stat not in {"mean","median","count"}:
        raise ValueError("stat must be 'mean'|'median'|'count'")
    g = df.groupby(group_by, dropna=False)
    if stat == "mean":
        return g[["osi_control","hbw_control","mean_control"]].mean(numeric_only=True)
    if stat == "median":
        return g[["osi_control","hbw_control","mean_control"]].median(numeric_only=True)
    return g.size().to_frame("count")

# Mixed signatures: positional-only + varargs (rarely needed, just to demo)
def get_tuning_matrix(df: pd.DataFrame, /, kind: str = "control", *,
                      unit_ids: Optional[Sequence[int]] = None
                      ) -> np.ndarray:
    """
    Returns an array (n_units x n_orientations) for the chosen kind ('control'|'laser').
    """
    if kind not in {"control","laser"}:
        raise ValueError("kind must be 'control' or 'laser'")
    _df = df if unit_ids is None else df[df["id"].isin(unit_ids)]
    curves = _df[kind].to_list()
    # ensure equal length
    L = len(curves[0]) if len(curves)>0 else 0
    A = np.zeros((len(curves), L), dtype=float)
    for i, c in enumerate(curves):
        A[i, :] = np.asarray(c, dtype=float)
    return A

def classify_effect(control: Sequence[float], laser: Sequence[float], /, *, flank_deg: int = 60) -> str:
    """
    Very simple heuristic: if laser roughly scales control (high correlation), call it 'MUL'.
    If laser suppresses flanks more than the peak, call it 'MXH'.
    """
    c = np.asarray(control, dtype=float)
    l = np.asarray(laser, dtype=float)
    if c.std() < 1e-6:
        return "MUL"
    corr = np.corrcoef(c, l)[0,1]
    return "MUL" if corr > 0.95 else "MXH"
