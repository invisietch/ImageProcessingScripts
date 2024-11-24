import os
import cv2
import numpy as np
import math

RESOLUTIONS = [
    (1024, 1024),
    (1216, 832),
    (832, 1216),
    (768, 768),
    (912, 624), 
    (624, 912),
    (512, 512),
    (608, 416),
    (416, 608),
]

def get_focal_point(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    moments = cv2.moments(edges)
    if moments["m00"] == 0:
        return "center", "center" 

    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])

    horizontal = "left" if cx < image.shape[1] // 3 else ("right" if cx > 2 * image.shape[1] // 3 else "center")
    vertical = "top" if cy < image.shape[0] // 3 else ("bottom" if cy > 2 * image.shape[0] // 3 else "center")
    
    return horizontal, vertical

def resize_image(image, resolution):
    h, w = image.shape[:2]
    pixels = h * w

    resolution_width, resolution_height = resolution

    if w / h > resolution_width / resolution_height:
        new_width = resolution_width
        new_height = int(h * resolution_width / w)
    else:
        new_height = resolution_height
        new_width = int(w * resolution_height / h)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    return resized_image

def crop_image(image, focal_point, resolution):
    h, w = image.shape[:2]
    res_w, res_h = resolution
    
    target_aspect_ratio = res_w / res_h

    image_aspect_ratio = w / h

    def center_crop(x1, y1, x2, y2):
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        return image[y1:y2, x1:x2]

    if image_aspect_ratio == target_aspect_ratio:
        return image
    
    if image_aspect_ratio > target_aspect_ratio:
        new_width = int(h * target_aspect_ratio)
        crop_x1 = (w - new_width) // 2
        
        if focal_point[0] == "left":
            crop_x1 = 0
        elif focal_point[0] == "right":
            crop_x1 = w - new_width
        
        crop_x2 = crop_x1 + new_width
        return center_crop(crop_x1, 0, crop_x2, h)

    elif image_aspect_ratio < target_aspect_ratio:
        new_height = int(w / target_aspect_ratio)
        crop_y1 = (h - new_height) // 2
        
        if focal_point[1] == "top":
            crop_y1 = 0
        elif focal_point[1] == "bottom":
            crop_y1 = h - new_height
        
        crop_y2 = crop_y1 + new_height
        return center_crop(0, crop_y1, w, crop_y2)

    else:
        return image


def save_image(image, resolution, idx):
    resolution_folder = f"../img/{resolution[0]}x{resolution[1]}"
    
    if not os.path.exists(resolution_folder):
        os.makedirs(resolution_folder)

    filename = f"{resolution_folder}/{idx}.png"
    cv2.imwrite(filename, image)

def select_best_resolution(image):
    h, w = image.shape[:2]
    aspect_ratio = w / h
    aspect_ratios = {
        (1,1): 1, 
        (2,3): 2/3, 
        (3,2): 3/2
    }

    best_aspect_ratio = min(aspect_ratios, key=lambda ratio: abs(aspect_ratios[ratio] - aspect_ratio))

    if best_aspect_ratio == (1, 1):
        if w >= 1024 and h >= 1024:
            return (1024, 1024)
        elif w >= 768 and h >= 768:
            return (768, 768)
        else:
            return (512, 512)
    elif best_aspect_ratio == (3, 2):
        if w >= 1216 and h >= 832:
            return (1216, 832)
        elif w >= 912 and h >= 624:
            return (912, 624)
        else:
            return (608, 416)
    else:
        if w >= 832 and h >= 1216:
            return (832, 1216)
        elif w >= 624 and h >= 912:
            return (624, 912)
        else:
            return (416, 608)

def process_images():
    raw_dir = '../raw'
    image_files = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    img_counter = {}

    for image_file in image_files:
        image_path = os.path.join(raw_dir, image_file)
        image = cv2.imread(image_path)

        focal_point = get_focal_point(image)
        best_resolution = select_best_resolution(image)

        cropped_image = crop_image(image, focal_point, best_resolution)
        resized_image = resize_image(cropped_image, best_resolution)

        if best_resolution not in img_counter:
            img_counter[best_resolution] = 0

        save_image(resized_image, best_resolution, img_counter[best_resolution])
        img_counter[best_resolution] += 1

if __name__ == "__main__":
    process_images()
