import os
import shutil
from codes import util
import codes.CalTopkBlocks as Caltopk


def optimiAlgo(inputfile, outpath, s, k, l, maxSp, N, delimeter, steps):
    augmented_lines, accum_lines = [], []
    sindex = 0
    mints = 0
    with open(inputfile, 'r') as f:
        for line in f:
            user, obj, ts, v = map(int, line.strip().split(delimeter))
            augmented_lines.append(line)
            accum_lines.append(line)
            if ts - mints >= s:
                dcube_file = os.path.join('augfile.txt')
                f = open(dcube_file, 'w')
                f.writelines(augmented_lines)
                f.close()
                dcube_output = os.path.join('augfile_dcube_output', str(sindex))
                if not os.path.exists(dcube_output):
                    os.makedirs(dcube_output)
                os.system('cd ./dcube-master && ./run_single.sh' + ' ../' +
                          dcube_file + ' ../' + dcube_output + ' ' + str(N) + ' ari density ' + str(k+l))
                if sindex == 0:
                    curr_output = os.path.join(outpath, str(sindex))
                    if not os.path.exists(curr_output):
                        os.makedirs(curr_output)
                    for fn in os.listdir(dcube_output):
                        file = os.path.join(dcube_output, fn)
                        file2 = os.path.join(curr_output, fn)
                        shutil.copy(file, file2)
                else:
                    dcubeBlocks = util.readBlocksfromPath(dcube_output, k+l)
                    past_output = os.path.join(outpath, str(sindex - 1))
                    pastBlocks = util.readBlocksfromPath(past_output, k+l)

                    curr_output = os.path.join(outpath, str(sindex))
                    if not os.path.exists(curr_output):
                        os.mkdir(curr_output)

                    currBlocks = Caltopk.calTopkBlock(dcubeBlocks, pastBlocks, k, l, maxSp, N)

                    for idx, block in enumerate(currBlocks):
                        tuplefile = 'block_' + str(idx + 1) + '.tuples'
                        util.writeBlockToFile(curr_output, block, tuplefile)
                mints = ts
                augmented_lines = []
                sindex += 1
                if sindex == steps:
                    print('***end***')
                    break