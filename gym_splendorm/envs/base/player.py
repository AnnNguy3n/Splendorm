import itertools
import numpy
import json
import pandas

class Player:
    def __init__(self, name):
        self.__name = name
        with open('gym_splendorm/envs/action_space.json') as f:
            self.__full_action = json.load(f)

        self.__cards_infor = [[]]
        # Đọc thẻ thường: 1 -> 90
        data = pandas.read_csv('gym_splendorm/envs/base/cards_information/normal_cards.csv')
        for i in range(data.__len__()):
            temp = data.loc[i]
            self.__cards_infor.append(
                numpy.array(
                    [
                        int(temp['score']), # score
                        int(temp['A point']), # A point
                        ['yellow', 'blue', 'orange', 'red', 'purple'].index(temp['type of stock']) # type stock
                    ] + [int(a) for a in temp['price'].split(',')] # yellow, blue, orange, red, purple
                )
            )
        
        # Đọc thẻ Noble: 91 -> 98
        data = pandas.read_csv('gym_splendorm/envs/base/cards_information/noble_cards.csv')
        for i in range(data.__len__()):
            temp = data.loc[i]
            self.__cards_infor.append(
                numpy.array(
                    [
                        (int(temp['score'])), # score
                    ] + [int(a) for a in temp['price'].split(',')] # yellow, blue, orange, red, purple
                )
            )
        
        self.__amount_action = self.__full_action.__len__()
        self.__score = None
        self.__A_point = None
        self.__stocks = None
        self.__stocks_const = None
        self.__opened_cards = None
        self.__upside_cards = None
        self.__avenger_card = None
        self.__infinity_card = None

    def reset(self):
        # ----------------------------------------------------------------------------------------------------
        self.__score = 0
        self.__A_point = 0

        # ----------------------------------------------------------------------------------------------------
        self.__stocks = numpy.array(
            [
                0, # yellow
                0, # blue
                0, # orange
                0, # red
                0, # purple
                0, # auto-color (gray)
                0  # time token (green)
            ]
        )

        # ----------------------------------------------------------------------------------------------------
        self.__stocks_const = numpy.array(
            [
                0, # yellow
                0, # blue
                0, # orange
                0, # red
                0  # purple
            ]
        )

        # ----------------------------------------------------------------------------------------------------
        self.__opened_cards = [] # bao gồm thẻ thường, thẻ quý'ss tộc'ss
        self.__upside_cards = [] # chỉ bao gồm thẻ thường
        self.__avenger_card = False
        self.__infinity_card = False

    @property
    def name(self):
        return self.__name

    @property
    def cards_infor(self):
        return self.__cards_infor.copy()

    @property
    def score(self):
        return self.__score

    @property
    def A_point(self):
        return self.__A_point

    @property
    def stocks(self):
        return self.__stocks.copy()

    @property
    def stocks_const(self):
        return self.__stocks_const.copy()

    @property
    def opened_cards(self):
        return self.__opened_cards.copy()

    @property
    def upside_cards(self):
        return self.__upside_cards.copy()

    @property
    def amount_action(self):
        return self.__amount_action
    
    @property
    def avenger_card(self):
        return self.__avenger_card

    @property
    def infinity_card(self):
        return self.__infinity_card

    def convert_player_object_to_dict(self, player):
        return {
            'Name': player.name,
            'Score': player.score,
            'A_point': player.A_point,
            'Stocks': dict(zip(['yellow', 'blue', 'orange', 'red', 'purple', 'auto-color', 'time-token'], list(player.stocks))),
            'Stocks_const': dict(zip(['yellow', 'blue', 'orange', 'red', 'purple'], list(player.stocks_const))),
            'Opened_cards_id': player.opened_cards,
            'Upside_cards_id': player.upside_cards,
            'Own_avenger': player.avenger_card,
            'Own_infinity': player.infinity_card
        }
    
    def convert_board_object_to_dict(self, board):
        if board.avenger_card[1] != None:
            name_1 = board.avenger_card[1].name
        else:
            name_1 = 'No one'
        
        if board.infinity_card[1] != None:
            name_2 = board.infinity_card[1].name
        else:
            name_2 = 'No one'

        return {
            'Stocks': dict(zip(['yellow', 'blue', 'orange', 'red', 'purple', 'auto-color', 'time-token'], list(board.stocks))),
            'Dict_cards_id_show': {
                'I': board.normal_cards[3],
                'II': board.normal_cards[4],
                'III': board.normal_cards[5],
                'Noble': board.noble_cards
            },
            'Avenger_owner': name_1,
            'Highest_current_A_point': board.avenger_card[0],
            'Infinity_owner': name_2,
            'Highest_current_score': board.infinity_card[0],
        }

    def convert_card_id_to_dict(self, card_id):
        card_infor = self.cards_infor[card_id]
        if card_id >= 1 and card_id <= 90:
            return {
                'Type': 'normal',
                'Card_id': card_id,
                'Score': card_infor[0],
                'A_point': card_infor[1],
                'Type_stock': ['yellow', 'blue', 'orange', 'red', 'purple'][card_infor[2]],
                'Price': dict(zip(['yellow', 'blue', 'orange', 'red', 'purple'], list(card_infor[-5:])))
            }
        elif card_id > 90 and card_id <= 98:
            return {
                'Type': 'noble',
                'Card_id': card_id,
                'Score': card_infor[0],
                'Price': dict(zip(['yellow', 'blue', 'orange', 'red', 'purple'], list(card_infor[-5:])))
            }
        
        else:
            return {}

    def get_list_index_action(self, state):
        list_index_action = []

        # Lấy các thông tin từ state
        self_st = numpy.array(state[7:14])
        self_st_const = numpy.array(state[143:148])
        normal_cards = state[44:-32]
        board_stocks = numpy.array(state[:7])

        # Check mua thẻ
        cards_check_buy = [i+1 for i in range(90) if normal_cards[i] in [-1,4]]
        cards_can_buy = []
        for card_id in cards_check_buy:
            card_price = self.cards_infor[card_id][-5:]
            if sum((card_price > (self_st[:5] + self_st_const)) * (card_price - self_st[:5] - self_st_const)) <= self_st[5]:
                cards_can_buy.append(card_id)

        # mua thẻ, index action: 0->89, không trả
        for card_id in cards_can_buy:
            if card_id < 71 or card_id > 90:
                list_index_action.append(card_id-1)
            else:
                if self_st[6] == 0 and (self.cards_infor[card_id][-5:] <= self_st_const).all() and sum(self_st) == 10: # Mua thẻ 3 free nhưng cần trả nguyên liệu: 1227->1346
                    st_can_return = numpy.where(self_st[:6] > 0)[0]
                    for st_id in st_can_return:
                        list_index_action.append((card_id-71)*6+st_id+1227)
                else:
                    list_index_action.append(card_id-1)
        
        # Check úp thẻ
        if normal_cards.count(4) < 3:
            cards_can_upside = [i+1 for i in range(90) if normal_cards[i] == -1]
            
            # Check có cần trả nguyên liệu hay không?
            return_stock = False
            if board_stocks[5] > 0 and sum(self_st) == 10:
                return_stock = True

            if return_stock: # úp thẻ trả nguyên liệu, index action: 180->719
                pl_st_after = self_st.copy()
                pl_st_after[5] += 1
                st_can_return = numpy.where(pl_st_after[:6] > 0)[0]

                # Úp thẻ hiện: 180->719
                for card_id in cards_can_upside:
                    for st_id in st_can_return:
                        list_index_action.append((card_id-1)*6+st_id+180)
                
                # Úp thẻ ẩn: I: 721->726, II: 728->733, III: 735->740
                if normal_cards[:40].count(-2) != 0:
                    for st_id in st_can_return:
                        list_index_action.append(721+st_id)
                
                if normal_cards[40:70].count(-2) != 0:
                    for st_id in st_can_return:
                        list_index_action.append(728+st_id)

                if normal_cards[70:90].count(-2) != 0:
                    for st_id in st_can_return:
                        list_index_action.append(735+st_id)

            else: # úp thẻ không trả nguyên liệu, index action: 90->179
                # Úp thẻ hiện: 90->179
                for card_id in cards_can_upside:
                    list_index_action.append(card_id+89)

                # Úp thẻ ẩn: 720, 727, 734
                if normal_cards[:40].count(-2) != 0:
                    list_index_action.append(720)
                if normal_cards[40:70].count(-2) != 0:
                    list_index_action.append(727)
                if normal_cards[70:90].count(-2) != 0:
                    list_index_action.append(734)

        # Lấy nguyên liệu: index action: 741->1226
        st_can_get = numpy.where(board_stocks[:5] > 0)[0]
        if sum(self_st) <= 7: # lấy 3 khác, 2 khác, duy nhất 1, 2 giống, không trả
            num_get = min(3, st_can_get.__len__()) # lấy tối đa 3, không trả
            if num_get != 0:
                get_cases = itertools.combinations(st_can_get, num_get)
                if num_get == 3: # lấy 3 không trả: 741->750
                    for get_case in get_cases:
                        list_index_action.append(741 + self.__full_action[741:751].index([1, [1 if i in get_case else 0 for i in range(5)], [0,0,0,0,0,0]]))

                elif num_get == 2: # lấy 2 khác không trả: 941->950
                    for get_case in get_cases:
                        list_index_action.append(941 + self.__full_action[941:951].index([1, [1 if i in get_case else 0 for i in range(5)], [0,0,0,0,0,0]]))

                else: # num_get = 1, lấy duy nhất 1 không trả: 1091->1095
                    if board_stocks[st_can_get[0]] < 4:
                        list_index_action.append(1091+st_can_get[0])

                # lấy double, không trả: 1121->1125
                st_can_get_double = numpy.where(board_stocks[:5] >= 4)[0]
                for st_id in st_can_get_double:
                    list_index_action.append(1121+st_id)

            else:
                list_index_action.append(1226)

        elif sum(self_st) == 8: # trả 1: lấy 3, không trả: 2 khác, duy nhất 1, double
            num_get = min(2, st_can_get.__len__()) # lấy tối đa 2, không trả
            if num_get != 0:
                if st_can_get.__len__() >= 3: # lấy 3 trả 1: 751->780
                    get_cases = itertools.combinations(st_can_get, 3)
                    for get_case in get_cases:
                        st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i not in get_case]
                        for i in st_can_return:
                            list_index_action.append(751 + self.__full_action[751:781].index([1, [1 if j in get_case else 0 for j in range(5)], [1 if j == i else 0 for j in range(6)]]))

                get_cases = itertools.combinations(st_can_get, num_get)
                if num_get == 2: # lấy 2 khác không trả: 941->950
                    for get_case in get_cases:
                        list_index_action.append(941 + self.__full_action[941:951].index([1, [1 if i in get_case else 0 for i in range(5)], [0,0,0,0,0,0]]))

                else: # num_get = 1, lấy duy nhất 1 không trả: 1091->1095
                    if board_stocks[st_can_get[0]] < 4:
                        list_index_action.append(1091+st_can_get[0])

                # lấy double, không trả: 1121->1125
                st_can_get_double = numpy.where(board_stocks[:5] >= 4)[0]
                for st_id in st_can_get_double:
                    list_index_action.append(1121+st_id)

            else:
                list_index_action.append(1226)
        
        elif sum(self_st) == 9: # trả 2: lấy 3, trả 1: lấy 2 khác, lấy double, không trả: lấy 1 duy nhất
            num_get = min(1, st_can_get.__len__()) # lấy tối đa 1, không trả
            if num_get != 0:
                if st_can_get.__len__() >= 3: # lấy 3 trả 2: 781->840
                    get_cases = itertools.combinations(st_can_get, 3)
                    for get_case in get_cases:
                        # trả 2 nl khác nhau
                        st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i not in get_case]
                        if st_can_return.__len__() >= 2:
                            return_cases = itertools.combinations(st_can_return, 2)
                            for return_case in return_cases:
                                list_index_action.append(781 + self.__full_action[781:841].index([1, [1 if j in get_case else 0 for j in range(5)], [1 if j in return_case else 0 for j in range(6)]]))

                        # trả 2 nl giống nhau
                        st_can_return_double = [i for i in numpy.where(self_st[:6]>1)[0] if i not in get_case]
                        for i in st_can_return_double:
                            list_index_action.append(781 + self.__full_action[781:841].index([1, [1 if j in get_case else 0 for j in range(5)], [2 if j == i else 0 for j in range(6)]]))

                if st_can_get.__len__() >= 2: # lấy 2 khác trả 1: 951->990
                    get_cases = itertools.combinations(st_can_get, 2)
                    for get_case in get_cases:
                        st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i not in get_case]
                        for i in st_can_return:
                            list_index_action.append(951 + self.__full_action[951:991].index([1, [1 if j in get_case else 0 for j in range(5)], [1 if j == i else 0 for j in range(6)]]))
                
                # Lấy duy nhất 1 không trả: 1091->1095
                for st_id in st_can_get:
                    list_index_action.append(1091+st_id)

                # Lấy double trả 1: 1126->1150
                st_can_get_double = numpy.where(board_stocks[:5] >= 4)[0]
                for st_id in st_can_get_double:
                    st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i != st_id]
                    for i in st_can_return:
                        list_index_action.append(1126 + self.__full_action[1126:1151].index([1, [2 if j == st_id else 0 for j in range(5)], [1 if j == i else 0 for j in range(6)]]))

            else:
                list_index_action.append(1226)

        else: # 10nl, lấy 3 trả 3, lấy 2 khác trả 2, lấy 1 trả 1, lấy double trả 2, không lấy gì
            num_get = min(1, st_can_get.__len__())
            if num_get != 0:
                if st_can_get.__len__() >= 3: # lấy 3 trả 3: 841->940
                    get_cases = itertools.combinations(st_can_get, 3)
                    for get_case in get_cases:
                        # trả 3 nl khác nhau
                        st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i not in get_case]
                        if st_can_return.__len__() >= 3:
                            list_index_action.append(841 + self.__full_action[841:941].index([1, [1 if j in get_case else 0 for j in range(5)], [1 if j in st_can_return else 0 for j in range(6)]]))
            
                        # trả kiểu 2 nl loại này 1 nl loại kia
                        st_can_return_2 = [i for i in numpy.where(self_st[:6]>1)[0] if i not in get_case]
                        for st_id_2 in st_can_return_2:
                            st_can_return_1 = [i for i in numpy.where(self_st[:6]>0)[0] if i not in get_case and i != st_id_2]
                            for st_id_1 in st_can_return_1:
                                temp = [0,0,0,0,0,0]
                                temp[st_id_2] = 2
                                temp[st_id_1] = 1
                                list_index_action.append(841 + self.__full_action[841:941].index([1, [1 if j in get_case else 0 for j in range(5)], temp]))
                        
                        # trả 3 nl giống nhau
                        st_can_return_triple = [i for i in numpy.where(self_st[:6]>2)[0] if i not in get_case]
                        for i in st_can_return_triple:
                            list_index_action.append(841 + self.__full_action[841:941].index([1, [1 if j in get_case else 0 for j in range(5)], [3 if j == i else 0 for j in range(6)]]))
                
                if st_can_get.__len__() >= 2: # lấy 2 khác trả 2: 991->1090
                    get_cases = itertools.combinations(st_can_get, 2)
                    for get_case in get_cases:
                        # trả 2 nl khác nhau
                        st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i not in get_case]
                        if st_can_return.__len__() >= 2:
                            return_cases = itertools.combinations(st_can_return, 2)
                            for return_case in return_cases:
                                list_index_action.append(991 + self.__full_action[991:1091].index([1, [1 if j in get_case else 0 for j in range(5)], [1 if j in return_case else 0 for j in range(6)]]))

                        # trả 2 nl giống nhau
                        st_can_return_double = [i for i in numpy.where(self_st[:6]>1)[0] if i not in get_case]
                        for i in st_can_return_double:
                            list_index_action.append(991 + self.__full_action[991:1091].index([1, [1 if j in get_case else 0 for j in range(5)], [2 if j == i else 0 for j in range(6)]]))
                
                # lấy 1 trả 1: 1096->1120
                for st_id in st_can_get:
                    st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i != st_id]
                    for st_id_r in st_can_return:
                        list_index_action.append(1096 + self.__full_action[1096:1121].index([1, [1 if j == st_id else 0 for j in range(5)], [1 if j == st_id_r else 0 for j in range(6)]]))
                
                # lấy double trả 2: 1151:1225
                st_can_get_double = numpy.where(board_stocks[:5] >= 4)[0]
                for st_id in st_can_get_double:
                    # trả 2 nl khác nhau
                    st_can_return = [i for i in numpy.where(self_st[:6]>0)[0] if i != st_id]
                    if st_can_return.__len__() >= 2:
                        return_cases = itertools.combinations(st_can_return, 2)
                        for return_case in return_cases:
                            list_index_action.append(1151 + self.__full_action[1151:1226].index([1, [2 if j == st_id else 0 for j in range(5)], [1 if j in return_case else 0 for j in range(6)]]))
                    
                    # trả 2 nl giống nhau:
                    st_can_return_double = [i for i in numpy.where(self_st[:6]>1)[0] if i != st_id]
                    for i in st_can_return_double:
                        list_index_action.append(1151 + self.__full_action[1151:1226].index([1, [2 if j == st_id else 0 for j in range(5)], [2 if j == i else 0 for j in range(6)]]))

                list_index_action.append(1226)

            else:
                list_index_action.append(1226)

        # return list_index_action
        return [int(ii) for ii in list_index_action]

    def check_victory(self, state):
        if state[-1] == 1:
            if state[43] == 0:
                return 1
            else:
                return 0
        else:
            return -1

    def get_list_state(self, dict_input):
        # Board stocks: 0->6
        board_stocks = list(dict_input['Board'].stocks)

        # Lần lượt, stocks của 4 người chơi, của bản thân đầu tiên: 7->34
        players_stocks = []
        players_stocks = list(self.stocks)
        for p in dict_input['Players']:
            players_stocks += list(p.stocks)

        if players_stocks.__len__() < 28:
            for k in range(int((28-players_stocks.__len__())/7)):
                players_stocks += [0,0,0,0,0,0,0]
        
        # Lần lượt, điểm của 4 người chơi, của bản thân đầu tiên: 35->38
        players_score = [self.score] + [p.score for p in dict_input['Players']]
        while players_score.__len__() < 4:
            players_score.append(0)

        # Lần lượt, điểm Avenger của 4 người chơi, của bản thân đầu tiên: 39->42
        players_A_point = [self.A_point] + [p.A_point for p in dict_input['Players']]
        while players_A_point.__len__() < 4:
            players_A_point.append(0)

        # 43->142
        # 100 phần tử, thẻ thường (1-90), thẻ quý tộc (91-98), thẻ avenger (99) và thẻ infinity (0)
        # Quy ước:
        #     - 0,1,2,3: 0 là thẻ của mình đang ở hữu, 1,2,3 là thẻ mà những người chơi sau mình 1,2,3 turn đang sở hữu
        #     - -1: thẻ đang ở trên bàn chơi, chưa ai sở hữu
        #     - 4,5,6,7: 4 là thẻ của mình đang úp, 5,6,7 là thẻ mà những người chơi sau mình 1,2,3 turn đang úp
        #     - -2: thẻ không hoặc chưa xuất hiện trên bàn chơi
        cards = [-2 for i in range(100)]

        # 1->98: thẻ thường và thẻ quý tộc
        # 0: thẻ infinity
        # 99: thẻ avenger

        for card_id in (dict_input['Board'].normal_cards[3] + dict_input['Board'].normal_cards[4] + dict_input['Board'].normal_cards[5]):
            cards[card_id] = -1

        for card_id in self.opened_cards:
            cards[card_id] = 0
        
        for card_id in self.upside_cards:
            cards[card_id] = 4

        for k in range(dict_input['Players'].__len__()):
            for card_id in dict_input['Players'][k].opened_cards:
                cards[card_id] = k+1
            
            for card_id in dict_input['Players'][k].upside_cards:
                cards[card_id] = k+5

        if dict_input['Board'].avenger_card[1] == None:
            cards[99] = -1 
        else:
            if self.avenger_card:
                cards[99] = 0
            else:
                for k in range(dict_input['Players'].__len__()):
                    if dict_input['Players'][k].avenger_card:
                        cards[99] = k+1
                        break
        
        if dict_input['Board'].infinity_card[1] == None:
            cards[0] = -1
        else:
            if self.infinity_card:
                cards[0] = 0
            else:
                for k in range(dict_input['Players'].__len__()):
                    if dict_input['Players'][k].infinity_card:
                        cards[0] = k+1
                        break

        # Lần lượt, stocks_const của 4 người chơi, của bản thân đầu tiên
        players_stocks_const = list(self.stocks_const)
        for p in dict_input['Players']:
            players_stocks_const += list(p.stocks_const)
        
        if players_stocks_const.__len__() < 20:
            for k in range(int((20-players_stocks_const.__len__())/5)):
                players_stocks_const += [0,0,0,0,0]

        # return board_stocks + players_stocks + players_score + players_A_point + cards + players_stocks_const + [dict_input['Turn'], dict_input['Players'].__len__() + 1, 1 if dict_input['End_game'] else 0]
        return [int(ii) for ii in (board_stocks + players_stocks + players_score + players_A_point + cards + players_stocks_const + [dict_input['Turn'], dict_input['Players'].__len__() + 1, 1 if dict_input['End_game'] else 0])]