from django.db import models
from django.utils.timezone import now


class ProfileManager(models.QuerySet):
    def active_only(self):
        return self.filter(is_deleted=False, person__is_active=True)
    

