"""
Train a chest X-ray classifier using Kaggle's chest-xray-pneumonia dataset.
EfficientNetB3 Version (Higher Accuracy)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = (300, 300)   # EfficientNetB3 works best with 300x300
BATCH_SIZE = 16        # Reduced due to larger model


# =====================================
# Build Model (EfficientNetB3 + ReLU)
# =====================================
def build_model(num_classes: int) -> tuple[tf.keras.Model, tf.keras.Model]:

    base = tf.keras.applications.EfficientNetB3(
        include_top=False,
        weights="imagenet",
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
    )
    base.trainable = False

    inputs = layers.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3))

    # EfficientNet preprocessing
    x = tf.keras.applications.efficientnet.preprocess_input(inputs)

    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)

    # 🔥 Stronger classifier head
    x = layers.Dense(512, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    

    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model, base


# =====================================
# Fine-Tuning
# =====================================
def unfreeze_for_finetune(base_model: tf.keras.Model, unfreeze_layers: int) -> None:

    if unfreeze_layers <= 0:
        return

    base_model.trainable = True

    for layer in base_model.layers[:-unfreeze_layers]:
        layer.trainable = False

    for layer in base_model.layers[-unfreeze_layers:]:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False


# =====================================
# Data Generators
# =====================================
def create_generators(dataset_root: Path):

    chest_root = dataset_root / "chest_xray"
    train_dir = chest_root / "train"
    val_dir = chest_root / "val"
    test_dir = chest_root / "test"

    train_aug = ImageDataGenerator(
        rescale=1 / 255.0,
        rotation_range=15,
        zoom_range=0.25,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        brightness_range=(0.8, 1.2),
        horizontal_flip=True,
    )

    val_aug = ImageDataGenerator(rescale=1 / 255.0)

    train_gen = train_aug.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        class_mode="categorical",
        batch_size=BATCH_SIZE,
    )

    val_gen = val_aug.flow_from_directory(
        val_dir,
        target_size=IMG_SIZE,
        class_mode="categorical",
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    test_gen = val_aug.flow_from_directory(
        test_dir,
        target_size=IMG_SIZE,
        class_mode="categorical",
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    return train_gen, val_gen, test_gen


# =====================================
# Main
# =====================================
def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="/kaggle/input/chest-xray-pneumonia")
    parser.add_argument("--output", default="cnn_model/medxai_model.h5")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--fine-tune-epochs", type=int, default=15)
    parser.add_argument("--unfreeze-layers", type=int, default=80)

    args = parser.parse_args()

    dataset_root = Path(args.dataset)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    train_gen, val_gen, test_gen = create_generators(dataset_root)
    model, base_model = build_model(num_classes=train_gen.num_classes)

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-6),
        ModelCheckpoint(str(output_path), monitor="val_accuracy", save_best_only=True),
    ]

    print("[Phase 1] Training classifier head...")
    model.fit(train_gen, validation_data=val_gen, epochs=args.epochs, callbacks=callbacks)

    print("[Phase 2] Fine-tuning...")
    unfreeze_for_finetune(base_model, args.unfreeze_layers)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=args.fine_tune_epochs,
        callbacks=callbacks,
    )

    loss, acc = model.evaluate(test_gen)
    print(f"Test accuracy: {acc:.4f}, loss: {loss:.4f}")

    model.save(output_path)
    print(f"Saved model to: {output_path.resolve()}")


if __name__ == "__main__":
    main()