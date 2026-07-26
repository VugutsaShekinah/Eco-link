"""
rewards/views.py — browse the catalogue, redeem, and view redemption history.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Reward
from .services import (
    InsufficientPointsError,
    RewardUnavailableError,
    redeem,
)


@login_required
def reward_list(request):
    """Show active rewards and whether the user can currently afford each."""
    rewards = Reward.objects.filter(is_active=True)
    return render(
        request,
        "rewards/reward_list.html",
        {"rewards": rewards, "balance": request.user.eco_points_balance},
    )


@login_required
@require_POST
def redeem_reward(request, pk):
    """Redeem a reward (POST only). Deducts points via the service layer."""
    reward = get_object_or_404(Reward, pk=pk)
    try:
        redemption = redeem(request.user, reward)
    except RewardUnavailableError as exc:
        messages.error(request, str(exc))
    except InsufficientPointsError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            f"Success! You redeemed “{reward.name}” for {redemption.points_spent} eco-points.",
        )
    return redirect("reward_list")


@login_required
def my_redemptions(request):
    """The current user's redemption history."""
    redemptions = request.user.redemptions.select_related("reward").all()
    return render(request, "rewards/my_redemptions.html", {"redemptions": redemptions})
