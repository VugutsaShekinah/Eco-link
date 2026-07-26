"""
leaderboard/views.py — community leaderboard + impact visualisation (§4.3.5).

Ranks participants by their verified eco-points balance (recalculated live on
each load, so it always matches the underlying data), highlights the viewer's
own row, and shows aggregate impact figures for the whole programme.
"""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from accounts.models import User
from dropoffs.models import DropOff

from .ranking import participant_rank

# Rough average weight of a single plastic item, used only to translate the
# kilograms collected into an approximate, easy-to-grasp "items diverted from
# landfill" figure (report §4.3.5 calls this an *approximate* count). ~20 g.
AVG_ITEM_WEIGHT_KG = Decimal("0.02")


def _impact():
    """Programme-wide impact figures from verified drop-offs only."""
    verified = DropOff.objects.filter(status=DropOff.Status.VERIFIED)
    total_kg = verified.aggregate(t=Sum("weight_kg"))["t"] or Decimal("0")

    items_diverted = int(total_kg / AVG_ITEM_WEIGHT_KG) if total_kg else 0
    return {
        "total_kg": total_kg,
        "items_diverted": items_diverted,
        "verified_dropoffs": verified.count(),
    }


@login_required
def leaderboard(request):
    """Ranked participants + the viewer's own rank + impact figures."""
    # Participants only (administrators are staff, not competitors).
    rankings = (
        User.objects.exclude(role=User.Role.ADMIN)
        .order_by("-eco_points_balance", "date_joined")
    )

    # The viewer's competition rank (None for admins, who aren't ranked).
    my_rank = participant_rank(request.user)

    context = {
        "rankings": rankings,
        "my_rank": my_rank,
        "participant_count": rankings.count(),
    }
    context.update(_impact())
    return render(request, "leaderboard/leaderboard.html", context)
