import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = "dmidkmbyp",
  api_key = "256857942333283",
  api_secret = "dEV8dxWyWpCClSgv9F8ikse1abQ"
)

result = cloudinary.uploader.upload(
    "retina.jpg",
    folder="retina_input"
)

print(result["secure_url"])
