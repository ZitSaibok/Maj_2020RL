import sys
import json
import random
from utils import FanCalculator
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    hand = []
    pack = [[], [], [], []]  # 副露
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

        lastReq = req = [-1, -1]
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
                    in_tile = lastReq[-1]
                    if in_tile < req[3]:
                        in_tile = 1
                    elif in_tile == req[3]:
                        in_tile = 2
                    else:
                        in_tile = 3
                    pack[playerID].append(['CHI', req[3], in_tile])
                    if playerID == myPlayerID:
                        hand.remove(req[4])
                        for pos in range(3):
                            if pos + 1 == in_tile:
                                continue
                            hand.remove(req[3][0] + str(int(req[3][1]) - 1 + pos))
                    pool[playerID].append(req[4])
                    pool[int(lastReq[1])].pop()

                elif req[2] == 'PENG':
                    in_player = (playerID - int(lastReq[1]) + 4) % 4
                    in_tile = lastReq[-1]
                    pack[playerID].append(['PENG', in_tile, in_player])
                    if playerID == myPlayerID:
                        hand.remove(req[3])
                        hand.remove(in_tile)
                        hand.remove(in_tile)
                    pool[playerID].append(req[3])
                    pool[int(lastReq[1])].pop()


                elif req[2] == 'GANG':
                    if int(lastReq[0]) == 3:
                        in_player = (playerID - int(lastReq[1]) + 4) % 4
                    else:
                        in_player = myPlayerID
                    in_tile = lastReq[-1]
                    pack[playerID].append(['GANG', in_tile, in_player])
                    if playerID == myPlayerID:
                        hand.remove(in_tile)
                        hand.remove(in_tile)
                        hand.remove(in_tile)
                    if int(lastReq[0]) == 3:
                        pool[int(lastReq[1])].pop()
                    else:
                        hand.remove(in_tile)
                    

                elif req[2] == 'BUGANG':
                    for pack_id in range(len(pack[playerID])):
                        if pack[playerID][pack_id][1] == req[3]:
                            pack[playerID][pack_id][0] = 'GANG'
                            if playerID == myPlayerID:
                                hand.remove(req[3])
                            break
                    
            lastReq = req

        newReq = request[turnID].split(' ')
        itmp = int(newReq[0])
        logging.info('****hand****')
        logging.info(sorted(hand))
        logging.info('****pack****')
        for _ in pack:
            logging.info(_)
        logging.info('****pool****')
        for _ in pool:
            logging.info(_)
        logging.info('****wall****')
        logging.info(wall)

        ################### strategy begin ###################
        #### step1: HU strategy ####
        # 自摸/杠开
        result = ()
        poolAndPack = []
        for player in pack:
            for p in player:
                if p[0] == 'CHI':
                    poolAndPack += [p[1][0] + str(int(p[1][1]) - 1 + pos) for pos in range(3)]
                elif p[0] == 'PENG':
                    poolAndPack += [p[1]] * 3
                elif p[0] == 'GANG':
                    poolAndPack += [p[1]] * 4
        poolAndPack += sum(pool, [])


        if itmp == 2:
            isJUEZHANG = poolAndPack.count(newReq[-1]) == 3
            isLAST = wall[(myPlayerID + 1) % 4] == 0
            result = FanCalculator(pack=pack[myPlayerID],
                                   hand=hand,
                                   winTile=newReq[-1],
                                   isZIMO=True,
                                   isJUEZHANG=isJUEZHANG,
                                   isGANG=int(lastReq[0]) == 3 and int(lastReq[1]) == myPlayerID,
                                   isLAST=isLAST,
                                   menFeng=myPlayerID,
                                   quanFeng=quan)

        # 胡/抢杠
        elif itmp == 3 and int(newReq[1]) != myPlayerID and newReq[2] in ['CHI', 'PENG', 'PLAY', 'BUGANG']:
            isJUEZHANG = poolAndPack.count(newReq[-1]) == 3
            isLAST = wall[(int(newReq[1]) + 1) % 4] == 0
            result = FanCalculator(pack=pack[myPlayerID],
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
        if fan >= 8:
            response.append('HU')
        logging.info('****fan****')
        logging.info(result)
        #### step2: CHI/PENG/GANG strategy ####
        if itmp == 2:
            hand.append(newReq[-1])
        elif itmp == 3 and newReq[2] in ['CHI', 'PENG', 'PLAY']:
            poolAndPack.append(newReq[-1])
        random.shuffle(hand)
        toPlay = hand[0]
        restCount = [4 - poolAndPack.count(tile) - hand.count(tile) for tile in hand]
        handCount = [hand.count(tile) for tile in hand]
        idx = np.argsort(restCount)
        full = False
        for _ in idx:
            if handCount[_] == 1:
                toPlay = hand[_]
                break
            elif handCount[_] == 2 and restCount[_] == 0:
                if full:
                    toPlay = hand[_]
                full = True

        if itmp == 3 and int(newReq[1]) != myPlayerID and newReq[2] in ['CHI', 'PENG', 'PLAY',]:
            if hand.count(newReq[-1]) == 2:
                response.append('PENG ' + toPlay)
            elif hand.count(newReq[-1]) == 3:
                response.append('GANG')
            else:
                response.append('PASS')
        elif itmp == 2:
            if hand.count(newReq[-1]) == 4:
                response.append('GANG ' + newReq[-1])
            else:
                response.append('PLAY ' + toPlay)
                for p in pack[myPlayerID]:
                    if p[0] == 'PENG' and p[1] == newReq[-1]:
                        response[-1] = 'BUGANG' + newReq[-1]
                        break
        else:
            response.append('PASS')


        #### step3: PLAY strategy ####

        ################### strategy end ###################

    outputJSON = json.dumps({'response': response[turnID]})
    sys.stdout.write(outputJSON)
