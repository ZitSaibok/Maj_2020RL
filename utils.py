from MahjongGB import MahjongFanCalculator


def FanCalculator(pack, hand, winTile, isZIMO, isJUEZHANG, isGANG, isLAST, menFeng, quanFeng):
    for i in range(len(pack)):
        pack[i] = tuple(pack[i])
    try:
        result = MahjongFanCalculator(tuple(pack), tuple(hand), winTile, 0, isZIMO, isJUEZHANG, isGANG, isLAST, menFeng, quanFeng)
    except:
        result = ()
    return result
