def judge(key, existAttrSetdict, remainColsetdict, N, d):
    for idx in d:
        if key[idx] not in remainColsetdict[idx]:
            return False
    spModes = set(range(N)) - set(d)
    for idx in spModes:
        if key[idx] not in existAttrSetdict[idx]:
            return False
    return True


def judge2(key, dimen1Attrs, dimen2Attrs, dimen1Attrs2, dimen2Attrs2, dimen1, dimen2):
    if key[dimen1] in dimen1Attrs and key[dimen2] in dimen2Attrs:
        return True
    if key[dimen1] in dimen1Attrs2 and key[dimen2] in dimen2Attrs2:
        return True
    return False


def findInsecTuples(block1, block2,  existAttrSetdict, N):
    block1Tuples, block2Tuples = block1.getTuples(), block2.getTuples()
    block2ColKeysetDicts = block2.getColKeysetDicts()
    colKeysetDict = block2ColKeysetDicts[2]
    cols = existAttrSetdict[N-1]
    isChanged, changeTuples = False, {}
    for col in cols:
        keyset = colKeysetDict[col]
        for key in keyset:
            if key not in block1Tuples and key[0] in existAttrSetdict[0] and key[1] in existAttrSetdict[1]:
               changeTuples[key] = block2Tuples[key]
    if len(changeTuples) != 0:
        isChanged = True
    return isChanged, changeTuples


def spliceOnModes(block1, block2, existAttrSetdict, N, d):
    M, S, initden = block1.getMass(), block1.getSize(), block1.getDensity()
    m, isChanged  = len(d), False
    modeToAttVals2 = block2.getAttributeDict()
    block2Tuples = block2.getTuples()
    block2ColKeysetDicts = block2.getColKeysetDicts()
    attrMassdict, newattrsKeydict, remainColsetdict = {}, {}, {}
    filColsetdict = filterBlock2Cols(initden, block2, existAttrSetdict, d)
    for idx in d:
        remainColset = modeToAttVals2[idx] - existAttrSetdict[idx]
        remainColsetdict[idx] = remainColset - filColsetdict[idx]
    mode = d[0]
    remainColset = remainColsetdict[mode]
    colKeysetDict = block2ColKeysetDicts[mode]
    for col in remainColset:
        keyset = colKeysetDict[col]
        for key in keyset:
            if judge(key, existAttrSetdict, remainColsetdict, N, d):
                if m == 1:
                    attrkey = key[mode]
                else:
                    attrkey = tuple([key[dimen] for dimen in d])
                if attrkey not in attrMassdict:
                    attrMassdict[attrkey] = 0
                    newattrsKeydict[attrkey] = set()
                attrMassdict[attrkey] += block2Tuples[key]
                newattrsKeydict[attrkey].add(key)
    sorted_dict = sorted(attrMassdict.items(), key=lambda x: x[1], reverse=True)
    accessColsetdict = {}
    for idx in range(m):
        accessColsetdict[idx] = set()
    for attr, mass in sorted_dict:
        if mass >= m * initden:
            attrkeys = newattrsKeydict[attr]
            changeTuples = {}
            for product in attrkeys:
                changeTuples[product] = block2Tuples[product]
            block1.addUpdate(changeTuples)
            block2.removeUpdate(changeTuples)
            initden = block1.getDensity()
            isChanged = True
        else:
            break
    return isChanged, block1, block2


# should update block1, block2
def alterCalOneModeByMost(block1, block2, existAttrSetdict, newAttrSetdict, attrMassdict,
                          attrTupledict, N, idx, isfirst):
    M, S, initden = block1.getMass(), block1.getSize(), block1.getDensity()
    modeToAttVals2 = block2.getAttributeDict()
    block2Tuples = block2.getTuples()
    block2ColKeysetDicts = block2.getColKeysetDicts()
    colKeysetDict = block2ColKeysetDicts[idx]
    newattrs, isChanged = set(), False

    remainCols = modeToAttVals2[idx] - existAttrSetdict[idx]
    filterColset = filterBlock2Cols(initden, block2, existAttrSetdict, d=[idx])[idx]
    remainCols.difference_update(filterColset)
    cols = list(range(N))
    cols.remove(idx)
    dimen1, dimen2 = cols[0], cols[1]
    if isfirst:
        dimen1Attrs = newAttrSetdict[dimen1] | existAttrSetdict[dimen1]
        dimen2Attrs = newAttrSetdict[dimen2] | existAttrSetdict[dimen2]
        dimen1Attrs2, dimen2Attrs2 = [], []
    else:
        if len(newAttrSetdict[dimen1]) == 0 and len(newAttrSetdict[dimen2]) != 0:
            dimen1Attrs = existAttrSetdict[dimen1]
            dimen2Attrs = newAttrSetdict[dimen2]
            dimen1Attrs2, dimen2Attrs2 = [], []
        elif len(newAttrSetdict[dimen1]) != 0 and len(newAttrSetdict[dimen2]) == 0:
            dimen1Attrs = newAttrSetdict[dimen1]
            dimen2Attrs = existAttrSetdict[dimen2]
            dimen1Attrs2, dimen2Attrs2 = [], []
        elif len(newAttrSetdict[dimen1]) != 0 and len(newAttrSetdict[dimen2]) != 0:
            dimen1Attrs = existAttrSetdict[dimen1] | newAttrSetdict[dimen1]
            dimen2Attrs = newAttrSetdict[dimen2]
            dimen1Attrs2 = newAttrSetdict[dimen1]
            dimen2Attrs2 = existAttrSetdict[dimen2]
        else:
            dimen1Attrs, dimen2Attrs, dimen1Attrs2, dimen2Attrs2 = [], [], [], []
    remainColsMassdict = {}

    for col in remainCols:
        keyset = colKeysetDict[col]
        for key in keyset:
            if key not in attrTupledict[col]:
                belong = judge2(key, dimen1Attrs, dimen2Attrs, dimen1Attrs2, dimen2Attrs2, dimen1, dimen2)
                if belong:
                    attrMassdict[col] += block2Tuples[key]
                    attrTupledict[col].add(key)
        remainColsMassdict[col] = attrMassdict[col]

    sorted_dict = sorted(remainColsMassdict.items(), key=lambda x: x[1], reverse=True)
    for attr, mass in sorted_dict:
        if mass >= initden:
            M = M + mass
            S = S + 1
            initden = M / S
            newattrs.add(attr)
        else:
            break
    changeTuples = {}
    if len(newattrs) != 0:
        for attr in newattrs:
            attrkeys = attrTupledict[attr]
            for product in attrkeys:
                changeTuples[product] = block2Tuples[product]
    if len(changeTuples) != 0:
        isChanged = True
        block1.addUpdate(changeTuples)
        block2.removeUpdate(changeTuples)
    return isChanged, block1, block2, attrMassdict, newattrs, attrTupledict


def filterBlock2Cols(initden, block2, existAttrSetdict, d):
    modeToAttVals2 = block2.getAttributeDict()
    block2ColDegreeDicts = block2.getColDegreeDicts()
    filterColsetdict = {}
    M2, initden2 = block2.getMass(), block2.getDensity()
    for idx in d:
        remainCols = modeToAttVals2[idx] - existAttrSetdict[idx]
        filterColsetdict[idx] = set()
        collen = len(modeToAttVals2[idx])
        thres = M2 - (collen - 1) * initden2
        if thres < initden:
            filterColsetdict[idx] = remainCols
        else:
            block2ColDegreeDict = block2ColDegreeDicts[idx]
            for col in remainCols:
                degree = block2ColDegreeDict[col]
                if degree < initden:
                    filterColsetdict[idx].add(col)
    return filterColsetdict


def alterCalModesByMost(block1, block2, existAttrSetdict, N):
    modeToAttVals2 = block2.getAttributeDict()
    'initializa attrMassdicts, newAttr, existAttr'
    newAttrSetdict, attrMassdicts, attrTupledicts = {}, {}, {}
    for idx in range(N):
        newAttrSetdict[idx] = set()
        attrMassdicts[idx] = {}
        attrTupledicts[idx] = {}
        for attr in modeToAttVals2[idx]:
            attrMassdicts[idx][attr] = 0
            attrTupledicts[idx][attr] = set()
    isContinue, isfirst = True, True
    while isContinue:
        isContinue = False
        for idx in range(N):
            attrMassdict = attrMassdicts[idx]
            attrTupledict = attrTupledicts[idx]
            'when recur to this dimension again, existing cols should change'
            existAttrSetdict[idx] = existAttrSetdict[idx] | newAttrSetdict[idx]
            isChanged, block1, block2, attrMassdicts[idx], newAttrSetdict[idx], attrTupledicts[idx] = \
                alterCalOneModeByMost(block1, block2, existAttrSetdict, newAttrSetdict,
                                      attrMassdict, attrTupledict, N, idx, isfirst)
            if isChanged:
                if block2.getSize() == 0:
                    isContinue = False
                    break
                isContinue = True
        if isContinue:
            isfirst = False
    return block1, block2


def splice_two_block(block1, block2, N):
    sflag, isChanged = False, False
    modeToAttVals1 = block1.getAttributeDict()
    modeToAttVals2 = block2.getAttributeDict()
    'existAttrSetdict: attributes of block2 which have taken'
    d, insec_dimens_dict = [], {}
    for idx in range(N):
        insec_dimens = modeToAttVals1[idx] & modeToAttVals2[idx]
        if len(insec_dimens) == 0:
            d.append(idx)
        insec_dimens_dict[idx] = insec_dimens
    if len(d) == N:
        return sflag, block1, block2
    else:
        'dimension->dict(col->mass)'
        if len(d) == 0:
            'add insec block into block1, remove it from block2'
            isChanged, changeTuples = findInsecTuples(block1, block2, insec_dimens_dict, N)
            block1.addUpdate(changeTuples)
            block2.removeUpdate(changeTuples)
        if len(d) >= 1:
            'only calculate laped block'
            isChanged, block1, block2 = \
                spliceOnModes(block1, block2, insec_dimens_dict, N, d)
        if isChanged:
            sflag = True
            if block2.getSize() != 0:
                for idx in range(N):
                    insec_dimens_dict[idx] = modeToAttVals1[idx] & modeToAttVals2[idx]
                block1, block2 = alterCalModesByMost(block1, block2, insec_dimens_dict, N)
        return sflag, block1, block2

