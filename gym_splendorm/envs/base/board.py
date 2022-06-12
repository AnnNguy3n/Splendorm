import pandas
import random
import numpy


class Board:
    def __init__(self):
        self.name = 'Splendor-Marvel: Board'
        self.__cards_infor = [[]]

        # ----------------------------------------------------------------------------------------------------
        # Đọc thẻ infinity, thẻ điều kiện chiến thắng
        # data = pandas.read_csv('gym_splendorm/envs/base/Cards information/Infinity Card.csv')
        # self.__cards_infor.append(
        #     numpy.array(
        #         [int(a) for a in data.loc[0]['conditions'].split(',')] # score, time, yellow, blue, orange, red, purple
        #     )
        # )

        # ----------------------------------------------------------------------------------------------------
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

        # ----------------------------------------------------------------------------------------------------
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

        # ----------------------------------------------------------------------------------------------------
        # Đọc thẻ avenger: 99
        # data = pandas.read_csv('gym_splendorm/envs/base/Cards information/Avenger Card.csv')
        # temp = data.loc[0]
        # self.__cards_infor.append(
        #     numpy.array(
        #         [int(temp['score']), int(temp['starting point'])]
        #     )
        # )

        self.__stocks = None
        self.__normal_cards = None
        self.__noble_cards = None
        self.__avenger_card = None
        self.__infinity_card = None

    def reset(self):
        # ----------------------------------------------------------------------------------------------------
        # Stocks
        self.__stocks = numpy.array(
            [
                7, # yellow
                7, # blue
                7, # orange
                7, # red
                7, # purple
                5, # auto-color (gray)
                4, # time token (green)
            ]
        )

        # ----------------------------------------------------------------------------------------------------
        # Normal cards
        self.__normal_cards = [
            [i for i in range(1, 41)], # thẻ cấp 1 chưa xuất hiện
            [i for i in range(41, 71)], # thẻ cấp 2 chưa xuất hiện
            [i for i in range(71, 91)], # thẻ cấp 3 chưa xuất hiện
            [], # thẻ cấp 1 hiện tại trên bàn chơi
            [], # thẻ cấp 2 hiện tại trên bàn chơi
            [], # thẻ cấp 3 hiện tại trên bàn chơi
        ]

        for i in range(3):
            random.shuffle(self.__normal_cards[i])
            for j in range(4):
                self.__normal_cards[i+3].append(self.__normal_cards[i].pop())
                
        # ----------------------------------------------------------------------------------------------------
        # noble cards
        self.__noble_cards = [
            random.randint(0,1) + 91 + 2*i for i in range(4)
        ]

        # ----------------------------------------------------------------------------------------------------
        # avenger card
        self.__avenger_card = [2, None]

        # ----------------------------------------------------------------------------------------------------
        # infinity card
        self.__infinity_card = [15, None]

    @property
    def cards_infor(self):
        return self.__cards_infor.copy()
    
    @property
    def stocks(self):
        return self.__stocks.copy()

    @property
    def normal_cards(self):
        return self.__normal_cards.copy()

    @property
    def noble_cards(self):
        return self.__noble_cards.copy()

    @property
    def avenger_card(self):
        return self.__avenger_card.copy()
    
    @property
    def infinity_card(self):
        return self.__infinity_card.copy()