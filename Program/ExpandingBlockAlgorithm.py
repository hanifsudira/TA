import cv2
import numpy as np
import time
from sklearn.feature_extraction import image

class ExpandingBlockAlgorithm():
    def __init__(self,myImage,blockSize):
        self.blockSize = blockSize
        try:
            self.myImage = cv2.imread(myImage)
            self.height, self.width, self.channel = self.myImage.shape
            #toGrayScaleImage
            self.grayScaleImage = self.rgbToGrayScale(self.myImage).astype(np.uint8)
        except:
            print "Tidak Dapat Membuka Gambar"

    def rgbToGrayScale(self,rgb):
        return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

    def expandingBlockAlgorithm(self):
        #make overlapping blok
        self.overLappingBlock = image.extract_patches_2d(self.grayScaleImage,(self.blockSize,self.blockSize))
        self.sizeOverLappingBlock = self.overLappingBlock.shape[0]

        #calculation mean or average grayscale
        self.arrayCalculation = np.zeros((self.sizeOverLappingBlock,3),dtype=object)
        for i in range(self.sizeOverLappingBlock):
            meanEachBlock = self.overLappingBlock[i].mean()
            self.arrayCalculation[i] = [i,meanEachBlock,self.overLappingBlock[i]]

        #sort based on dominant feature (mean)
        self.arrayCalculation = sorted(self.arrayCalculation, key=lambda value:value[1])
        print len(self.arrayCalculation)

if __name__ == '__main__':
    startTime = time.time()
    Run = ExpandingBlockAlgorithm("im2_t.bmp",32)
    Run.expandingBlockAlgorithm()
    endTime = time.time()
    print "Proccess Time : " + str(endTime - startTime)