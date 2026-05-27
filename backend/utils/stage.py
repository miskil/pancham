def derive_stage_and_substatus(internal_status: str) -> tuple[str, str]:
    PROPOSAL_STATES = {
        "CREATED": "Not yet submitted",
        "PROPOSAL_SUBMITTED": "Submitted — awaiting review",
        "UNDER_REVIEW": "Under review",
        "AMENDMENT_REQUESTED": "Amendment requested",
        "AMENDED": "Amendment submitted — awaiting review",
    }
    PLAN_STATES = {
        "ACCEPTED": "Proposal accepted — plan required",
        "PLAN_SUBMITTED": "Plan submitted — awaiting review",
        "PLAN_REVIEW": "Plan under review",
        "PLAN_ACCEPTED": "Plan accepted — WIP active",
        "BASELINE_FROZEN": "Baseline frozen, WIP active",
    }
    ACTIVE_STATES = {
        "YEAR_1": "Year 1 of 3",
        "YEAR_2": "Year 2 of 3",
        "YEAR_3": "Year 3 of 3",
    }
    if internal_status in PROPOSAL_STATES:
        return "PROPOSAL", PROPOSAL_STATES[internal_status]
    if internal_status in PLAN_STATES:
        return "PLAN", PLAN_STATES[internal_status]
    if internal_status in ACTIVE_STATES:
        return "ACTIVE", ACTIVE_STATES[internal_status]
    return "COMPLETED", "Programme completed"
