"""Deterministic oracle for the Markdown-owned design governance contract."""


def classify_design(
    *,
    existing_seam=None,
    coherent_outcome=None,
    new_subsystem=None,
    new_public_interface_shape=None,
    cross_context_consistency_rule=None,
    unresolved_load_bearing_architecture=None,
):
    """Classify as bounded only when every required fact is explicit."""

    bounded_facts = (existing_seam, coherent_outcome)
    architectural_facts = (
        new_subsystem,
        new_public_interface_shape,
        cross_context_consistency_rule,
        unresolved_load_bearing_architecture,
    )
    if not all(value is True for value in bounded_facts):
        return "architectural"
    if not all(value is False for value in architectural_facts):
        return "architectural"
    return "bounded"


def initial_design_review(
    *, mode, classification=None, grounded_recommendations=0
):
    """Select the first review without granting authority to later stages."""

    if mode == "autonomous":
        return (
            "autonomous-grounded-recommendation"
            if grounded_recommendations == 1
            else "stop-no-unique-grounded-recommendation"
        )
    if mode != "interactive":
        raise ValueError("unknown design mode")
    if classification == "bounded":
        return "bounded-gate-1"
    return "architectural-alternative-selection"


def bounded_gate_1_transition(choice):
    """Map a bounded Gate 1 choice without widening its authority."""

    transitions = {
        "recommended": "workspace-preparation-then-gate-2",
        "nonrecommended": "design-elaboration-then-gate-1",
        "reject": "stop",
    }
    try:
        return transitions[choice]
    except (KeyError, TypeError) as error:
        raise ValueError("unknown bounded Gate 1 choice") from error
