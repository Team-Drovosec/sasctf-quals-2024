from PIL import Image
import os

source_dir = 'service/skuf/avatar'
target_dir = 'service/skuf/avatar200'

os.makedirs(target_dir, exist_ok=True)

pid = 1
for filename in os.listdir(source_dir):
    if filename.endswith('.jpg'):
        file_path = os.path.join(source_dir, filename)
        with Image.open(file_path) as img:
            img_r = img.resize((200, 200), Image.ANTIALIAS)
            save_path = os.path.join(target_dir, f'{pid}.jpg')
            img_r.save(save_path)
            pid += 1