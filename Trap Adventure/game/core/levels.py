from config import asset
# kí hiệu cho các loại ô trong level
# '#' : solid block
# '.' : không gian trống
# 'P' : vị trí xuất hiện của player
# 'M' : moving platform
# 'L' : moving platform 
# '^', 'v', '<', '>' : spike
# 'C' : checkpoint
# 'F' : fake checkpoint
# 'D' : delay checkpoint
# 'H' : hidden spike 
# 'G' : hidden spike 
# 'N' : fake block
# '+' : tide (sóng)
# '~' : water (nước)
# 'W' : wall (tường rắn)
# 'O' : connected block
# 'B' : half block
# 'S' : stone (đá lăn)
# 'X' : moving wall 
# 'Q' : switch
LEVELS = [
    [
        "####################",   # Level 1
        "#..................#",
        "#..................#",
        "#..................#",
        "#..................#",
        "#.P................#",
        "#D.................#",
        "#....M......L....F.#",
        "#GGG............HHH#",
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
        "OOOOO.A.A.A.A.A.AOOO",
    ],
    [ 
        "####################",
        "##vv##vv#v##v#######",
        "##...........v......E",
        "#R.<##.....^....Q..#", 
        "##..##^^.^.#.N..####", 
        "#R.<####.#.#.N.#####", 
        ".P..#########N######",
        "#R..<########N######", 
        "##..NNNNNNNNNN######", 
        "####################"
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
        "OOOOO......O.P..OOOO",
        "####################"
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