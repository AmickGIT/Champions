from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile storing balance, fantasy points, and admin status.
    Automatically created via signal when a new User is registered.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=10000000
    )  # 10M starting balance
    total_points = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-total_points"]
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return (
            f"{self.user.username} - Balance: {self.balance} "
            f"- Points: {self.total_points}"
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile automatically when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """Save the UserProfile whenever the User is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
