import tensorflow as tf
from tensorflow.keras import layers, models
import os

data_dir = "models/cropnet/plant_disease_model"

img_size = (128, 128)
batch_size = 16

dataset = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    image_size=img_size,
    batch_size=batch_size
)

class_names = dataset.class_names
print("Classes:", class_names)

model = models.Sequential([
    layers.Rescaling(1./255, input_shape=(128, 128, 3)),
    layers.Conv2D(32, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(dataset, epochs=3)

os.makedirs("models/cropnet", exist_ok=True)
model.save("models/cropnet/plant_disease_model.h5")

print("CropNet model trained and saved.")