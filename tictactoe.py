import numpy as np


class ttt_board(object):
    
    def __init__(self):
        self.spaces = ['_'] * 9
        
    def __str__(self):
        # Allow for printing of board in human-readable format
        return '%s\n%s\n%s\n' % (' '.join(self.spaces[:3]), ' '.join(self.spaces[3:6]), ' '.join(self.spaces[6:]))
    
    def update(self, ix, mark):
        """
        Updates the board with a new X or O.
        """
        self.spaces[ix] = mark

    
class ttt_player(object):
    
    def __init__(self, player_type, mark, epsilon=.9, alpha=.1):
        self.player_type = player_type
        self.mark = mark
        self.board_vals = [2**i for i in range(9)]
        if player_type == 'computer':
            self.policy = dict()
            self.alpha = alpha            # learning rate
            self.epsilon = epsilon        # exploration rate
            self.prev_state = None
    
    
    def __str__(self):
        return 'Player %s' % self.mark
    
    
    def set_epsilon(self, epsilon):
        """
        Sets the player's exploration rate. This is the rate at which the player explores move options that
        *don't* have the highest win probability based on the player's current policy.
        """
        self.epsilon = epsilon
    
    
    def set_alpha(self, alpha):
        """
        Sets the player's learning rate. This indicates how much the player should adjust its win probabilities
        based on new information.
        """
        self.alpha = alpha
    
    
    def get_player_total(self, state):
        """
        Returns a total for each player based on values I've assigned to each space on the board.
        This enables us to easily know if someone has won the game.
        """
        total = 0
        for i, x in enumerate(state):
            if x == self.mark:
                total += self.board_vals[i]
        return total
    
    
    def get_move_outcome(self, state):
        """
        Informs the player that the given state is a win, draw, or none of the above. Uses bitwise operations to
        translate the board state into an indication of a win. See explanation here:
        http://mamallamacoding.blogspot.com/2014/03/making-tictactoe-with-object-oriented.html
        """
        win_totals = [7, 56, 448, 73, 146, 292, 273, 84]
        total = self.get_player_total(state)
        for val in win_totals:
            if total & val == val: # bitwise operation!
                return 'win'
        if '_' not in state:
            return 'draw'
        return None
    
    
    def get_prob_from_policy(self, state):
        """
        This function returns a player's current understanding of its probability of winning from a given
        board state. If the player has never seen this state before, the function fills the player's policy with
        a 1 if it's a win state (e.g. three X's in a row), a .5 if it's a draw state, or a .5 if it's an unknown
        state prior to the end of the game.
        
        (A player will never store a lose state in its policy [e.g. three O's in a row if you are player X] 
        because the player will not make any more moves after it has lost.)
        """
        state = tuple(state)
        if state in self.policy:
            return self.policy[state]
        
        outcome = self.get_move_outcome(state)
        if outcome == 'win':
            self.policy[state] = 1
        elif outcome == 'draw':
            self.policy[state] = .5
        else:                       # Fill with .5 if winner hasn't been decided yet
            self.policy[state] = .5
        return self.policy[state]

                                   
    def update_policy(self, current_win_prob):
        """
        Updates the win probability of a previous state based on the win probability of the current state.
        """
        prev_state = tuple(self.prev_state)
        prev_win_prob = self.policy[prev_state]
        self.policy[prev_state] = round(prev_win_prob + self.alpha*(current_win_prob - prev_win_prob), 5)
        
        
    def get_move(self, board, print_output):
        """
        Gets a move from a human or computer player.
        returns: index of the board space that the player wants to make an X or O in (ix from 0-8)
        """
        if self.player_type == 'human':
            while True:
                try:
                    row_index, col_index = eval(raw_input( \
                                "Enter the row and column you want to make a mark in, using the format x,y "))
                    # Get correct index in the board list, adjusting for 0-indexing
                    move_index = (row_index-1)*3 + col_index - 1
                    if board.spaces[move_index] == '_':
                        return move_index
                except:
                    pass
                print "Invalid move.\n"
        
        # Make Computer player decision
        state = board.spaces[:]
        possible_move_indices = [i for i, x in enumerate(state) if x == '_']
        
        if np.random.uniform() < self.epsilon:     # randomly choose a move with probability = epsilon
            move_index = np.random.choice(possible_move_indices)
            next_state = state[:]
            next_state[move_index] = self.mark
            _ = self.get_prob_from_policy(next_state) # I don't use the result, but this function fills the
                            # policy with a win probability for this state if this state key doesn't already exist
        
        else:               # Choose the best known move with probability = 1-epsilon
            max_prob = 0
            best_move_ixs = []
            for i in possible_move_indices:
                potential_state = state[:]
                potential_state[i] = self.mark
                prob = self.get_prob_from_policy(potential_state)                
                if prob > max_prob:
                    best_move_ixs = [i]
                    max_prob = prob
                elif prob == max_prob:
                    best_move_ixs.append(i)
            if print_output:
                print 'best move ixs: ', best_move_ixs
                print 'max_prob: ', max_prob
            move_index = np.random.choice(best_move_ixs)
            if self.prev_state:
                self.update_policy(max_prob)  

        self.prev_state = state
        self.prev_state[move_index] = self.mark
        return move_index
                            
            
# Game object instantiates the board and human or CPU players
class ttt_game(object):
    
    def __init__(self, playerX, playerO, print_output = True):
        self.board = ttt_board()
        if isinstance(playerX, ttt_player):
            if playerX.mark == 'X':
                self.playerX = playerX
                self.playerX.prev_state = None
            else:
                raise ValueError('playerX must have player mark "X".')
        elif playerX == 'human':
            self.playerX = ttt_player('human', 'X')
        elif playerX == 'computer':
            self.playerX = ttt_player('computer', 'X')
        else:
            raise ValueError('playerX must be a ttt_player object, or it must be a string indicating "human" or "computer."')
          
        if isinstance(playerO, ttt_player):
            if playerO.mark == 'O':
                self.playerO = playerO
                self.playerO.prev_state = None
            else:
                raise ValueError('playerO must have player mark "O".')
        elif playerO == 'human':
            self.playerO = ttt_player('human', 'O')
        elif playerO == 'computer':
            self.playerO = ttt_player('computer', 'O')
        else:
            raise ValueError('playerO must be a ttt_player object, or it must be a string indicating "human" or "computer."')
               
        self.playerX_score = []
        self.playerO_score = []
        self.current_player = self.playerX
        self.print_output = print_output
        
        
    def set_print(self, print_output):
        """
        Sets the print_output attribute. If True, ttt_game will print the board at each move, say whose turn
        it is, and state the outcome of each game.
        print_output: True or False
        """
        self.print_output = print_output
    
    
    def take_a_turn(self):
        """
        Asks the current player to select its next move.
        """
        if self.print_output:
            print "%s's turn:" % self.current_player
        move_index = self.current_player.get_move(self.board, self.print_output)
        self.board.update(move_index, self.current_player.mark)
        if self.current_player == self.playerX:
            self.current_player = self.playerO
        else:
            self.current_player = self.playerX
        if self.print_output:
            print self.board
        
        
    def game_outcome(self):
        """
        Returns information on wins or ties, or returns None if the game is not yet over.
        """
        state = self.board.spaces
        win_totals = [7, 56, 448, 73, 146, 292, 273, 84]
        X_total = self.playerX.get_player_total(state)
        O_total = self.playerO.get_player_total(state)
        for val in win_totals:
            if X_total & val == val:        # Bitwise operation!
                self.playerX_score.append(1)
                self.playerO_score.append(0)
                return 'Player X wins!'
            if O_total & val == val:
                self.playerO_score.append(1)
                self.playerX_score.append(0)
                return 'Player O wins!'
        if '_' not in state:
            self.playerX_score.append(.5)
            self.playerO_score.append(.5)
            return 'The game is a tie!'
        return None

                                   
    def send_game_end_signal(self, outcome):
        """
        The "current player" is the player who took the penultimate turn. We send that player information on
        the game outcome, so that player can adjust its policy.
        """
        penultimate_player = self.current_player
        if outcome == 'The game is a tie!':
            win_prob = .5
        else:
            win_prob = 0
        if penultimate_player.player_type == 'computer':
            penultimate_player.update_policy(win_prob)   
    
    
    def play(self):
        """
        Plays a game of tic tac toe.
        """
        if self.print_output:
            print self.board
        outcome = self.game_outcome()
        while not (outcome):
            self.take_a_turn()
            outcome = self.game_outcome()
        self.send_game_end_signal(outcome)
        if self.print_output:
            print outcome
      
    
    def reset(self):
        """
        Resets board and certain player attributes in preparation for a new game.
        """
        self.board = ttt_board()
        self.playerX.prev_state = None
        self.playerO.prev_state = None
        self.current_player = self.playerX

     
    def get_player_score(self, player):
        """
        Returns all scores (win statistics) for the given player.
        player: string indicating 'playerX' or 'playerO'
        """
        if player == 'playerX':
            return self.playerX_score
        if player == 'playerO':
            return self.playerO_score
        raise ValueError('player should be either "playerX" or "playerO"')

            