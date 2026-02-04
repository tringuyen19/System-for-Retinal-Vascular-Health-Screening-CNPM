import cv2
import numpy as np

def preprocess_image(file, target_size=(224, 224)):
    # read bytes → numpy
    image_bytes = file.file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)

    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = cv2.resize(img, target_size)
    img = img / 255.0

    img = np.expand_dims(img, axis=0)
    return img
