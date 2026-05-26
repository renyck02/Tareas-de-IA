from datasets import load_dataset
from transformers import ViTImageProcessor, ViTForImageClassification, TrainingArguments, Trainer
import torch
import warnings

warnings.filterwarnings("ignore")

def entrenar_modelo_personalizado():
    print("1. Cargando las imágenes de tu dataset de Rocket League...")
    # Carga las carpetas automáticamente y les asigna etiquetas
    dataset = load_dataset("imagefolder", data_dir="datasets_rocket_league", split="train")
    
    etiquetas = dataset.features["label"].names
    id2label = {str(i): label for i, label in enumerate(etiquetas)}
    label2id = {label: str(i) for i, label in enumerate(etiquetas)}
    
    print(f"   Etiquetas detectadas: {etiquetas}")

    print("\n2. Descargando el cerebro base de Hugging Face (ViT)...")
    # Usamos in21k porque es la mejor versión para hacer fine-tuning
    procesador = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
    
    # Configuramos el modelo con tu número exacto de categorías
    modelo = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224-in21k",
        num_labels=len(etiquetas),
        id2label=id2label,
        label2id=label2id
    )

    print("\n3. Preparando las imágenes para la red neuronal...")
    def transformar_imagenes(batch):
        # Convierte las fotos al tamaño y formato matemático que exige ViT
        inputs = procesador([x.convert("RGB") for x in batch["image"]], return_tensors="pt")
        inputs["labels"] = batch["label"]
        return inputs

    dataset_preparado = dataset.with_transform(transformar_imagenes)

    print("\n4. Configurando el motor de entrenamiento...")
    argumentos_entrenamiento = TrainingArguments(
        output_dir="./resultados_entrenamiento",
        per_device_train_batch_size=4, # Pequeño para no saturar la memoria de ferhp9
        num_train_epochs=5,            # 5 pasadas completas sobre tus fotos
        logging_steps=10,
        save_strategy="no",            # No guardar puntos intermedios para ahorrar disco
        remove_unused_columns=False
    )

    entrenador = Trainer(
        model=modelo,
        args=argumentos_entrenamiento,
        train_dataset=dataset_preparado,
    )

    print("\n🔥 ¡INICIANDO EL ENTRENAMIENTO! (Esto puede tardar unos minutos)...")
    entrenador.train()

    print("\n5. ¡Entrenamiento terminado! Guardando tu modelo personalizado...")
    # Guardamos el modelo final en una carpeta de tu proyecto
    modelo.save_pretrained("./mi_vit_rocket_league")
    procesador.save_pretrained("./mi_vit_rocket_league")
    
    print("======================================================")
    print("✅ ¡ÉXITO! Tu modelo IA está listo en la carpeta 'mi_vit_rocket_league'")
    print("======================================================")

if __name__ == "__main__":
    entrenar_modelo_personalizado()