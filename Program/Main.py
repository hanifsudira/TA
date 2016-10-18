import sys
import time
import numpy as np
import scipy.misc
from skimage import io, color
from scipy.stats import chisquare
from sklearn.feature_extraction import image
from operator import itemgetter
from scipy.stats.distributions import chi2

class Block:
    def __init__(self,image, row, col, blockSize, varTres):
        rowEnd          = row + (blockSize-1)
        colEnd          = col + (blockSize-1)
        self.row        = row
        self.col        = col
        self.coor       = (row,col)
        self.block      = image[row:rowEnd,col:colEnd]
        self.variance   = np.var(self.block)

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
        #self.sortByDominantFeature()
        self.createGroup()
        self.createBucket()
        #print color.gray2rgb(self.buckets[0][0].block)
        self.copyMoveDetection()
        self.buildCopyMoveImage()

    def buildOverLapBlock(self):
        print "Fungsi Build Overlapping"
        #self.overLappingBlock = image.extract_patches_2d(self.grayScaleImage, (self.blockSize,self.blockSize))
        self.overLappingBlock = []
        for i in range(self.height - self.blockSize +1 ):
            for j in range(self.width - self.blockSize + 1):
                self.overLappingBlock.append(Block(self.grayScaleImage,i,j,self.blockSize,self.varianceThreshold))
        self.overLappingBlock.sort(key=lambda val: val.variance)
        self.sizeOverLappingBlock = len(self.overLappingBlock)
        print "Selesai Fungsi Overlapping"

    #def sortByDominantFeature(self):
    #    print "Fungsi Sort Dominant Feature"
    #    arrayTemp = np.zeros((self.sizeOverLappingBlock, 4), dtype=object)
    #    for i in range(self.sizeOverLappingBlock):
    #        meanEachBlock = np.mean(self.overLappingBlock[i])
    #        varianceEachBlock = np.var(self.overLappingBlock[i])
    #        arrayTemp[i] = [i, meanEachBlock, varianceEachBlock, self.overLappingBlock[i]]
    #    self.arrayCalculation = sorted(arrayTemp, key=itemgetter(1,2))
    #    print "Selesai Fungsi Sort Dominant Feature"

    def createGroup(self):
        print "Fungsi Create Group"
        self.groups = [[] for i in range(self.numBuckets)]
        blocksPerBucket = int(self.sizeOverLappingBlock / self.numBuckets)
        #modBlocksPerBucket = self.sizeOverLappingBlock % self.numBuckets
        #print self.sizeOverLappingBlock, self.numBuckets, blocksPerBucket, modBlocksPerBucket
        start = 0
        end = blocksPerBucket
        for i in range(self.numBuckets):
            tempBlock = self.overLappingBlock[start:end]
            while len(tempBlock) > 0:
                self.groups[i].append(tempBlock.pop())
            start = end
            end += blocksPerBucket

        modIndex = self.numBuckets * blocksPerBucket - 1
        counter = 0
        for i in range(modIndex,self.sizeOverLappingBlock):
            self.groups[counter].append(self.overLappingBlock[i])
            counter += 1
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

    def checkZeroRows(self,connectionMatrix):
        for i in connectionMatrix:
            if i == 1:
                return False
        return True

    def copyMoveDetection(self):
        print "Fungsi Copy Move"
        self.tupleCoordinate = []
        for i in range(len(self.buckets)-1):
            bucket1 = self.buckets[i]
            lenBucket1 = len(bucket1)
            bucket2 = self.buckets[i+1]
            lenBucket2 = len(bucket2)
            connectionMatrix = np.ones((lenBucket1,lenBucket2))

            for x in range(lenBucket1):
                if any(v == 1 for v in connectionMatrix[x]):
                    for y in range(lenBucket2):
                        block1 = bucket1[x]
                        block2 = bucket2[y]
                        rowblock1 = block1.row
                        colblock1 = block1.col
                        rowblock2 = block2.row
                        colblock2 = block2.col
                        if abs(rowblock1-rowblock2) < self.blockSize and abs(colblock1-colblock2) < self.blockSize:
                            connectionMatrix[x,y] = 0
                            break
                        subSize = 2
                        while subSize < self.blockSize:
                            image1 = block1.block[0:subSize,0:subSize]
                            image2 = block2.block[0:subSize,0:subSize]
                            variance2block = np.var([image1,image2])
                            subtract2block =  np.subtract(image1,image2)
                            t = np.multiply(subtract2block.transpose(),subtract2block)
                            t = t/(variance2block/subSize**2)
                            chi = chisquare(image1, image2, axis=None)

                            X = chi[0]
                            pval = chi[1]
                            if pval < self.pvalThreshold:
                                connectionMatrix[x,y] = 0
                                break
                            subSize = min(subSize << 1 , self.blockSize)

            for a in range(connectionMatrix.shape[0]):
                for b in range(connectionMatrix.shape[1]):
                    if connectionMatrix[a,b] == 1:
                        tempa = self.buckets[i][a].coor
                        tempb = self.buckets[i][a].coor
                        self.tupleCoordinate.append((tempa,tempb))

    def buildCopyMoveImage(self):
        myimage = np.zeros((self.height,self.width))
        for i in self.tupleCoordinate:
            print i
            a = i[0]
            b = i[1]
            myimage[a[0]:a[0] + self.blockSize, a[1]:a[1] + self.blockSize] = 255
            myimage[b[0]:b[0] + self.blockSize, b[1]:b[1] + self.blockSize] = 255
        scipy.misc.imsave("coba.png",myimage)

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
