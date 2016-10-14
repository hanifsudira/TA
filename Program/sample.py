# -*- coding: utf-8 -*-
"""
Created on Sat May  7 11:53:35 2016
@author: efron
"""

"""
expanding_block
"""

import numpy as np
import os
from PIL import Image
import copy
import skimage
from skimage import io
from skimage import color
from scipy.stats.distributions import chi2


def IMPORT_PLACEHOLDER():
    pass


filename = 'face.png'

"""
file IO and conversion to grayscale:
"""
baseImg = io.imread(filename)
try:
    img = skimage.color.rgb2gray(baseImg)
except ValueError as valError:
    shape = np.shape(baseImg)
    if shape[2] == 1:  # image is grayscale already
        img = baseImg
    else:
        raise valError
except Exception as exc:
    raise exc

"""
set parameters based off image size
"""


class ExpandingBlockInit:
    def __init__(self, img):
        shape = np.shape(img)
        size = shape[0] * shape[1]

        if size <= 50 ** 2:
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 400
            self.minArea = 32
            self.varianceThreshold = 8 * 4
        elif size <= 100 ** 2:
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 400
            self.minArea = 50
            self.varianceThreshold = 8 * 4
        elif size <= 200 ** 2:
            self.blockSize = 8
            self.blockDistance = 1
            self.numBuckets = 600
            self.minArea = 50
            self.varianceThreshold = 8 * 4
        elif size <= 350 ** 2:
            self.blockSize = 16
            self.blockDistance = 1
            self.numBuckets = 5000
            self.minArea = 50
            self.varianceThreshold = 16 * 4
        elif size <= 700 ** 2:
            self.blockSize = 16
            self.blockDistance = 1
            self.numBuckets = 12000
            self.minArea = 70
            self.varianceThreshold = 16 * 4
        else:
            self.blockSize = 16
            self.blockDistance = 1
            self.numBuckets = size // 128
            self.minArea = 70
            self.varianceThreshold = 16 * 4


init = ExpandingBlockInit(img)

"""
Divide the image into small overlapping blocks of blockSize ** 2
"""


# img = Image.open(filename)


def find_variance(A):
    # find the variance of A
    mean = np.mean(A)
    variance = sum((a - mean) ** 2 for a in A) / A.size
    return variance


image = None  # pass
size = np.shape(img)
rows = size[0]
cols = size[1]


class Block:
    def __init__(self, img, row, col):
        rowEnd = row + (init.blockSize - 1)
        colEnd = col + (init.blockSize - 1)

        # use copy.copy because python assigns by reference
        self.pixel = (img[row:rowEnd, col:colEnd, :])
        self.row = row
        self.col = col
        self.variance = find_variance(self.pixel)
        self.tooLowVariance = self.variance < init.varianceThreshold
        self.subBlock = None
        self.connection = None


# list comprehensions make this whole next section way easier!
blocks = [Block(row, col) for row in range(rows - init.blockSize)
          for col in range(cols - init.blockSize)]

# sort by variance
blocks.sort(key=lambda x: x.variance)

"""
remove elements with too low of variance
causes false positives due to bad white balance on camera or just areas of
block color
"""
# this is not efficient, but it is negligible in comparison to overhead of
# other parts of program, and it's a neat bit of set theory.

blocks = [block for block in blocks if not block.tooLowVariance]
groups = []
# assign blocks to groups
blocksPerBucket = len(blocks) / init.numBuckets
group = 0
count = 0
for block in enumerate(blocks):
    count += 1
    groups[group].append = block
    if count > blocksPerBucket:
        count -= blocksPerBucket
        # group is full, move on to next group
        groups.append([])

# assign groups to buckets
buckets = [None] * init.numBuckets

for n in range(init.numBuckets):
    buckets[n] = group[n - 1] + group[n] + group[n + 1]


def process_bucket(bucket, init):
    TINY_NUMBER = 10. ** -12
    """
    subfunctions
    """

    def overlap(bucket, init):
        # if buckets overlap, they should be more similar than chance

        row = [block.row for block in bucket]
        col = [block.col for block in bucket]
        rowDistance = row - row.reshape(-1, 1)
        colDistance = col - col.reshape(-1, 1)

        # broadcast to an N x N array
        rowOverlap = rowDistance < init.blockSize
        colOverlap = colDistance < init.blockSize

        return np.logical_or(rowOverlap, colOverlap)

    # calculate test statistic of block-to-block similarity
    def calculate_test_statistic(bucket):
        test_statistic = np.zeros(len(bucket), len(bucket))
        for index, subBlock in enumerate(subBlocks):
            pixel_diff = np.sum((subBlock - subBlocks) ** 2, axis=1)
            sigmaSq = (variance[index] + variance) / 2.
            # avoid zero divides
            sigmaSq[(sigmaSq < TINY_NUMBER)] = (TINY_NUMBER)
            # calcualte test statistic
            test_statistic[index] = (pixel_diff / (sigmaSq * subSize))
        return test_statistic

    # calculate whether blocks are too similar to have occured by chance
    def find_connection(bucket, test_statistic):
        test_statistic = calculate_test_statistic(bucket)
        pValThreshold = chi2.ppf(.01, subSize ** 2)
        too_similar = test_statistic < pValThreshold
        # blocks are "connected" if they occur by chance < 1% of the time and
        # do not overlap.
        connection = np.any(np.logical_and(~overlap, too_similar), [0])
        return connection

    """
    process_bucket body
    """

    if len(bucket) == 0:
        # bucket empty, no need to process
        return

    subSize = 1
    variance = [block.variance for block in bucket]
    count = 0
    while subSize < init.blockSize:
        # sanity check for while loop
        count += 1
        if count > 10:
            raise (ValueError('process_bucket in infinite loop'))

        # expanding block: we start with a 2x2 subblock of the image,
        # test for similarity to other 2x2 subblocks,
        # then continue
        subSize = min(subSize << 1, init.blockSize)
        subBlocks = np.array([np.reshape(block.pixel[0:subSize][:, 0:subSize], -1) for block in bucket])
        test_statistic = calculate_test_statistic(bucket)
        connection = find_connection(bucket, test_statistic)

        # test if number of connected blocks are under minimum area
        # if so, we consider those connections false positives and empty bucket
        # then kick out early

        if (sum(connection) * init.blockSize) < init.minArea:
            bucket = []
            return bucket

        # otherwise, we remove isolated blocks from bucket and let the loop run

        for index, block in enumerate(bucket):
            block.connection = connection[index]
            bucket = [block for block in bucket if block.connection]
    return bucket


"""
call process_bucket with one-line list comprehension
"""
buckets = [process_bucket(bucket) for bucket in buckets]
