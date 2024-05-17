import cv2 as cv
import os


class Armorer:
    def __init__(self, items):
        for i in items:
            pass
        set = items[0].split(' ')[0]

        folder = '../graphics/temp_player/'
        sub_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
        print(sub_folders)

        # get all the sub folders

        # self.image = self.equip_armor(items, set)

    def equip_armor(self, base_path, modif_path, items, set):
        img1 = cv.imread(base_path, cv.IMREAD_UNCHANGED)
        for i in items:
            img2 = cv.imread(modif_path, cv.IMREAD_UNCHANGED)
            rows, cols, channels = img2.shape
            roi = img1[0:rows, 0:cols]
            img2gray = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
            _, mask = cv.threshold(img2gray, 0, 255, cv.THRESH_BINARY)
            mask_inv = cv.bitwise_not(mask)
            img1_bg = cv.bitwise_and(roi, roi, mask=mask_inv)
            img2_fg = cv.bitwise_and(img2, img2, mask=mask)
            dst = cv.add(img1_bg, img2_fg)
            img1[0:rows, 0:cols] = dst

        return img1


arm = Armorer(['brigand armor', 'brigand hood'])
arm2 = Armorer(['bandit body'])
cv.imshow('self.image1', arm.image)
cv.imshow('self.image2', arm2.image)
cv.waitKey(0)