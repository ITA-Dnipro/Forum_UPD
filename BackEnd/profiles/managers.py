from django.db import models
from django.utils.timezone import now


class ProfileManager(models.QuerySet):
    def active_only(self):
        return self.filter(is_deleted=False, person__is_active=True)
    

    def soft_delete(self, user):
        self.is_deleted = True
        self.save()
        user.is_active = False
        user.email = (
            f"is_deleted_{now().strftime('%Y%m%d%H%M%S')}_{user.email}"
        )
        user.save()
