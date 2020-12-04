import random
import networkx as nx
import codes.spliceTwoBlock as stb


def insertBlockbyDensity(block, blocklist):
    density = block.getMass() / block.getSize()
    canfind = False
    for idx, block2 in enumerate(blocklist):
        density2 = block2.getMass() / block2.getSize()
        if density >= density2:
            blocklist.insert(idx, block)
            canfind = True
            break
    if not canfind:
        blocklist.append(block)
    return blocklist


def getResultBlocks(blockNumdict, k, l):
    results = []
    for key in blockNumdict:
        block = blockNumdict[key]
        if block.getSize() == 0:
            continue
        insertBlockbyDensity(block, results)
    return results[:k+l]


def init_graph(blocklist1, blocklist2, N, k):
    edges = []
    blockNumdict = {}
    for idx, block in enumerate(blocklist1):
        blockNumdict[idx] = block
    for idx, block in enumerate(blocklist2):
        blockNumdict[idx + k] = block
    for idx1, block1 in enumerate(blocklist1):
        modeToAttVals1 = block1.getAttributeDict()
        for idx2, block2 in enumerate(blocklist2):
            modeToAttVals2 = block2.getAttributeDict()
            for dimen in range(N):
                insec_dimens = modeToAttVals1[dimen] & modeToAttVals2[dimen]
                if len(insec_dimens) != 0:
                    edges.append((idx1, k+idx2))
                    break
    G = nx.Graph()
    G.add_edges_from(edges)
    return G, blockNumdict

'block1: remove edge with taken_ego_nodes, add edge with left_ego_nodes'
'block2: remove edge with left_ego_nodes'
def update_graph(G, blockNumdict, takennode, leftnode, N):
    takenblock = blockNumdict[takennode]
    leftblock = blockNumdict[leftnode]
    modeToAttVals1 = takenblock.getAttributeDict()
    modeToAttVals2 = leftblock.getAttributeDict()
    left_ego_nodes = set(list(nx.ego_graph(G, leftnode, radius=1)))
    taken_ego_nodes = set(list(nx.ego_graph(G, takennode, radius=1)))
    'block1: add edge with left_ego_nodes'
    nodeset1 = left_ego_nodes - taken_ego_nodes
    for node in nodeset1:
        block = blockNumdict[node]
        modeToAttVals3 = block.getAttributeDict()
        for dimen in range(N):
            insec_dimens = modeToAttVals1[dimen] & modeToAttVals3[dimen]
            if len(insec_dimens) != 0:
                G.add_edge(node, takennode)
                break
    'block1: remove edge with taken_ego_nodes'
    taken_ego_nodes.remove(takennode)
    taken_ego_nodes.remove(leftnode)
    for node in taken_ego_nodes:
        block = blockNumdict[node]
        modeToAttVals3 = block.getAttributeDict()
        insec = False
        for dimen in range(N):
            insec_dimens = modeToAttVals1[dimen] & modeToAttVals3[dimen]
            if len(insec_dimens) != 0:
                insec = True
                break
        if not insec:
            G.remove_edge(node, takennode)
    'block2: remove edge with left_ego_nodes'
    left_ego_nodes.remove(leftnode)
    for node in left_ego_nodes:
        block = blockNumdict[node]
        modeToAttVals3 = block.getAttributeDict()
        insec = False
        for dimen in range(N):
            insec_dimens = modeToAttVals2[dimen] & modeToAttVals3[dimen]
            if len(insec_dimens) != 0:
                insec = True
                break
        if not insec:
            G.remove_edge(node, leftnode)
    return G


'block1: remove edge with taken_ego_nodes, add edge with left_ego_nodes'
'block2: delete leftnode'
def remove_update_graph(G, blockNumdict, takennode, leftnode, N):
    takenblock = blockNumdict[takennode]
    modeToAttVals1 = takenblock.getAttributeDict()
    left_ego_nodes = set(list(nx.ego_graph(G, leftnode, radius=1)))
    taken_ego_nodes = set(list(nx.ego_graph(G, takennode, radius=1)))
    nodeset1 = left_ego_nodes - taken_ego_nodes
    'block1: add edge with left_ego_nodes'
    for node in nodeset1:
        block = blockNumdict[node]
        modeToAttVals3 = block.getAttributeDict()
        for dimen in range(N):
            insec_dimens = modeToAttVals1[dimen] & modeToAttVals3[dimen]
            if len(insec_dimens) != 0:
                G.add_edge(node, takennode)
                break
    'block1: remove edge with taken_ego_nodes'
    taken_ego_nodes.remove(takennode)
    taken_ego_nodes.remove(leftnode)
    for node in taken_ego_nodes:
        block = blockNumdict[node]
        modeToAttVals3 = block.getAttributeDict()
        insec = False
        for dimen in range(N):
            insec_dimens = modeToAttVals1[dimen] & modeToAttVals3[dimen]
            if len(insec_dimens) != 0:
                insec = True
                break
        if not insec:
            G.remove_edge(node, takennode)
    'delete leftnode'
    G.remove_node(leftnode)
    return G


def calTopkBlock(blocklist1, blocklist2, k, l, maxSp, N):
    G, blockNumdict = init_graph(blocklist1, blocklist2, N, k)
    if len(G.nodes) == 0:
        return getResultBlocks(G, blockNumdict, k, l)
    lastden = min(blocklist1[-1].getDensity(), blocklist2[-1].getDensity())
    i, fail = 0, 0
    while i < maxSp and fail < 5 * maxSp:
        cnode, neighnode = random.choice(list(G.edges()))
        block1 = blockNumdict[cnode]
        block2 = blockNumdict[neighnode]
        if block1.getDensity() >= block2.getDensity():
            sflag, takenBlock, leftBlock = stb.splice_two_block(block1, block2, N)
            label = '1'
        else:
            sflag, takenBlock, leftBlock = stb.splice_two_block(block2, block1, N)
            label = '2'
        if sflag:
            i += 1
            if label == '2':
                cnode, neighnode = neighnode, cnode
            blockNumdict[cnode], blockNumdict[neighnode] = takenBlock, leftBlock
            if leftBlock.getSize() != 0 and leftBlock.getDensity() >= lastden:
                'update rule changes'
                G = update_graph(G, blockNumdict, cnode, neighnode, N)
            else:
                G = remove_update_graph(G, blockNumdict, cnode, neighnode, N)
        else:
            fail += 1
    return getResultBlocks(blockNumdict, k, l)