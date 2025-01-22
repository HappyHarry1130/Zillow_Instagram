

# # DyFimC9t@9cKJ?78
# bot.login(username = "longislandlender", 
#           password = "DyFimC9t@9cKJ?78")
 
from instagrapi import Client

def upload_to_instagram(username, password, image_path, caption):
    # Initialize the client
    cl = Client()

    # Log in to your Instagram account
    cl.login(username, password)

    # Upload the photo with a caption
    media = cl.photo_upload(image_path, caption)
    print(f"Uploaded successfully! Media ID: {media.pk}")

if __name__ == "__main__":
    USERNAME = "longislandlender"
    PASSWORD = "DyFimC9t@9cKJ?78"
    IMAGE_PATH = "1.png"
    CAPTION = "here"

    upload_to_instagram(USERNAME, PASSWORD, IMAGE_PATH, CAPTION)
