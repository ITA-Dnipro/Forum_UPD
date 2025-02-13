from django.db import models
import logging

logger = logging.getLogger(__name__)

class ProfileManager(models.QuerySet):
    def active_only(self):
        return self.filter(is_deleted=False, person__is_active=True)
    def create(self, **kwargs):
        profile = super().create(**kwargs)
        logger.info(f"New profile {profile.name} (ID: {profile.pk}) was created.")
        return profile

    def delete(self, **kwargs):
        logger.info(f"Profile {kwargs.get('name')} is being deleted.")
        super().delete(**kwargs)