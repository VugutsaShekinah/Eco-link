"""
rewards/services.py — the redemption business rule in one testable place.

Redeeming must be safe against double-spending: if a user double-clicks or two
requests arrive at once, they must not be able to redeem more points than they
hold. We do the check-and-deduct inside a single DB transaction, locking the
user's row with select_for_update() so concurrent redemptions run one at a time.
"""

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Redemption, Reward


class RewardUnavailableError(Exception):
    """Raised when a reward is not active / not redeemable."""


class InsufficientPointsError(Exception):
    """Raised when the user's balance is below the reward's cost."""


@transaction.atomic
def redeem(user, reward: Reward) -> Redemption:
    """
    Redeem `reward` for `user`. Returns the Redemption on success, or raises
    RewardUnavailableError / InsufficientPointsError.

    The user row is locked for the duration so the balance check and the
    deduction cannot interleave with another redemption.
    """
    if not reward.is_active:
        raise RewardUnavailableError("This reward is no longer available.")

    User = get_user_model()
    # Lock this user's row until the transaction commits.
    locked_user = User.objects.select_for_update().get(pk=user.pk)

    if locked_user.eco_points_balance < reward.points_required:
        raise InsufficientPointsError("You do not have enough eco-points.")

    locked_user.eco_points_balance -= reward.points_required
    locked_user.save(update_fields=["eco_points_balance"])

    redemption = Redemption.objects.create(
        user=locked_user,
        reward=reward,
        points_spent=reward.points_required,
    )

    # Keep the caller's in-memory user object consistent with the DB.
    user.eco_points_balance = locked_user.eco_points_balance
    return redemption
