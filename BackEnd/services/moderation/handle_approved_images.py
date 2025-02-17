from utils.completeness_counter import completeness_count
import logging

logger = logging.getLogger(__name__)

class ApprovedImagesDeleter:
    """
    Entity that handles the deletion of approved images if a user deletes an image under moderation.
    """

    def __init__(self, profile):
        self.profile = profile

    def delete_approved_image(self, approved_image):
        if self.profile.status == self.profile.PENDING and approved_image:
            approved_image.is_deleted = True
            approved_image.save()
            logger.info("Approved image was deleted.")
            completeness_count(self.profile)

    def handle_potential_deletion(self):
        if not self.profile.banner:
            self.delete_approved_image(self.profile.banner_approved)

        if not self.profile.logo:
            self.delete_approved_image(self.profile.logo_approved)
