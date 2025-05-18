import os
import base64


def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def get_vlm_images(folder_path, nb_images=1, symbol_split="-"):
    """
    Get the images needed for the VLM in base64 from the folder_path
    """
    subdir = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    
    subdir.sort(key=lambda x: int(x.split(symbol_split)[-1]))
    if len(subdir) == 0:
        return []
    if len(subdir) == 1:
        dir_name = subdir[0]
    else:
        dir_name = subdir[-2]

    # print(f"Using images from {dir_name}")
    
    images = []
    for filename in os.listdir(os.path.join(folder_path, dir_name)):
        if filename.endswith(".png") and filename.split(symbol_split)[-1].split('.')[0].isdigit():
            images.append(os.path.join(folder_path, dir_name, filename))

    if len(images) == 0:
        print(f"No images found in {folder_path}")
        return []
    
    images.sort(key=lambda x: int(x.split(os.sep)[-1].split(symbol_split)[-1].split('.')[0]))
    
    if nb_images == 1:
        return [convert_image_to_base64(images[-1])]
    else:
        if nb_images > len(images):
            nb_images = len(images)
        
        images_to_return = []
        images_to_return.append(convert_image_to_base64(images[0]))

        for i in range(1, nb_images - 1):
            images_to_return.append(convert_image_to_base64(images[int(i * len(images) / (nb_images - 1))]))

        images_to_return.append(convert_image_to_base64(images[-1]))
        return images_to_return


def format_api_query(image, ollama=False):
    """
    Format the image for the API query
    """
    if ollama:
        return {
            "type": "image_url",
            "image_url": f"data:image/png;base64,{image}"
        }
    else:
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image}",
                        "detail": "high"}
        }


if __name__ == '__main__':
    # test
    folder_path="voyager/env/mineflayer/runs"
    images = get_vlm_images(folder_path, nb_images=3)
    for image in images:
        print(type(image))