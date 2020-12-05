import os
import codes.blockClass as bloc


def delAttri(path):
    for name in os.listdir(path):
        if name.endswith(".attributes"):
            os.remove(os.path.join(path, name))


def calFscore(predset, trueset):
    correct = 0
    for p in predset:
        if p in trueset: correct += 1
    pre = 0 if len(predset) == 0 else float(correct) / len(predset)
    rec = 0 if len(trueset) == 0 else float(correct) / len(trueset)
    print('pre: {}, rec: {}'.format(pre, rec))
    if pre + rec > 0:
        F = 2 * pre * rec / (pre + rec)
    else:
        F = 0
    print('f1:{}'.format(F))
    return F


def cal_block_density(file):
    ids = set()
    apps = set()
    it_sts = set()
    mass = 0
    f = open(file, 'r')
    for line in f.readlines():
        cols = line.replace('\n', '').split(',')
        ids.add(cols[0])
        apps.add(cols[1])
        it_sts.add(cols[2])
        mass = mass + float(cols[3])
    blocksize = ids.__len__()+apps.__len__()+it_sts.__len__()
    if blocksize != 0:
        density = round(mass/blocksize, 1)
    else:
        density = 0
    return density, mass, blocksize


def writeBlockToFile(path, block, tuplefilename):
    tuplefile = os.path.join(path, tuplefilename)
    tuples = block.getTuples()
    with open(tuplefile, 'w') as tuplef:
        for key in tuples:
            words = list(key)
            words.append(str(tuples[key]))
            tuplef.write(','.join(words))
            tuplef.write('\n')
    tuplef.close()


def readBlocksfromPath(path, k):
    blocklist = []
    for i in range(1, k+1):
        tuplefile = os.path.join(path, 'block_{}.tuples'.format(i))
        block = readBlock(tuplefile)
        blocklist.append(block)
    return blocklist


def readBlock(tuplefile):
    attridict, colDegreeDicts, colKeysetDicts, tupledict = {}, {}, {}, {}
    dimension = 3
    for idx in range(dimension):
        attridict[idx] = set()
        colDegreeDicts[idx] = {}
        colKeysetDicts[idx] = {}
    M = 0.0
    with open(tuplefile, 'r') as tf:
        for line in tf:
            cols = line.strip().split(',')
            key, value = tuple(cols[:-1]), int(cols[-1])
            if key not in tupledict:
                tupledict[key] = value
            else:
                tupledict[key] += value
            M += value
            for idx in range(dimension):
                attr = key[idx]
                if attr not in attridict[idx]:
                    attridict[idx].add(attr)
                    colKeysetDicts[idx][attr] = set()
                    colKeysetDicts[idx][attr].add(key)
                    colDegreeDicts[idx][attr] = value
                else:
                    colDegreeDicts[idx][attr] += value
                    colKeysetDicts[idx][attr].add(key)
    size = len(attridict[0]) + len(attridict[1]) + len(attridict[2])
    block = bloc.block(tupledict, attridict, colDegreeDicts, colKeysetDicts, M, size, dimension)
    return block


def saveSimpleListData(simls, outfile):
    with open(outfile, 'w') as fw:
        'map(function, iterable)'
        fw.write('\n'.join(map(str, simls)))
        fw.write('\n')
        fw.close()




