import os
import torch
import torchvision.transforms.functional as TVF
from PIL import Image
from transformers import AutoTokenizer, LlavaForConditionalGeneration


IMAGE_PATH = "../img"
DATASET_PATH = "../dataset"

PROMPT = """
Write a long description of the image.
"""
MODEL_NAME = "fancyfeast/llama-joycaption-alpha-two-hf-llava"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
llava_model = LlavaForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype="bfloat16", device_map=0)
llava_model.eval()

def process_image(image_path, dataset_path):
    with torch.no_grad():
        image = Image.open(image_path)

        if image.size != (384, 384):
            image = image.resize((384, 384), Image.LANCZOS)

        image = image.convert("RGB")
        pixel_values = TVF.pil_to_tensor(image)

        pixel_values = pixel_values / 255.0
        pixel_values = TVF.normalize(pixel_values, [0.5], [0.5])
        pixel_values = pixel_values.to(torch.bfloat16).unsqueeze(0)

        convo = [
            {
                "role": "system",
                "content": "You are a helpful image captioner.",
            },
            {
                "role": "user",
                "content": PROMPT,
            },
        ]

        convo_string = tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=True)
        convo_tokens = tokenizer.encode(convo_string, add_special_tokens=False, truncation=False)

        input_tokens = []
        for token in convo_tokens:
            if token == llava_model.config.image_token_index:
                input_tokens.extend([llava_model.config.image_token_index] * llava_model.config.image_seq_length)
            else:
                input_tokens.append(token)

        input_ids = torch.tensor(input_tokens, dtype=torch.long).unsqueeze(0)
        attention_mask = torch.ones_like(input_ids)

        generate_ids = llava_model.generate(input_ids=input_ids.to('cuda'), pixel_values=pixel_values.to('cuda'), attention_mask=attention_mask.to('cuda'), max_new_tokens=512, do_sample=True, suppress_tokens=None, use_cache=True)[0]
        generate_ids = generate_ids[input_ids.shape[1]:]

        caption = tokenizer.decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        caption = caption.strip()

        return caption

def process_images_in_directory(img_dir, dataset_dir):
    for root, dirs, files in os.walk(img_dir):
        relative_path = os.path.relpath(root, img_dir)
        dataset_root = os.path.join(dataset_dir, relative_path)
        os.makedirs(dataset_root, exist_ok=True)

        for file_name in files:
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file_name)

                caption = process_image(image_path, dataset_root)

                new_image_path = os.path.join(dataset_root, file_name)
                image = Image.open(image_path)
                image.save(new_image_path)

                caption_file = os.path.join(dataset_root, f"{os.path.splitext(file_name)[0]}.txt")
                with open(caption_file, "w") as f:
                    f.write(caption)

                print(f"Processed {file_name}, caption saved as {caption_file}")

process_images_in_directory(IMAGE_PATH, DATASET_PATH)
