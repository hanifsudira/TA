temp = [None]*100

print temp
self.dominantFeature = np.empty((len(self.overLappingBlock), 32, 32))
        for i in range(len(self.overLappingBlock)):
            for j in range(self.overLappingBlock[i].shape[0]):
                for k in range(self.overLappingBlock[i].shape[1]):
                    temp = self.overLappingBlock[i, j, k]
                    self.dominantFeature[i, j, k] = self.histogram[temp]