import tensorflow as tf
import numpy as np
import cv2

# load model once
vessel_model = tf.keras.models.load_model(
    "models/seg.h5",
    compile=False
)

def vessel_segmentation(image):
    """
    image: (1, H, W, 3)
    """
    pred = vessel_model.predict(image)[0]

    # binary mask
    vessel_mask = (pred > 0.5).astype("uint8")

    vessel_ratio = float(np.sum(vessel_mask) / vessel_mask.size)

    # heatmap
    heatmap = cv2.applyColorMap(
        (pred * 255).astype("uint8"),
        cv2.COLORMAP_JET
    )

    return vessel_mask, vessel_ratio, heatmap
