#!/usr/bin/env python3
"""One-time lossless Naxxramas wrapper -> date-map migration, safe to rerun."""
from pathlib import Path
import json
import subprocess
from date_schema import load, put, migrate_document, validate_timeline
ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = load(ROOT/"cards.json")
    if catalog.get("set") != "Curse of Naxxramas":
        raise ValueError("Naxxramas only")
    current = {c["id"]:c for c in catalog["cards"]}
    commit = subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    audit = {c["id"]: c for c in load(ROOT/"tools/naxx-release-audit.json")["cards"]}
    changed = 0
    for path in sorted((ROOT/"data").glob("*.json")):
        document = load(path)
        if "card" not in document:
            validate_timeline(document)
            if not (ROOT/"metadata"/path.name).exists():
                raise ValueError(f"Missing metadata for {path.name}")
            continue
        sidecar = ROOT/"metadata"/path.name
        if sidecar.exists():
            raise ValueError(f"Refusing to overwrite migration evidence: {sidecar}")
        timeline, meta = migrate_document(document, current.get(path.stem), commit)
        mechanics_correction = meta.pop("mechanicsCorrection", None)
        reviewed = audit[path.stem]
        meta["baselineEvidence"] = {
            "numericTypeStatus": reviewed["initialNumericSpecStatus"],
            "textStatus": reviewed["historicalDisplayTextStatus"],
            "source": reviewed["source"],
            "audit": "tools/naxx-release-audit.json",
        }
        meta["confidenceNote"] = "All five Korean wing reward dates and initial numeric/type data have source support. Exact historical Korean wording and all intermediate cosmetic edits are not fully verified. Existing partial evidence is preserved; strict lookup does not promote it."
        meta["currentOnlyFields"] = sorted(set(current[path.stem]) - set(meta["canonicalFields"]) - {"releasedAt", "releaseStatus"})
        if document.get("historicalTextObservations"):
            meta["undatedEvidence"] = {"historicalTextObservations": document["historicalTextObservations"], "reason": "Client observation ranges are not verified Korean effective dates."}
        if mechanics_correction:
            meta["mechanicsCorrection"] = mechanics_correction
        meta["availabilityScope"] = "User-selected Korean normal-match play availability: constructed reward opening, excluding adventure-only previews and client preloading."
        if path.stem in ("FP1_014", "FP1_015", "FP1_014t"):
            meta["availabilityObservations"] = [load(ROOT/"tools/naxx-date-recheck.json")["separateAvailabilityObservation"]]
        put(sidecar,meta)
        put(path,timeline)
        changed += 1
    print(json.dumps({"migrated":changed,"format":"date-map-1"}))


if __name__ == "__main__":
    main()
