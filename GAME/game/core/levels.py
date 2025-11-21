from config import asset
# kí hiệu cho các loại ô trong level
# '#' : solid block
# '.' : không gian trống
# 'P' : vị trí xuất hiện của player
# 'M' : moving platform
# 'L' : moving platform 
# '^' : spike
# 'C' : checkpoint
# 'F' : fake checkpoint
# 'D' : delay checkpoint
# 'H' : hidden spike 
# 'G' : hidden spike 
# '+' : tide (sóng)
# '~' : water (nước)
# 'W' : wall (tường rắn)
# 'O' : connected block
# 'B' : half block
# 'S' : stone (đá lăn)
# 'X' : moving wall 
LEVELS = [
    [
        "####################",   # Level 1
        "#..................#",
        "#..................#",
        "#..................#",
        "#..................#",
        "#.P................#",
        "#..................#",
        "#..C.M......L....F.#",
        "#GGG............HHH#",
        "####^^^^^^^^^^^^####",
        "####################",
    ],
    [
        "....................",    # Level 2
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "..P.................",
        "....................",
        "S.................MC",
        "#######BBBB#########",
    ],    
    [
        "...........O.......O",    # Level 3 room 1
        "...........O.......O",
        "...........O.......O",
        "...........O.......O",
        "OOOOO......O.......O",
        "OOOOO++++++O.......O",
        "OOOOO~~~~~~O.......O",
        "OOOOO~~~~~~O.....C.O",
        "OOOOO~~~~~~O~~~~OOOO",
        "OOOOO~~~~~~O~~~~OOOO",
        "EEEEEEEEEEEE~~~~~~~~"
    ],
    [
        "......OOOOOOOOO...OO",
        "......OOOOOOOOO...OO",
        "......OOOOOOOOO...OO",
        "OOOOO+++++++++++++++E",###Đi về bên phải map này là đến map của cái Ánh
        "OOOOO~~~~~~~~~~~~~~~E",
        "OOOOO~~~~~~~~~~~~~~~E",
        "OOOOO~~~~~~~~~~~~OOO",
        "OOOOO~~~~~~~~~~~~OOO",
        "OOOOO~~~~~~~~~~~~OOO",
        "OOOOO~A~A~A~A~A~~OOO",
    ],
    [ 
        "..##################",
        "..TT##vv##v#v###vvv#",
        "..TTTATTvTTTTvTvTTTT",
        "..T^##TTTTT*TTTT***#", 
        "..TT##**T*T#T*T*####", 
        "..T^####T#T#T#T#####", 
        "..TT################",
        "..T^################", 
        "..PT################", 
        "..TT################"
    ]
        
]
LEVEL_BGS = [
    asset("bg-1.png"),
    asset("bg-2.png"),
    asset("bg-3.png"),
    asset("bg-1.png"),
    asset("bg-2.png")
]