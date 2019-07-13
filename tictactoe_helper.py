from tictactoe import *
import pandas as pd
import warnings

def print_board(state):
    """
    state: list of strings that indicates the board state
    """
    print '%s\n%s\n%s' % (' '.join(state[:3]), ' '.join(state[3:6]), ' '.join(state[6:]))
                          

def train_computer_players(playerX, playerO, n_games=200000, adj_pX_epsilon=True, adj_pO_epsilon=True):
    """
    Trains an "X" computer player and an "O" computer player on n_games of tic tac toe.
    By default, player exploration rate is set high to learn quickly, and then is decreased according
    to the following scheme:
    .9 for first 50% of games, .5 for next 40%, 0.0 for the last 10%
    
    If adj_p_epsilon is set to False, the player's exploration rate will remain as it was before
    calling this function.
    """
    if adj_pX_epsilon:
        playerX.set_epsilon(.75)
    if adj_pO_epsilon:
        playerO.set_epsilon(.75)
    game = ttt_game(playerX, playerO, print_output = False)
    for i in range(1, n_games+1):
        if i/float(n_games) >= .3:
            if i/float(n_games) >= .7:
                if adj_pX_epsilon:
                    playerX.set_epsilon(0)
                if adj_pO_epsilon:
                    playerO.set_epsilon(0)
            else:
                if adj_pX_epsilon:
                    playerX.set_epsilon(.2)
                if adj_pO_epsilon:
                    playerO.set_epsilon(.2)
        game.play()
        game.reset()
    return game
        

def test_computer(computer_player, n_games=3):
    """
    Used when a human wants to evaluate a computer player.
    This function plays n_games with a human versus the computer_player.
    """    
    #computer_player.set_epsilon(0)
    if computer_player.mark == 'X':
        game = ttt_game(computer_player, 'human', print_output=True)
    if computer_player.mark == 'O':
        game = ttt_game('human', computer_player, print_output=True)
    for i in range(n_games):
        game.play()
        game.reset()
        
        
def explore_policy(state, player):
    """
    Given a board state, this function shows all possible next moves for a player and the probability of winning
    from those next moves, according to the player's policy.
    state: list of strings indicating the board state
    player: ttt_player object 
    """
    print_board(state)
    print 'Initial board state\n'
    possible_move_indices = [i for i, x in enumerate(state) if x == '_']
    for i in possible_move_indices:
        potential_state = state[:]
        potential_state[i] = player.mark        
        print_board(potential_state)
        print 'Win probability = %.17f\n' % player.policy[tuple(potential_state)]
    
    
def compute_player_stats(game, player, n_groups=100):
    scores = pd.DataFrame(game.get_player_score(player))
    scores.columns = ['score']
    scores['win_draw'] = (scores.score != 0).astype(int)
    group_size = len(scores)/n_groups
    if group_size == 0:
        warnings.warn('This player has fewer scores than n_groups. Scores will not be aggregated.')
        group_size = 1
    scores_agg = scores.groupby(scores.index/group_size).win_draw.aggregate(lambda x: x.sum()/float(x.shape[0]))
    return scores, scores_agg
