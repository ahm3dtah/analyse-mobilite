import os
import torch
from PIL import Image

# 1. Détection automatique du matériel et choix de la stratégie
if torch.cuda.is_available():
    device = "cuda"
    model_type = "blip2"
    dtype = torch.float16
elif torch.backends.mps.is_available():
    device = "mps"
    model_type = "blip2"
    dtype = torch.float16
else:
    device = "cpu"
    model_type = "clip"
    dtype = torch.float32

print(f"⚙️ Appareil : {device.upper()} | Modèle sélectionné : {model_type.upper()}")

# 2. Chargement conditionnel du modèle et du processeur
if model_type == "blip2":
    from transformers import Blip2Processor, Blip2ForConditionalGeneration
    
    model_name = "Salesforce/blip2-opt-2.7b" #
    print(f"Chargement de BLIP-2 ({model_name}) sur {device} en float16...")
    processor = Blip2Processor.from_pretrained(model_name)
    model = Blip2ForConditionalGeneration.from_pretrained(
        model_name, 
        torch_dtype=dtype,
        low_cpu_mem_usage=True
    ).to(device)
    model.eval()

else:
    from transformers import CLIPProcessor, CLIPModel
    
    model_name = "openai/clip-vit-base-patch32"
    print(f"Chargement de CLIP ({model_name}) sur CPU...")
    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name).to(device)
    model.eval()

# 3. Fonction de filtrage hybride
import os
import shutil
import torch
from PIL import Image

# ... [garder le bloc d'initialisation du modèle CLIP / BLIP-2] ...

def filter_and_save_images(input_dir, output_dir="./images_valides"):
    # Création du dossier de destination s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    valid_images = []
    
    if model_type == "blip2":
        prompt = "Question: Is this a street scene viewed from a road? Answer yes or no." #[cite: 6]
    else:
        candidate_labels = [
            "a photo of a street scene viewed from a road with driving traffic", #[cite: 3, 4]
            "a photo of a parking lot or parked cars in a parking zone",           #[cite: 3, 4]
            "an indoor view or non-road perspective"                              #[cite: 3]
        ]

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            
            try:
                raw_image = Image.open(image_path).convert("RGB")
                
                # Evaluation selon le modèle actif
                if model_type == "blip2":
                    inputs = processor(images=raw_image, text=prompt, return_tensors="pt").to(device, dtype)
                    with torch.no_grad():
                        outputs = model.generate(**inputs, max_new_tokens=5)
                    answer = processor.decode(outputs[0], skip_special_tokens=True).strip().lower()
                    is_valid = "yes" in answer
                    log_msg = f"BLIP-2 -> {answer}"
                else:
                    inputs = processor(text=candidate_labels, images=raw_image, return_tensors="pt", padding=True).to(device)
                    with torch.no_grad():
                        outputs = model(**inputs)
                        probs = outputs.logits_per_image.softmax(dim=1)[0]
                    traffic_prob = probs[0].item()
                    parking_prob = probs[1].item()
                    is_valid = (traffic_prob > parking_prob) and (traffic_prob > 0.45)
                    log_msg = f"CLIP -> Score route : {traffic_prob:.2%}"

                # Copie physique de l'image si elle est validée
                if is_valid:
                    dest_path = os.path.join(output_dir, filename)
                    shutil.copy(image_path, dest_path)
                    valid_images.append(dest_path)
                    print(f"✅ {filename} : Conservée et copiée vers {output_dir}")
                else:
                    print(f"❌ {filename} : Rejetée ({log_msg})")
                    
            except Exception as e:
                print(f"⚠️ Erreur avec {filename}: {e}")
                
    return valid_images

# Exécution
dossier_images = r"C:\Users\konan\OneDrive\Bureau\5A-IMDS\Projet Polycompetence\students\students\0rTwCg1mDAHYPkcbp-5MLA"
images_valides = filter_and_save_images(dossier_images, r"C:\Users\konan\OneDrive\Bureau\5A-IMDS\Projet Polycompetence\students\students\images_valides")

print(f"\nFiltrage terminé : {len(images_valides)} images conservées pour le passage sous YOLO.")