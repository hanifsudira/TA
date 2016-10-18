import time
import sys
import numpy as np
#import scipy.misc
from skimage import io, color
#from scipy.stats import chisquare
from sklearn.feature_extraction import image
#from operator import itemgetter
from scipy.stats.distributions import chi2

class Block:
    def __init__(self,image, row, col, blockSize, varTres):
        rowEnd          = row + (blockSize-1)
        colEnd          = col + (blockSize-1)
        self.row        = row
        self.col        = col
        self.coor       = (row,col)
        self.pixel      = image[row:rowEnd,col:colEnd]
        self.variance   = np.var(self.pixel)

class ExpandingBlockAlgorithm:
    def __init__(self,filename):
        try:
            self.image = io.imread(filename)
            self.height, self.width, self.channel = np.shape(self.image)
            self.size = self.height * self.width
            self.grayScaleImage = color.rgb2gray(self.image)
            self.setValue()
            self.pvalThreshold = 0.99
        except:
            print "File Gambar Tidak Ditemukan"

    def expandingBlockAlgorithm(self):
        self.buildOverLapBlock()
        #self.createGroup()
        #self.createBucket()
        #self.copyMoveDetection()
        #self.buildCopyMoveImage()

    def buildOverLapBlock(self):
        print "Fungsi Build Overlapping"
        self.overLappingBlock = image.extract_patches_2d(self.grayScaleImage, (self.blockSize,self.blockSize))
        self.overLappingBlock = []
        for i in range(self.height - self.blockSize +1 ):
            for j in range(self.width - self.blockSize + 1):
                self.overLappingBlock.append(Block(self.grayScaleImage,i,j,self.blockSize,self.varianceThreshold))
        self.overLappingBlock.sort(key=lambda val: val.variance)
        self.sizeOverLappingBlock = len(self.overLappingBlock)
        print self.sizeOverLappingBlock
        print "Selesai Fungsi Overlapping"

    def createGroup(self):
        print "Fungsi Create Group"
        self.groups = [[] for i in range(self.numBuckets)]
        blocksPerBucket = int(self.sizeOverLappingBlock / self.numBuckets)
        #start = 0
        #end = blocksPerBucket
        #for i in range(self.numBuckets):
        #    tempBlock = self.overLappingBlock[start:end]
        #    while len(tempBlock) > 0:
        #        self.groups[i].append(tempBlock.pop())
        #    start = end
        #    end += blocksPerBucket

        #modIndex = self.numBuckets * blocksPerBucket - 1
        #counter = 0
        #for i in range(modIndex,self.sizeOverLappingBlock):
        #    self.groups[counter].append(self.overLappingBlock[i])
        #    counter += 1
        group = 0
        count = 0
        for block in self.overLappingBlock:
            self.groups[group].append(block)
            count += 1
            if count > blocksPerBucket:
                group += 1
                count = 0
        print "Selesai Fungsi Create Group"

    def createBucket(self):
        print "Fungsi Create Bucket"
        self.buckets = [None]*self.numBuckets
        for i in range(self.numBuckets):
            try:
                self.buckets[i] = self.groups[i-1] + self.groups[i] + self.groups[i+1]
            except IndexError:
                if i == self.numBuckets-1:
                    self.buckets[i] = self.groups[i-1]+self.groups[i]
                else:
                    raise IndexError
        print "Selesai Fungsi Create Bucket"

    def copyMoveDetection(self):
        print "Fungsi Copy Move"
        tempBuckets = [self.bucketProcess(bucket) for bucket in self.buckets]
        self.buckets = tempBuckets
        tempBlocks = [block for bucket in self.buckets for block in bucket]
        self.blocks = tempBlocks
        print "Selesai Fungsi Copy Move"

    def bucketProcess(self,bucket):
        subSize = 1
        while subSize < self.blockSize:
            if len(bucket)*self.blockSize < self.minArea:
                return []

            subSize = min(subSize << 1, self.blockSize)
            subBlocks = [block.pixel[0:subSize,0:subSize] for block in bucket]

            testStatistic = self.calTestStatistic(subBlocks,subSize)
            overLap = self.findOverlap(bucket)
            connection = self.findConnection(testStatistic,overLap,subSize)
            connection = np.any(connection, axis=0)

            bucket = [bucket[i] for i in range(len(bucket)) if connection[i]]

            if len(bucket)*self.blockSize < self.minArea:
                return []
        return bucket

    def findConnection(self,testStatistic,overLap,subSize):
        pvalThreshold = chi2.ppf(.01,subSize**2)
        tooSimilar = testStatistic < self.pvalThreshold
        connection = np.ones_like(tooSimilar)
        connection = np.logical_xor(connection, np.logical_or(overLap, np.logical_not(tooSimilar)))
        return connection

    def calTestStatistic(self,subBlocks,subSize):
        lenSubBlocks = len(subBlocks)
        testStatistic = np.zeros((lenSubBlocks,lenSubBlocks))
        variance = [np.var(subBlock) for subBlock in subBlocks]

        for index, subBlock in enumerate(subBlocks):
            diffPixel = np.sum((subBlock - subBlocks)**2, axis=(1,2))
            sigmaSQ = (variance[index] + variance) / 2.
            try:
                testStatistic[index] = diffPixel / (sigmaSQ*subSize)
            except ZeroDivisionError:
                print "Zero Division Error"
                testStatistic[index] = 0
        return testStatistic

    def findOverlap(self,bucket):
        row = [block.row for block in bucket]
        col = [block.col for block in bucket]
        rowDistance = np.abs(row - np.reshape(row, (-1, 1)))
        colDistance = np.abs(col - np.reshape(col, (-1, 1)))
        rowOverlap = rowDistance < self.blockSize
        colOverlap = colDistance < self.blockSize

        return np.logical_or(rowOverlap, colOverlap)

    def buildCopyMoveImage(self):
        print "Fungsi Build Copy Move"
        if len(self.blocks) == 0:
            print "Cupu"
        mask = self.createMask()
        imageOut = np.uint8(self.writeMask(mask))
        io.imsave("hasil4.png",imageOut)
        print "Fungsi Build Copy Move"

    def createMask(self):
        RED = 0
        GREEN = 1
        BLUE = 2
        FILL_CHANNEL = 4
        mask = np.zeros((self.height,self.width,3), dtype=np.uint8)
        for block in self.blocks:
            row = block.row
            col = block.col
            endRow = row + self.blockSize
            endCol = col + self.blockSize
            mask[row:endRow, col:endCol, RED] = FILL_CHANNEL
            mask[row:endRow, col:endCol, BLUE] = FILL_CHANNEL
            mask[row:endRow, col:endCol, GREEN] = FILL_CHANNEL
        return mask

    def writeMask(self,mask):
        FILL_CHANNEL = 4
        REMOVE_CHANNEL = 8
        imgMasked = np.uint8(255 * color.gray2rgb(color.rgb2gray(self.image)))
        imgMasked[mask == FILL_CHANNEL] = 255
        imgMasked[mask == REMOVE_CHANNEL] = 0
        row = self.height
        separator = np.ones((row,16,3),dtype=np.uint8)
        imageOut = np.concatenate((self.image,separator,imgMasked), axis=1)
        return imageOut

    def setValue(self):
        if self.size <= 50**2:
            print 1
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 400
            self.minArea = 32
            self.varianceThreshold = 2*self.blockSize**2
        elif self.size <= 100**2:
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 400
            self.minArea = 55
            self.varianceThreshold = 4*self.blockSize**2
        elif self.size <= 200**2:
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 600
            self.minArea = 55
            self.varianceThreshold = 2*self.blockSize**2
        elif self.size <= 350**2:
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 5000
            self.minArea = 55
            self.varianceThreshold = 2*self.blockSize**2
        elif self.size <= 700**2:
            self.blockSize = 16
            self.blockDistance = 1
            self.numBuckets = 12000
            self.minArea = 100
            self.varianceThreshold = 4*self.blockSize**2
        else:
            self.blockSize = 16
            self.blockDistance = 1
            self.numBuckets = self.size // 128
            self.minArea = 120
            self.varianceThreshold = 4*self.blockSize**2


if __name__ == '__main__':
    startTime = time.time()
    Run = ExpandingBlockAlgorithm("02_tree.png")
    Run.expandingBlockAlgorithm()
    endTime = time.time()
    print "Proccess Time : " + str(endTime - startTime)
