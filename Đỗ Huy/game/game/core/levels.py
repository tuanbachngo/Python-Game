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
        "O..................O",
        "O..................O",
        "O..................O",
        "O..................O",
        "O.P................O",
        "OD.................O",
        "O....M......L....F.O",
        "OGGG............HHHO",
        "####^^^^^^^^^^^^####",
        "####################",
    ],
    [
        "####################",    # Level 2
        "#..................#",
        "#..................#",
        "#..................#",
        "#..................#",
        "...................#",
        "..P................#",
        "....................",
        "S.................XC",
        "#########BB#########",
    ],    
    [
        "...........O.......O",    # Level 3 room 1
        "...........O.......O",
        "...........O.......O",
        "...........O.......O",
        "OOOOO......O.......O",
        "OOOOO......O.....C.O",
        "OOOOO......O....BBBO",
        "OOOOO......O....OOOO",
        "OOOOO......O....OOOO",
        "OOOOO.....~O....OOOO",
        "EEEEEEEEEEEE"
    ],
    [
        "......OOOOOOOOO...OO",
        "......OOOOOOOOO...OO",
        "...........~........E",
        "OOOOO...............E",
        "OOOOO...............E",
        "OOOOO...............E",
        "OOOOO............OOO",
        "OOOOO............OOO",
        "OOOOO............OOO",
        "OOOOO.A.A.A.A....OOO",
    ],
    [ 
        "####################",
        "##..##vv#v##v###vvv#",
        "##......v....v......E",
        "#R.<##..........^^^#", 
        "##..##^^.^.#.^.^####", 
        "#R.<####.#.#.#.#####", 
       "#.P..################",
        "#R..<###############", 
        "##^^################", 
        "####################",
        "..EEEEEEEEE"
    ],
    [
        "...........O.......O",    # Level 3 room 1
        "...........O.......O",
        "..........~O.......O",
        "...........O.......O",
        "OOOOO......O.......O",
        "OOOOO......O.....C.O",
        "OOOOO......O....BBBO",
        "OOOOO......O....OOOO",
        "OOOOO......O....OOOO",
        "OOOOO......O....OOOO",
    ]
]
LEVEL_BGS = [
    asset("bg-1.png"),
    asset("bg-2.png"),
    asset("bg-3.png"),
    asset("bg-1.png"),
    asset("bg_sea.png"),
    asset("bg-3.png")

]
