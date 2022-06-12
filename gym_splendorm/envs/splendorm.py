import gym
import random
import numpy
import json
from colorama import Fore, Style
from gym_splendorm.envs.base.board import Board
from gym_splendorm.envs.agents import agent_interface

class splendormEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        with open('gym_splendorm/envs/action_space.json') as f:
            self.full_action = json.load(f)

        self.board = Board()
        self.turn = None
        self.amount_player = None
        self.players = None
        self.dict_input = None

    def reset(self):
        self.board.reset()
        self.turn = 0
        self.amount_player = min(agent_interface.list_players.__len__(), 4)
        self.adjust_starting_stocks(self.amount_player)
        self.players = random.sample(agent_interface.list_players, k=self.amount_player)
        for p in self.players:
            p.reset()

        self.dict_input = {
            'Turn': self.turn,
            'Board': self.board,
            'Players': [self.players[(self.turn+1+i)%self.amount_player] for i in range(self.amount_player-1)],
            'End_game': False,
        }

    def render(self, mode='human', close=False):
        # print('----------------------------------------------------------------------------------------------------')
        # print('Turn:', self.turn, 'Board stocks:', self.board.stocks)
        for k in [3,4,5]:
            # print(f'card level {k-2}:', self.board.normal_cards[k], end=' ')
            pass
        
        # print('card noble:', self.board.noble_cards)
        for p in self.players:
            # print(p.name, p.score, p.A_point, p.stocks, p.stocks_const, p.opened_cards, p.upside_cards)
            pass

    def close(self):
        if (self.turn+1) % self.amount_player == 0 and self.board.infinity_card[1] != None:
            self.dict_input['End_game'] = True
            return True

        self.turn += 1
        self.dict_input['Turn'] = self.turn
        self.dict_input['Players'] = [self.players[(self.turn+1+i)%self.amount_player] for i in range(self.amount_player-1)]
        return False

    def step(self, action_player):
        current_player = self.players[self.turn % self.amount_player]
        try:
            action = self.full_action[action_player]
        except:
            action = action_player.copy()
        
        if action[0] == 1: # Lấy nguyên liệu
            if self.check_get_stocks(current_player, numpy.array(action[1]), numpy.array(action[2])):
                self.get_stocks(current_player, numpy.array(action[1]), numpy.array(action[2]))
                
        elif action[0] == 2: # Lấy thẻ
            if self.check_get_card(current_player, action[1], numpy.array(action[2])):
                self.get_card(current_player, action[1], numpy.array(action[2]))
                
        elif action[0] == 3: # Úp thẻ
            if self.check_upside_card(current_player, action[1], numpy.array(action[2])):
                self.upside_card(current_player, action[1], numpy.array(action[2]))

        else:
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: tham số chỉ định hành động không đúng', Style.RESET_ALL)
            input()
            pass
        
        return None, None, self.close(), None

    # ****************************************************************************************************
    
    def upside_card(self, current_player, card_id, stocks_return):
        # Nhận nguyên liệu vàng
        if self.board.stocks[5] > 0:
            current_player._Player__stocks[5] += 1
            self.board._Board__stocks[5] -= 1
        
        # Trả nguyên liệu nếu thừa
        if sum(current_player.stocks) > 10:
            current_player._Player__stocks[:6] -= stocks_return
            self.board._Board__stocks[:6] += stocks_return

        # Thêm vào chồng thẻ úp
        if card_id in [100,200,300]:
            current_player._Player__upside_cards.append(self.board._Board__normal_cards[int(card_id/100)-1].pop())
            # print(Fore.LIGHTGREEN_EX, current_player.name, f'úp thẻ ẩn cấp {int(card_id/100)}', Style.RESET_ALL)
        
        else:
            for k in [3,4,5]:
                if card_id in self.board.normal_cards[k]:
                    current_player._Player__upside_cards.append(card_id)
                    self.board._Board__normal_cards[k].remove(card_id)
                    # print(Fore.LIGHTGREEN_EX, current_player.name, 'úp thẻ', card_id, Style.RESET_ALL)
                    try:
                        self.board._Board__normal_cards[k].append(self.board._Board__normal_cards[k-3].pop())
                    except:
                        pass

                    break

    def check_upside_card(self, current_player, card_id, stocks_return):
        if current_player.upside_cards.__len__() == 3:
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: không thể úp thêm thẻ nữa do đã có 3 thẻ đang úp', Style.RESET_ALL)
            input()
            return False
        
        if card_id in [100,200,300]:
            if self.board.normal_cards[int(card_id/100)-1].__len__() == 0:
                # print(Fore.LIGHTRED_EX, current_player.name, f'lỗi không còn thẻ ẩn cấp {int(card_id/100)} để mà úp', Style.RESET_ALL)
                input()
                return False

        else:
            if card_id not in (self.board.normal_cards[3] + self.board.normal_cards[4] + self.board.normal_cards[5]):
                # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: úp thẻ không xuất hiện trên bàn chơi', Style.RESET_ALL)
                input()
                return False

        pl_st_after = current_player.stocks.copy()
        if self.board.stocks[5] > 0:
            pl_st_after[5] += 1

        if sum(pl_st_after) > 10:    
            pl_st_after[:6] -= stocks_return

        if (pl_st_after < 0).any() or sum(pl_st_after) > 10:
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: trả chưa đủ nguyên liệu hoặc trả nguyên liệu không có', Style.RESET_ALL)
            input()
            return False

        return True

    def get_card(self, current_player, card_id, stocks_return):
        # Trả nguyên liệu
        player_stocks = current_player.stocks[:5]
        card_infor = self.board.cards_infor[card_id]
        card_price = card_infor[-5:]
        nl_bo_ra = (card_price > current_player.stocks_const) * (card_price - current_player.stocks_const)
        nl_bt = numpy.minimum(nl_bo_ra, player_stocks)
        nl_auto = sum(nl_bo_ra - nl_bt)

        current_player._Player__stocks[:5] -= nl_bt
        current_player._Player__stocks[5] -= nl_auto
        self.board._Board__stocks[:5] += nl_bt
        self.board._Board__stocks[5] += nl_auto
        if card_id >= 71 and card_id <= 90:
            if current_player.stocks[6] == 0 and (card_price <= current_player.stocks_const).all() and sum(current_player.stocks) == 10:
                current_player._Player__stocks[:6] -= stocks_return
                self.board._Board__stocks[:6] += stocks_return

        # print(Fore.LIGHTGREEN_EX, current_player.name, 'lấy thẻ:', card_id, 'trả nguyên liệu thường:', nl_bt, 'nguyên liệu auto:', nl_auto, Style.RESET_ALL)

        # Nhận thẻ
        try:
            current_player._Player__upside_cards.remove(card_id)
        except:
            for k in [3,4,5]:
                if card_id in self.board.normal_cards[k]:
                    self.board._Board__normal_cards[k].remove(card_id)
                    try:
                        self.board._Board__normal_cards[k].append(self.board._Board__normal_cards[k-3].pop())
                    except:
                        pass

                    break

        current_player._Player__opened_cards.append(card_id)

        # Time token
        if card_id >= 71 and card_id <= 90 and current_player.stocks[6] == 0:
            current_player._Player__stocks[6] = 1
            self.board._Board__stocks[6] -= 1
            # print(Fore.LIGHTGREEN_EX, current_player.name, 'nhận 1 Time token', Style.RESET_ALL)

        # Stock const, score, A_point
        current_player._Player__stocks_const[card_infor[2]] += 1
        current_player._Player__score += card_infor[0]
        current_player._Player__A_point += card_infor[1]

        # Check thẻ Avenger
        if current_player.A_point > self.board.avenger_card[0]:
            self.board._Board__avenger_card[0] = current_player.A_point
            current_player._Player__score += 3
            if self.board.avenger_card[1] == None:
                self.board._Board__avenger_card[1] = current_player
                # print(Fore.LIGHTGREEN_EX, current_player.name, 'nhận thẻ Avenger', Style.RESET_ALL)
                current_player._Player__avenger_card = True
            else:
                if current_player != self.board._Board__avenger_card[1]:
                    self.board._Board__avenger_card[1]._Player__score -= 3
                    self.board._Board__avenger_card[1]._Player__avenger_card = False
                    # print(Fore.LIGHTGREEN_EX, current_player.name, 'cướp thẻ Avenger từ', self.board.avenger_card[1].name, Style.RESET_ALL)
                    current_player._Player__avenger_card = True
                    self.board._Board__avenger_card[1] = current_player
                else:
                    current_player._Player__score -= 3

        # Check thẻ Noble
        noble_lst = []
        for noble_id in self.board.noble_cards:
            if(self.board.cards_infor[noble_id][-5:] <= current_player.stocks_const).all():
                noble_lst.append(noble_id)
        
        for noble_id in noble_lst:
            self.board._Board__noble_cards.remove(noble_id)
            current_player._Player__opened_cards.append(noble_id)
            current_player._Player__score += 3
        
        # Check thẻ infinity
        if (current_player.stocks_const >= 1).all() and current_player.stocks[6] == 1 and current_player.score > self.board.infinity_card[0]:
            self.board._Board__infinity_card[0] = current_player.score
            if self.board.infinity_card[1] == None:
                self.board._Board__infinity_card[1] = current_player
                # print(Fore.LIGHTGREEN_EX, current_player.name, 'nhận thẻ Infinity', Style.RESET_ALL)
                current_player._Player__infinity_card = True
            else:
                # print(Fore.LIGHTGREEN_EX, current_player.name, 'cướp thẻ Infinity từ', self.board.infinity_card[1].name, Style.RESET_ALL)
                self.board._Board__infinity_card[1]._Player__infinity_card = False
                current_player._Player__infinity_card = True
                self.board._Board__infinity_card[1] = current_player

    def check_get_card(self, current_player, card_id, stocks_return):
        if card_id not in (current_player.upside_cards + self.board.normal_cards[3]
                            + self.board.normal_cards[4] + self.board.normal_cards[5]):
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: mua thẻ không xuất hiện trên bàn chơi hoặc chồng thẻ úp', Style.RESET_ALL)
            input()
            return False
        
        player_stocks = current_player.stocks[:5] + current_player.stocks_const
        card_price = self.board.cards_infor[card_id][-5:]
        if sum((card_price > player_stocks) * (card_price - player_stocks)) <= current_player.stocks[5]: # Đủ nguyên liệu lấy thẻ
            if card_id < 71 or card_id > 90:
                return True

            # Đồng thời xảy ra 3 điều kiện: thẻ cấp 3 đầu tiên, lấy free, tổng số nguyên liệu thường đang là 10
            if current_player.stocks[6] == 0 and (card_price <= current_player.stocks_const).all() and sum(current_player.stocks) == 10:
                if sum(stocks_return) < 1:
                    # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: thẻ cấp 3 đầu tiên lấy miễn phí, tổng số nguyên liệu thường là 10, chưa trả ra 1 nguyên liệu để nhận Time Token', Style.RESET_ALL)
                    input()
                    return False
                
                if ((current_player.stocks[:6] - stocks_return) < 0).any():
                    # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: trả nguyên liệu không có', Style.RESET_ALL)
                    input()
                    return False
            
            return True

        # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: không đủ nguyên liệu lấy thẻ', Style.RESET_ALL)
        input()
        return False
    
    def get_stocks(self, current_player, stocks, stocks_return):
        # Lấy nguyên liệu
        current_player._Player__stocks[:5] += stocks
        self.board._Board__stocks[:5] -= stocks
        # print(Fore.LIGHTGREEN_EX, current_player.name, 'lấy nguyên liệu:', stocks, end='')

        # Trả nguyên liệu
        if sum(current_player.stocks) > 10:
            current_player._Player__stocks[:6] -= stocks_return
            self.board._Board__stocks[:6] += stocks_return
            # print(' trả nguyên liệu:', stocks_return, end='')
        
        # print(Style.RESET_ALL)

    def check_get_stocks(self, current_player, stocks, stocks_return):
        _sum_stocks = sum(stocks)
        if _sum_stocks > 3:
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: lấy quá 3 nguyên liệu', Style.RESET_ALL)
            input()
            return False
        
        if _sum_stocks == 3 and (stocks > 1).any():
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: lấy 3 nguyên liệu tuy nhiên có ít nhất 2 nguyên liệu cùng màu', Style.RESET_ALL)
            input()
            return False

        if _sum_stocks == 2 and (stocks == 2).any() and self.board.stocks[numpy.where(stocks==2)[0][0]] < 4:
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: lấy 2 nguyên liệu cùng màu tuy nhiên không đủ điều kiện trên bàn chơi', Style.RESET_ALL)
            input()
            return False
        
        if ((self.board.stocks[:5] - stocks) < 0).any():
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: lấy nguyên liệu mà bàn chơi không có', Style.RESET_ALL)
            input()
            return False

        pl_st_after = current_player.stocks.copy()
        pl_st_after[:5] += stocks
        if sum(pl_st_after) > 10:
            pl_st_after[:6] -= stocks_return

        if sum(pl_st_after) > 10 or (pl_st_after < 0).any():
            # print(Fore.LIGHTRED_EX, current_player.name, 'lỗi: trả chưa đủ nguyên liệu hoặc trả nguyên liệu không có', Style.RESET_ALL)
            input()
            return False
        
        return True

    def adjust_starting_stocks(self, amount_player):
        if amount_player not in [1,4]:
            self.board._Board__stocks -= numpy.array([1,1,1,1,1,0,1]) * (4-amount_player) + numpy.array([1,1,1,1,1,0,0])