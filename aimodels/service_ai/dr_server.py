import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB1

NUM_CLASSES = 5

# rebuild architecture
dr_model = EfficientNetB1(
    include_top=True,
    weights=None,
    classes=NUM_CLASSES,
    input_shape=(224, 224, 3)
)

# load trained weights
dr_model.load_weights(
    "models/efficientnetb1_weights.h5",
    by_name=True,
    skip_mismatch=True
)

def dr_classification(image):
    """
    image: (1, 224, 224, 3)
    """
    preds = dr_model.predict(image)[0]

    dr_stage = int(np.argmax(preds))
    dr_probability = float(np.max(preds))

    return dr_stage, dr_probability
