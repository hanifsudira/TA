import cv2
import numpy as np
import scipy
import time
import logging
import traceback
from sklearn.feature_extraction import image
from scipy.stats import chisquare

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
        try:
            #make overlapping blok
            self.overLappingBlock = image.extract_patches_2d(self.grayScaleImage, (self.blockSize, self.blockSize))
            self.sizeOverLappingBlock = self.overLappingBlock.shape[0]

            #print self.overLappingBlock[0]

            #calculation mean or average grayscale
            self.arrayCalculation = np.zeros((self.sizeOverLappingBlock, 3), dtype=object)
            for i in range(self.sizeOverLappingBlock):
                meanEachBlock = self.overLappingBlock[i].mean()
                self.arrayCalculation[i] = [i, meanEachBlock, self.overLappingBlock[i]]

            #sort based on dominant feature (mean)
            self.arrayCalculation = sorted(self.arrayCalculation, key=lambda value: value[1])

            #create group
            midleValueGroup = self.sizeOverLappingBlock / 2
            splitGroup = np.split(self.arrayCalculation, [midleValueGroup])
            bigGroupA = splitGroup[0]
            bigGroupB = splitGroup[1]
            midleValueGroupA = bigGroupA.shape[0] / 2
            splitGroupA = np.split(bigGroupA, [midleValueGroupA])
            midleValueGroupB = bigGroupB.shape[0] / 2
            splitGroupB = np.split(bigGroupB, [midleValueGroupB])
            self.group1 = splitGroupA[0]
            self.group2 = splitGroupA[1]
            self.group3 = splitGroupB[0]
            self.group4 = splitGroupB[1]

            #create bucket
            self.bucket1 = np.concatenate((self.group1, self.group2))
            self.bucket2 = np.concatenate((self.group1, self.group2, self.group3))
            self.bucket3 = np.concatenate((self.group2, self.group3, self.group4))
            self.bucket4 = np.concatenate((self.group3, self.group4))

            self.sizeBucket1 = self.bucket1.shape[0]
            self.sizeBucket2 = self.bucket2.shape[0]
            self.sizeBucket3 = self.bucket3.shape[0]
            self.sizeBucket4 = self.bucket4.shape[0]

            for eachItemOnBucketColumn in range(self.bucket1.shape[0]):
                for eachItemOnBucketRow in range(eachItemOnBucketColumn + 1, self.bucket1.shape[0]):
                    arrayX = np.zeros((2, 2), dtype=object)
                    arrayY = np.zeros((2, 2), dtype=object)
                    tempArrayX = image.extract_patches_2d((self.bucket1[eachItemOnBucketColumn][2]), (2, 2))
                    tempArrayY = image.extract_patches_2d((self.bucket1[eachItemOnBucketRow][2]), (2, 2))
                    arrayX = tempArrayX[0]
                    arrayY = tempArrayY[0]
                    # convert 2Dimensional Array into 1D Array
                    x = np.reshape(arrayX, 4)
                    y = np.reshape(arrayY, 4)
                    # ___end___
                    hasilVariantAntarDuaBlock = np.var([x, y])
                    hasilSubstractAntarDuaBlock = np.subtract(x, y)
                    t = (np.multiply(((hasilSubstractAntarDuaBlock).transpose()), (hasilSubstractAntarDuaBlock))) / (
                    hasilVariantAntarDuaBlock / 4)
                    #chi = chisquare()
                    print t
                    break
                break



        except:
            logging.error(traceback.format_exc())

if __name__ == '__main__':
    startTime = time.time()
    Run = ExpandingBlockAlgorithm("im2_t.bmp", 32)
    Run.expandingBlockAlgorithm()
    endTime = time.time()
    print "Proccess Time : " + str(endTime - startTime)