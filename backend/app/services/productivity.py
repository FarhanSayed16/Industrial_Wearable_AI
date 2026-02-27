"""
Industrial Wearable AI — Productivity Scoring Service

Computes a composite productivity score (0–100) per session:
  score = 0.5 × active_ratio + 0.2 × consistency + 0.2 × (1 - risk_ratio) + 0.1 × (1 - break_excess)

Used by the analytics dashboard and worker profile pages.
"""


def compute_productivity_score(
    active_pct: float | None,
    idle_pct: float | None,
    adjusting_pct: float | None,
    error_pct: float | None,
    alert_count: int,
    session_duration_minutes: float = 60.0,
) -> float:
    """
    Compute a 0–100 productivity score for a session.

    Parameters:
        active_pct: Percentage of time in 'sewing' state (0–100)
        idle_pct: Percentage of time idle (0–100)
        adjusting_pct: Percentage of time adjusting (0–100)
        error_pct: Percentage of time in error state (0–100)
        alert_count: Number of risk alerts in the session
        session_duration_minutes: Duration of session in minutes

    Returns:
        Float 0–100 representing overall productivity.
    """
    # Normalize inputs
    active = (active_pct or 0) / 100.0
    idle = (idle_pct or 0) / 100.0
    adjusting = (adjusting_pct or 0) / 100.0
    error = (error_pct or 0) / 100.0

    # 1. Active ratio (50% weight) — sewing + adjusting counts as productive
    active_ratio = min(1.0, active + adjusting * 0.5)

    # 2. Consistency (20% weight) — lower variance in state is better
    #    If mostly one state, consistency is high
    distribution = [active, idle, adjusting, error]
    total = sum(distribution)
    if total > 0:
        normalized = [d / total for d in distribution]
        # Entropy-based: lower entropy = more consistent
        import math
        entropy = -sum(p * math.log(p + 1e-10) for p in normalized)
        max_entropy = math.log(len(distribution))
        consistency = 1.0 - (entropy / max_entropy)
    else:
        consistency = 0.0

    # 3. Risk penalty (20% weight) — fewer alerts is better
    alerts_per_hour = alert_count / max(session_duration_minutes / 60.0, 0.1)
    risk_ratio = min(1.0, alerts_per_hour / 10.0)  # 10+ alerts/hr → max penalty

    # 4. Break excess penalty (10% weight)
    #    Reasonable break: ~10% of shift. Penalize if > 20%
    break_time = idle  # Approximate breaks as idle time beyond normal
    break_excess = max(0.0, break_time - 0.15) / 0.85  # Penalize idle > 15%
    break_excess = min(1.0, break_excess)

    # Weighted score
    score = (
        0.50 * active_ratio +
        0.20 * consistency +
        0.20 * (1.0 - risk_ratio) +
        0.10 * (1.0 - break_excess)
    ) * 100.0

    return round(max(0.0, min(100.0, score)), 1)


def score_to_grade(score: float) -> str:
    """Convert productivity score to a letter grade."""
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score_to_color(score: float) -> str:
    """Return a CSS-friendly color for the score."""
    if score >= 70:
        return "#22c55e"  # green
    if score >= 40:
        return "#f59e0b"  # amber
    return "#ef4444"      # red
