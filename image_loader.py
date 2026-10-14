import requests
import os
from urllib.parse import quote
from PIL import Image
class ImageLoader:

    def get_image_url(self, title):

        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + title.replace(" ", "_")
        )

        headers = {
            "User-Agent": "SmartSearchAI/1.0"
        }

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()

            if "thumbnail" in data:

                return data["thumbnail"]["source"]

            return None

        except Exception as e:

          print("Image URL Error:", e)

          return None
        
    def create_image_folder(self):

     folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "images"
    )
     
     os.makedirs(folder, exist_ok=True)

     return folder
    
    def get_image_filename(self, title):

     filename = quote(title.replace(" ", "_")) + ".jpg"

     path = os.path.join(
        self.create_image_folder(),
        filename
    )

     

     return path

    
    def load_local_image(self, title):

     image_path = self.get_image_filename(title)

     if os.path.exists(image_path):

        try:
            return Image.open(image_path)

        except Exception as e:
            print("Image Load Error:", e)

     return None
    
    def download_image(self, image_url, title):

     headers = {
        "User-Agent": "SmartSearchAI/1.0"
    }

     response = requests.get(
        image_url,
        headers=headers,
        timeout=10
    )

     if response.status_code != 200:
        return None

     image_path = self.get_image_filename(title)

     with open(image_path, "wb") as file:
        file.write(response.content)

     return image_path