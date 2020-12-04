class block:
    tupledict = {}
    mass = 0.0
    size = 0.0
    dimension = 0
    colsetDict = {}
    colDegreeDicts = {}
    colKeysetDicts = {}

    def __init__(self, tupledict,  colsetDict, colDegreeDicts, colKeysetDicts, mass, size, dimension):
        self.tupledict = tupledict
        self.mass = mass
        self.size = size
        self.dimension = dimension
        self.colsetDict = colsetDict
        self.colDegreeDicts = colDegreeDicts
        self.colKeysetDicts = colKeysetDicts

    def addUpdate(self, changetuples):
        for key in changetuples:
            value = changetuples[key]
            if key not in self.tupledict:
                self.tupledict[key] = value
                self.mass = self.mass + value
                for i in range(self.dimension):
                    attr = key[i]
                    if attr not in self.colsetDict[i]:
                        self.size = self.size + 1
                        self.colDegreeDicts[i][attr] = value
                        self.colsetDict[i].add(attr)
                        self.colKeysetDicts[i][attr] = set()
                        self.colKeysetDicts[i][attr].add(key)
                    else:
                        self.colDegreeDicts[i][attr] += value
                        self.colKeysetDicts[i][attr].add(key)

    def removeUpdate(self, changetuples):
        for key in changetuples:
            value = changetuples[key]
            self.tupledict.pop(key)
            self.mass -= value
            for i in range(self.dimension):
                attr = key[i]
                self.colDegreeDicts[i][attr] -= value
                self.colKeysetDicts[i][attr].remove(key)
                if self.colDegreeDicts[i][attr] == 0:
                    self.colDegreeDicts[i].pop(attr)
                    self.colKeysetDicts[i].pop(attr)
                    self.colsetDict[i].remove(attr)
                    self.size -= 1

    def getTuples(self):
        return self.tupledict

    def getMass(self):
        return self.mass

    def getSize(self):
        return self.size

    def getDensity(self):
        return self.mass / self.size

    def getAttributeDict(self):
        return self.colsetDict

    def getColDegreeDicts(self):
        return self.colDegreeDicts

    def getColKeysetDicts(self):
        return self.colKeysetDicts