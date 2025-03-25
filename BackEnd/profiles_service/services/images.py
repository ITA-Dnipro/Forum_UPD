import os
from pathlib import Path
import uuid
from utils.repositories import BaseRepository


class ImageService:

    IMAGE_BASE_PATH = "static/media/startups"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


    def __init__(self, repo: BaseRepository):
        self.repository = repo

    
    def _create_storage_path(self, file_ext):
        base_dir = Path(self.IMAGE_BASE_PATH)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{uuid.uuid4().hex}.{file_ext}"
        return base_dir / filename


    async def add_image(self, file):

        file_ext = file.filename.split('.')[-1]

        if file_ext not in self.ALLOWED_EXTENSIONS:
            ValueError(f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSION)}")

        path = self._create_storage_path(file_ext)
        try:
            contents = file.file.read()
            with open(path, 'wb') as f:
                f.write(contents)
        except Exception as e:
            print("\n")
            print(e)
            print("\n")
            raise Exception('Something went wrong')
        finally:
            file.file.close()

        image_dict = {}
        image_dict["image_path"] = str(path)
        return await self.repository.add_one(image_dict)

