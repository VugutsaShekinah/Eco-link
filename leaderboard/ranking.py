"""
leaderboard/ranking.py — one place that computes a participant's rank.

Reused by both the leaderboard page and the user dashboard, so "your rank"
means the same thing everywhere.
"""

from accounts.models import User


def participant_rank(user):
    """
    1-based competition rank among participants (admins excluded).

    Returns None for administrators, who don't appear in the rankings.
    Rank = (number of participants with strictly more points) + 1, so ties
    share the same rank.
    """
    if user.is_administrator:
        return None
    ahead = (
        User.objects.exclude(role=User.Role.ADMIN)
        .filter(eco_points_balance__gt=user.eco_points_balance)
        .count()
    )
    return ahead + 1
