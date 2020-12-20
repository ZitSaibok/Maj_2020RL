import sys
import json
import random
from utils import FanCalculator

if __name__ == '__main__':

    hand = []
    pack = []  # 副露
    pool = [[], [], [], []]  # 牌池
    wall = [21, 21, 21, 21]

    inputRAW = sys.stdin.readline()
    inputJSON = json.loads(inputRAW)
    turnID = len(inputJSON['responses'])

    request = inputJSON['requests']
    response = inputJSON['responses']
    request.append(inputJSON['requests'][turnID])

    if turnID < 2:
        response.append('PASS')
    else:
        itmp, myPlayerID, quan = request[0].split(' ')
        itmp, myPlayerID, quan = int(itmp), int(myPlayerID), int(quan)  # 0，门风，圈风

        hand = request[1].split(' ')[5:]  # 手牌

        lastReq = req = []
        for i in range(2, turnID):
            req = request[i].split(' ')
            if int(req[0]) == 2:  # 摸牌
                hand.append(req[1])
                wall[myPlayerID] -= 1

                # hand.remove(response[i].split(' ')[1])
            elif int(req[0]) == 3:  # 打/鸣牌
                playerID = int(req[1])

                if req[2] == 'DRAW':
                    wall[playerID] -= 1

                elif req[2] == 'PLAY':
                    if playerID == myPlayerID:
                        hand.remove(req[3])
                    pool[playerID].append(req[3])

                elif req[2] == 'CHI':
                    if playerID == myPlayerID:
                        in_tile = lastReq[-1]
                        if in_tile < req[3]:
                            in_tile = 1
                        elif in_tile == req[3]:
                            in_tile = 2
                        else:
                            in_tile = 3
                        pack.append(['CHI', req[3], in_tile])
                        hand.remove(req[4])
                        for pos in range(3):
                            if pos + 1 == in_tile:
                                continue
                            hand.remove(req[3][0] + str(int(req[3][1]) - 1 + pos))
                    pool[playerID].append(req[4])

                elif req[2] == 'PENG':
                    if playerID == myPlayerID:
                        in_palyer = (myPlayerID - int(lastReq[1]) + 4) % 4
                        in_tile = lastReq[-1]
                        pack.append(['PENG', in_tile, in_palyer])
                        hand.remove(req[3])
                        hand.remove(in_tile)
                        hand.remove(in_tile)
                    pool[playerID].append(req[3])

                elif req[2] == 'GANG':
                    if playerID == myPlayerID:
                        in_palyer = (myPlayerID - int(lastReq[1]) + 4) % 4
                        in_tile = lastReq[-1]
                        pack.append(['GANG', in_tile, in_palyer])
                        hand.remove(in_tile)
                        hand.remove(in_tile)
                        hand.remove(in_tile)
                    

                elif req[2] == 'BUGANG':
                    if playerID == myPlayerID:
                        for pack_id in range(len(pack)):
                            if pack[pack_id][1] == req[3]:
                                pack[pack_id][0] = 'GANG'
                                hand.remove(req[3])
                                break
                    
            lastReq = req

        newReq = request[turnID].split(' ')
        itmp = int(newReq[0])


        ################### strategy begin ###################
        #### step1: HU strategy ####
        # 自摸/杠开
        result = ()
        if itmp == 2:
            isJUEZHANG = sum(pool, []).count(newReq[-1]) == 3
            isLAST = wall[(myPlayerID + 1) % 4] == 0
            result = FanCalculator(pack=pack,
                                   hand=hand,
                                   winTile=newReq[-1],
                                   isZIMO=True,
                                   isJUEZHANG=isJUEZHANG,
                                   isGANG=lastReq[0] == 3 and lastReq[1] == myPlayerID,
                                   isLAST=isLAST,
                                   menFeng=myPlayerID,
                                   quanFeng=quan)

        # 胡/抢杠
        elif itmp == 3 and int(newReq[1]) != myPlayerID and newReq[2] in ['CHI', 'PENG', 'PLAY', 'BUGANG']:
            isJUEZHANG = sum(pool, []).count(newReq[-1]) == 3
            isLAST = wall[(int(newReq[1]) + 1) % 4] == 0
            result = FanCalculator(pack=pack,
                                   hand=hand,
                                   winTile=newReq[-1],
                                   isZIMO=False,
                                   isJUEZHANG=isJUEZHANG,
                                   isGANG=newReq[2] == 'BUGANG',
                                   isLAST=isLAST,
                                   menFeng=myPlayerID,
                                   quanFeng=quan)

        fan = 0
        for fanZhong in result:
            fan += fanZhong[0]
        #### step2: CHI/PONG/GANG strategy ####

        #### step3: PLAY strategy ####
        if fan >= 8:
            response.append('HU')
        elif itmp == 2:
            random.shuffle(hand)
            response.append('PLAY ' + hand.pop())
        else:
            response.append('PASS')
        ################### strategy end ###################

    outputJSON = json.dumps({'response': response[turnID]})
    sys.stdout.write(outputJSON)
