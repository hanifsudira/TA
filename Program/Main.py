import time
import numpy as np
from skimage import io
from sklearn.feature_extraction import image
from operator import itemgetter

class ExpandingBlockAlgorithm:
    def __init__(self,filename):
        try:
            self.image = io.imread(filename)
            self.height, self.width, self.channel = np.shape(self.image)
            self.size = self.height * self.width
            self.setValue()
        except:
            print "File Gambar Tidak Ditemukan"

    def expandingBlockAlgorithm(self):
        self.buildOverLapBlock()        #step 1
        self.sortByDominantFeature()    #step 2
        self.createGroup()              #step 3
        self.createBucket()             #step 4
        self.copyMoveDetection()        #step 5

    def buildOverLapBlock(self):
        print "Fungsi Build Overlapping"
        self.grayScaleImage = self.rgbToGrayScale(self.image).astype(np.uint8)
        self.overLappingBlock = image.extract_patches_2d(self.grayScaleImage, (self.blockSize,self.blockSize))
        self.sizeOverLappingBlock = self.overLappingBlock.shape[0]
        #self.createHistogram()
        print "Selesai Fungsi Overlapping"

    def sortByDominantFeature(self):
        print "Fungsi Sort Dominant Feature"
        arrayTemp = np.zeros((self.sizeOverLappingBlock, 4), dtype=object)
        for i in range(self.sizeOverLappingBlock):
            meanEachBlock = np.mean(self.overLappingBlock[i])
            varianceEachBlock = np.var(self.overLappingBlock[i])
            arrayTemp[i] = [i, meanEachBlock, varianceEachBlock, self.overLappingBlock[i]]
        self.arrayCalculation = sorted(arrayTemp, key=itemgetter(1,2))
        print "Selesai Fungsi Sort Dominant Feature"

    def createGroup(self):
        print "Fungsi Create Group"
        self.groups = [[] for i in range(self.numBuckets)]
        blocksPerBucket = int(self.sizeOverLappingBlock / self.numBuckets)
        #modBlocksPerBucket = self.sizeOverLappingBlock % self.numBuckets
        #print self.sizeOverLappingBlock, self.numBuckets, blocksPerBucket, modBlocksPerBucket
        start = 0
        end = blocksPerBucket
        for i in range(self.numBuckets):
            tempBlock = self.arrayCalculation[start:end]
            while len(tempBlock) > 0:
                self.groups[i].append(tempBlock.pop())
            start = end
            end += blocksPerBucket

        modIndex = self.numBuckets * blocksPerBucket - 1
        counter = 0
        for i in range(modIndex,self.sizeOverLappingBlock):
            self.groups[counter].append(self.arrayCalculation[i])
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

    def bucketProcess(self, bucket):
        subSize = 1
        while subSize < self.blockSize:
            if len(bucket)*self.blockSize < self.minArea:
                return []
            subSize = min(subSize << 1, self.blockSize)
            subBlock = [block[3][0:subSize, 0:subSize] for block in bucket]

    def findConnection(self):
        print 1

    def findOverlapping(self,bucket):
        for block in bucket:
            print block[3].shape
            break

    def copyMoveDetection(self):
        #self.buckets = [self.bucketProcess(bucket) for bucket in self.buckets]
        for bucket in self.buckets:
            #self.bucketProcess(bucket)
            self.findOverlapping(bucket)
            break


    def rgbToGrayScale(self, rgb):
        return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

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

    def createHistogram(self):
        self.histogram = np.zeros((256))
        for i in range(self.width):
            for j in range(self.height):
                temp = int(self.grayScaleImage[j, i])
                self.histogram[temp] += 1

        for i in range(len(self.histogram)):
            self.histogram[i] = self.histogram[i]/self.size

if __name__ == '__main__':
    startTime = time.time()
    Run = ExpandingBlockAlgorithm("face.png")
    Run.expandingBlockAlgorithm()
    endTime = time.time()
    print "Proccess Time : " + str(endTime - startTime)
