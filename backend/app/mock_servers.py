"""Mock tool servers for testing. Candidate data is fixed. The CRM mock keeps its
notes in data/mock_crm.json, so they survive a restart. Screening criteria are read
from the job description in hiring/."""

import json
from pathlib import Path
from typing import Any

from app import hiring_files
from app.auth import Role
from app.config import Settings
from app.tool_servers import Tool, ToolRegistry, ToolServer, fields_schema

EVERYONE: frozenset[Role] = frozenset({"interviewer", "manager"})
MANAGER_ONLY: frozenset[Role] = frozenset({"manager"})
ASSESSMENTS = ("strong_yes", "yes", "no", "strong_no")
SLOTS = ("2026-11-10T10:00", "2026-11-10T14:00", "2026-11-11T09:30")

SEED_CANDIDATES: dict[str, dict[str, str]] = {
    "c-001": {
        "name": "Ada Example",
        "applied_for": "ceo",
        "summary": "Ex-COO, grew a 40-person org.",
    },
    "c-002": {
        "name": "Ben Sample",
        "applied_for": "ceo",
        "summary": "Two startup exits, no board experience.",
    },
}


class CrmStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        if path.is_file():
            self._data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        else:
            self._data = {
                "candidates": {
                    cid: {**fields, "notes": []}
                    for cid, fields in SEED_CANDIDATES.items()
                }
            }
            self._save()

    def candidate(self, candidate_id: str) -> dict[str, Any]:
        found = self._data["candidates"].get(candidate_id)
        if found is None:
            raise LookupError(f"candidate {candidate_id!r} not found")
        return found

    def add_note(self, candidate_id: str, note: str, assessment: str) -> dict[str, str]:
        record = self.candidate(candidate_id)
        entry = {"note": note, "assessment": assessment}
        record["notes"].append(entry)
        self._save()
        return entry

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")


def build_registry(settings: Settings) -> ToolRegistry:
    crm = CrmStore(settings.data_dir / "mock_crm.json")

    def get_job_criteria(args: dict[str, Any]) -> dict[str, str]:
        slug = str(args.get("position", ""))
        text = hiring_files.read_job_description(
            settings.hiring_dir, slug
        )  # ValueError if invalid
        if text is None:
            raise LookupError(f"position {slug!r} not found")
        return {"position": slug, "job_description": text}

    def get_candidate_profile(args: dict[str, Any]) -> dict[str, Any]:
        cid = str(args.get("candidate_id", ""))
        record = crm.candidate(cid)
        return {
            "candidate_id": cid,
            "name": record["name"],
            "summary": record["summary"],
        }

    def list_free_slots(_: dict[str, Any]) -> list[str]:
        return list(SLOTS)

    def propose_appointment(args: dict[str, Any]) -> dict[str, str]:
        # Proposal only: the hiring manager books it by hand (ADR-0005).
        cid = str(args.get("candidate_id", ""))
        slot = str(args.get("slot", ""))
        crm.candidate(cid)
        if slot not in SLOTS:
            raise ValueError(f"slot {slot!r} is not free")
        return {"candidate_id": cid, "slot": slot, "status": "proposed"}

    def get_candidate_record(args: dict[str, Any]) -> dict[str, Any]:
        cid = str(args.get("candidate_id", ""))
        return {"candidate_id": cid, **crm.candidate(cid)}

    def write_interview_note(args: dict[str, Any]) -> dict[str, str]:
        cid = str(args.get("candidate_id", ""))
        note = str(args.get("note", "")).strip()
        assessment = str(args.get("assessment", ""))
        if not note:
            raise ValueError("note must not be empty")
        if assessment not in ASSESSMENTS:
            raise ValueError(f"assessment must be one of {', '.join(ASSESSMENTS)}")
        return {"candidate_id": cid, **crm.add_note(cid, note, assessment)}

    candidate_id = "Candidate id, for example c-001"
    return ToolRegistry(
        [
            ToolServer(
                name="screening",
                description="Candidate screening against the job description.",
                capabilities=("screening", "job criteria", "candidate assessment"),
                tools=(
                    Tool(
                        "get_job_criteria",
                        "Read the screening criteria for a position.",
                        EVERYONE,
                        get_job_criteria,
                        fields_schema(position="Position slug, for example ceo"),
                    ),
                    Tool(
                        "get_candidate_profile",
                        "Read a candidate's profile summary.",
                        EVERYONE,
                        get_candidate_profile,
                        fields_schema(candidate_id=candidate_id),
                    ),
                ),
            ),
            ToolServer(
                name="scheduling",
                description="Interview slots and appointment proposals.",
                capabilities=("scheduling", "calendar", "appointments"),
                tools=(
                    Tool(
                        "list_free_slots",
                        "List free interview slots.",
                        EVERYONE,
                        list_free_slots,
                    ),
                    Tool(
                        "propose_appointment",
                        "Propose a slot for a candidate. Does not book.",
                        EVERYONE,
                        propose_appointment,
                        fields_schema(
                            candidate_id=candidate_id,
                            slot="A free slot from list_free_slots",
                        ),
                    ),
                ),
            ),
            ToolServer(
                name="crm",
                description="Candidate records and interview notes in the CRM.",
                capabilities=("crm", "candidate records", "interview notes"),
                tools=(
                    Tool(
                        "get_candidate_record",
                        "Read a candidate record with notes.",
                        MANAGER_ONLY,
                        get_candidate_record,
                        fields_schema(candidate_id=candidate_id),
                    ),
                    Tool(
                        "write_interview_note",
                        "Write an interview note and assessment.",
                        MANAGER_ONLY,
                        write_interview_note,
                        fields_schema(
                            candidate_id=candidate_id,
                            note="The interview note text",
                            assessment=f"One of {', '.join(ASSESSMENTS)}",
                        ),
                    ),
                ),
            ),
        ]
    )
