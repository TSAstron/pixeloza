import numpy

# Mosaic masks i.e. small triangles
MASKS1 = numpy.zeros((22,12,6), dtype='float64')
MASKS1[0, 8, 0] = 0.375
MASKS1[0, 9,:2] = [23/24, 1/6]
MASKS1[0,10,:3] = [1, 5/6, 1/24]
MASKS1[0,11,:3] = [1, 1, 0.625]
MASKS1[1, 8,:2] = [2/3, 1/12]
MASKS1[1, 9,:3] = [1, 11/12, 1/3]
MASKS1[1,10,:5] = [1, 1, 1, 2/3, 1/12]
MASKS1[1,11,:6] = [1, 1, 1, 1, 11/12, 1/3]
MASKS1[2, 4, 0] = 0.1875
MASKS1[2, 5, 0] = 0.5625
MASKS1[2, 6,:2] = [11/12, 1/48]
MASKS1[2, 7,:2] = [1, 0.3125]
MASKS1[2, 8,:2] = [1, 0.6875]
MASKS1[2, 9,:3] = [1, 47/48, 1/12]
MASKS1[2,10,:3] = [1, 1, 0.4375]
MASKS1[2,11,:3] = [1, 1, 0.8125]
MASKS1[3, 4, 0] = 0.375
MASKS1[3, 5,:2] = [23/24, 1/6]
MASKS1[3, 6,:3] = [1, 5/6, 1/24]
MASKS1[3, 7,:3] = [1, 1, 0.625]
MASKS1[3, 8,:4] = [1, 1, 1, 0.375]
MASKS1[3, 9,:5] = [1, 1, 1, 23/24, 1/6]
MASKS1[3,10,:6] = [1, 1, 1, 1, 5/6, 1/24]
MASKS1[3,11,:6] = [1, 1, 1, 1, 1, 0.625]
MASKS1[4, 0, 0] = 0.125
MASKS1[4, 1, 0] = 0.375
MASKS1[4, 2, 0] = 0.625
MASKS1[4, 3, 0] = 0.875
MASKS1[4, 4,:2] = [1, 0.125]
MASKS1[4, 5,:2] = [1, 0.375]
MASKS1[4, 6,:2] = [1, 0.625]
MASKS1[4, 7,:2] = [1, 0.875]
MASKS1[4, 8,:3] = [1, 1, 0.125]
MASKS1[4, 9,:3] = [1, 1, 0.375]
MASKS1[4,10,:3] = [1, 1, 0.625]
MASKS1[4,11,:3] = [1, 1, 0.875]

MASKS1[5] = MASKS1[0,:,::-1]
MASKS1[6] = MASKS1[1,:,::-1]
MASKS1[7] = MASKS1[2,:,::-1]
MASKS1[8] = MASKS1[3,:,::-1]
MASKS1[9] = MASKS1[4,:,::-1]

MASKS1[10] = MASKS1[0,::-1]
MASKS1[11] = MASKS1[1,::-1]
MASKS1[12] = MASKS1[2,::-1]
MASKS1[13] = MASKS1[3,::-1]
MASKS1[14] = MASKS1[4,::-1]
MASKS1[15,:4,:] = 1
MASKS1[15,4:8,:] = MASKS1[11,:4]

MASKS1[16] = MASKS1[5,::-1]
MASKS1[17] = MASKS1[6,::-1]
MASKS1[18] = MASKS1[7,::-1]
MASKS1[19] = MASKS1[8,::-1]
MASKS1[20] = MASKS1[9,::-1]
MASKS1[21] = MASKS1[15,:,::-1]

# decomposition of display characters into basic masks (no composites here)
SHAPES1 = [[q] for q in range(len(MASKS1))]
SHAPE1_LENS = [MASKS1[q].sum() for q in SHAPES1] # grid pixels per shape

CHARS1 = ["\U0001FB3C","\U0001FB3D","\U0001FB3E","\U0001FB3F","\U0001FB40",#🬼,🬽,🬾,🬿,🭀
          "\U0001FB47","\U0001FB48","\U0001FB49","\U0001FB4A","\U0001FB4B", #🭇,🭈,🭉,🭊,🭋
          "\U0001FB57","\U0001FB58","\U0001FB59","\U0001FB5A","\U0001FB5B","\U0001FB5C", #🭗,🭘,🭙,🭚,🭛,🭜
          "\U0001FB62","\U0001FB63","\U0001FB64","\U0001FB65","\U0001FB66","\U0001FB67"] #🭢,🭣,🭤,🭥,🭦,🭧
SET1 = {'masks': MASKS1, 'shapes': SHAPES1, 'chars': CHARS1}

# Quarter triangular masks
MASKS2 = numpy.zeros((7,12,6), dtype='float64')
MASKS2[0, 6,[2,3]] = 0.25
MASKS2[0, 7,[2,3]] = 0.75
MASKS2[0, 8,[1,2,3,4]] = [0.25, 1, 1, 0.25]
MASKS2[0, 9,[1,2,3,4]] = [0.75, 1, 1, 0.75]
MASKS2[0,10] = [0.25, 1, 1, 1, 1, 0.25]
MASKS2[0,11] = [0.75, 1, 1, 1, 1, 0.75]
MASKS2[1,[0,11],0] = 0.25
MASKS2[1,[1,10],0] = 0.75
MASKS2[1,2:10,0] = 1
MASKS2[1,[2,9],1] = 0.25
MASKS2[1,[3,8],1] = 0.75
MASKS2[1,4:8,1] = 1
MASKS2[1,[4,7],2] = 0.25
MASKS2[1,[5,6],2] = 0.75
MASKS2[2] = MASKS2[0,::-1]
MASKS2[3] = MASKS2[1,:,::-1]

# decomposition of display characters into basic masks
SHAPES2 = [[0],[1],[2],[3],[0,2],[1,2],[2,3]]
SHAPE2_LENS = [MASKS2[q].sum() for q in SHAPES2] # grid pixels per shape

CHARS2 = ["\U0001FB6F","\U0001FB6C","\U0001FB6D","\U0001FB6E", #🭯,🭬,🭭,🭮
          "\U0001FB9A","\U000025E4","\U000025E5"] #🮚,◤,◥,
SET2 = {'masks': MASKS2, 'shapes': SHAPES2, 'chars': CHARS2}

# 1/6 rectangular masks
MASKS3 = numpy.zeros((6,12,6), dtype='float64')
MASKS3[0,0:4,0:3] = 1
MASKS3[1,0:4,3:6] = 1
MASKS3[2,4:8,0:3] = 1
MASKS3[3,4:8,3:6] = 1
MASKS3[4,8:12,0:3] = 1
MASKS3[5,8:12,3:6] = 1

# decomposition of display characters into basic masks
SHAPES3 = [[0],[1],[2],[3],[4],[5],
           [0,1],[0,2],[0,3],[0,4],[0,5],
           [1,2],[1,3],[1,4],[1,5],
           [2,3],[2,4],[2,5],
           [3,4],[3,5],
           [4,5],
           [0,1,2],[0,1,3],[0,1,4],[0,1,5],
           [0,2,3],[0,2,4],[0,2,5],
           [0,3,4],[0,3,5],
           [0,4,5]]

SHAPE3_LENS = [MASKS3[q].sum() for q in SHAPES3] # grid pixels per shape, 12 per basic mask, 18 per quarter

CHARS3 = ["\U0001FB00","\U0001FB01","\U0001FB03","\U0001FB07","\U0001FB0F","\U0001FB1E", #🬀,🬁,🬃,🬇,🬞,
          "\U0001FB02", "\U0001FB04", "\U0001FB08", "\U0001FB10", "\U0001FB1F", #🬂,🬄,🬈,🬐,🬟
          "\U0001FB05", "\U0001FB09", "\U0001FB11", "\U0001FB20", #🬅,🬉,🬑,🬠
          "\U0001FB0B", "\U0001FB13", "\U0001FB22", #🬋,🬓,🬢
          "\U0001FB16", "\U0001FB26", #🬖,🬦
          "\U0001FB2D", #🬭
          "\U0001FB06", "\U0001FB0A", "\U0001FB12", "\U0001FB21", #🬆,🬊,🬒,🬡
          "\U0001FB0C", "\U0000258C", "\U0001FB23", #🬌,▌,🬣
          "\U0001FB17", "\U0001FB27", #🬗,🬧
          "\U0001FB2E"] #🬮
SET3 = {'masks': MASKS3, 'shapes': SHAPES3, 'chars': CHARS3}

# Quarter rectangular masks
MASKS4 = numpy.zeros((4,12,6), dtype='float64')
MASKS4[0,:6,:3] = 1
MASKS4[1,:6,3:] = 1
MASKS4[2,6:,:3] = 1
MASKS4[3,6:,3:] = 1

SHAPES4 = [[0],[1],[2],[3],[0,1],[0,2],[0,3]]
SHAPE4_LENS = [MASKS4[q].sum() for q in SHAPES4] # grid pixels per shape, 18 per basic mask,

CHARS4 = ["\U00002598", "\U0000259D", "\U00002596", "\U00002597", #▘,▝,▖,▗
          "\U00002580", "\U0000258C", "\U0000259A"] #▀,▌,▚
SET4 = {'masks': MASKS4, 'shapes': SHAPES4, 'chars': CHARS4}

# Horizontal and vertical bar, excluding halves
MASKS5 = numpy.zeros((12,12,6),dtype='float64')
MASKS5[ 0,:,0] = 0.75
MASKS5[ 1,:,0] = 1
MASKS5[ 1,:,1] = 0.5
MASKS5[ 2,:,:2] = 1
MASKS5[ 2,:, 2] = 0.25
MASKS5[ 3,:,:3] = 1
MASKS5[ 3,:, 3] = 0.75
MASKS5[ 4,:,:4] = 1
MASKS5[ 4,:, 4] = 0.5
MASKS5[ 5,:,:5] = 1
MASKS5[ 5,:, 5] = 0.25

MASKS5[ 6,10] = 0.5
MASKS5[ 6,11] = 1 
MASKS5[ 7,9:] = 1
MASKS5[ 8, 7] = 0.5
MASKS5[ 8,8:] = 1
MASKS5[ 9, 4] = 0.5
MASKS5[ 9,5:] = 1
MASKS5[10,3:] = 1
MASKS5[11, 1] = 0.5
MASKS5[11,2:] = 1

SHAPES5 = [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11]]
SHAPE5_LENS = [ MASKS5[q].sum() for q in SHAPES5 ]
CHARS5 = ["\U0000258F","\U0000258E","\U0000258D","\U0000258B","\U0000258A","\U00002589", #▏,▎,▍,▋,▊,▉ 1/8, 2/4, 3/8, 5/8, 6/8, 7/8
          "\U00002581","\U00002582","\U00002583","\U00002585","\U00002586","\U00002587"] #▁▂▃▅▆▇ 1/8, 2/4, 3/8, 5/8, 6/8, 7/8
SET5 = {'masks': MASKS5, 'shapes': SHAPES5, 'chars': CHARS5}


# Combining shapes is tricky - the numbers correspond to their own masks, and
# have to be shifted to fit the bigger MASK list
def compose( zestawy ):
    shift = 0
    MASKS, CHARS, SHAPES = [], [], []
    for Z in zestawy:
        MASKS.append( Z['masks'] )
        CHARS += Z['chars']
        SHAPES += [ [ind+shift for ind in shape] for shape in Z['shapes'] ]
        shift += len(Z['masks'])
    return numpy.concatenate(MASKS), CHARS, SHAPES
