import requests
import shutil
import cv2
import os
from pyagender import PyAgender

from time import sleep

agender = PyAgender()
url = "https://thispersondoesnotexist.com/"
temp_file = "temp_img.jpg"
cnt = 200
sleep_time = 0.3


def get_face():
    response = requests.get(url, stream=True)
    with open(temp_file, 'wb') as f:
        f.write(response.content)


# 3 genders??????
def recognise_face():
    faces = agender.detect_genders_ages(cv2.imread(temp_file))
    if len(faces) == 1:
        face = faces[0]
        gender_numeric = face['gender']
        age = int(face['age'])

        gender = 0
        if gender_numeric < 0.4:
            gender = 1  # male
        elif gender_numeric > 0.6:
            gender = 2  # female
    else:
        gender = 0
        age = 0

    return gender, age


def save(n):
    if not os.path.isdir('skufs'):
        os.mkdir('skufs')

    shutil.move(temp_file, f'skufs/{n}.jpg')
    print('# Saved!')


def main():
    n = 0
    while n < cnt:
        get_face()
        gender, age = recognise_face()
        if gender != 0:
            print(f'{age} year old {gender}')
            if age > 40 and gender == 1:
                n += 1
                save(n)
        else:
            print("Unclear gender")
        sleep(sleep_time)


if __name__ == '__main__':
    main()
