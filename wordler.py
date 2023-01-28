###
#
# A lot of this text below was just getting ideas down to decide how to build it.
# You might want to skip all this and just look at the code.
#
# Possible goals for wordle
# 1. get the word in the least number of guesses (forgetting about the 6-guess limit)
# 2. get the word in six guesses
# 3. both 1 and 2 with priority on 2
#
# We want to compute
# A. the best first word guess for 1, 2, and 3
# B. A, but with/without hard mode
# C. the best guess in any situation
#
# Solutions and Herrings
#
# There are two disjoint sets of words, 2315 solutions and 10657 herrings.  The
# solutions to the daily Wordle only come from solutions and never come from
# herrings, but the player may guess words from both sets.  Words not in either
# set are not allowed as guesses.  The words in solutions are those that are
# commonly known. Those in herrings are either uncommon or plural forms of
# common words.  So, there are few (maybe no) plural words in solutions.
#
# As players, we already have a sense of what words are in solutions and which
# are not.  A possible strategy is to use a herring word that has common or
# distinguishing letters even though we know it can't be a solution.  So, the
# algorithm for finding best guesses needs to consider all words.
#
# One way to compute the best is to simulate all possible games and guesses.
# Given a single solution, there are 12972 first guesses, and for each of those,
# 12971 second guesses, and so on.  If the goal is to find the word in 6 guesses,
# then the sixth guess must be in the solutions set.  So, an upper bound on the
# total number of guesses to simulate all games is 12972 ^ 6 = 4.76e24.  That's
# too big to compute (millions of years of CPU time).  The actual tree of
# guesses is smaller since solutions are forced at earlier guesses.  It might be
# computable, but let's assume we need to be smarter.
#
# At any state of the game, each candidate guess has an expected number of
# guesses to reach the solution and a probability of guessing in 6 or less.
# Let's start with the simplest problem of guessing in 6 in hard mode.  Let's
# make it simpler by ignoring the herrings.
#
# The probability of a guess should not assume that the next guess be random but
# the one with the best probability. Suppose the probability were first computed
# based on random selection.  The probability can only improve if we choose the
# next guess with the best probability.  So, we could iterate on all computations,
# remembering and reusing the best choice in each situation, until the tree
# converges at the top on the best first guess.
#
# Optimal Tree / Policy
#
# What is this final tree?  It is a collection of sequences of best choices for
# each of the 2315 solutions.  The kth depth level of the tree corresponds to
# the kth guess.  Each guess in the tree points to a node with the set of
# remaining candidates.  This is a superset of the solutions that lead
# to this same guess.
#
# Each guess in the tree has a probability of success and an average
# remaining depth for the cases that are successful.  So the number of nodes in
# this tree is less than 2315 * 5.
#
# Search State
#
# What are the necessary ingredients for a search state?  If in the context of
# a particular solution, the solution is part of the state.  In combination with
# the solution, choices include
# 1. The list of previous guesses
# 2. The set of previous guesses
# 3. The set of remaining candidate words
# 4. How many guesses so far
# 5. The letters matched in correct position
# 6. The letters matched but not in correct position
# 7. Letters not in solution
#
# Given that the feedback for each guess is independent of previous guesses,
# choice 2 is superior to 1.  Everything after choice 2 can be computed from 2.
# However, note that two sets of guesses could lead to the same remaining
# words.  For example, two alternative guesses, "crate" and "trace" would
# eliminate the same set words if all letters were mismatches.  So, while the
# choice 2 representation is compact, its states are not unique given a
# particular solution.
#
# Is the set of remaining candidates enough information by itself to determine
# the best next guess?  Spoiler: yes if combined with the number of guesses so
# far.
#
# It would be if the words that were eliminated by the
# next guess did not need to be informed by previous guesses.  Let's say "geese"
# is the unknown solution, and the guess was "libel."  All words with 'l', 'i',
# and 'b' would be eliminated, and words without an "e" or an "e" as the 4th
# letter would be eliminated.  If a previous guess had an "e" as the first
# letter (e.g. "exact"), we wouldn't need to remember the guess because all
# words with an "e" as the first letter would have been eliminated.  That means
# that for a particular next guess and solution, we could identify equivalent
# guess that need not be explored.  Note that the number of guesses does not
# matter.  If the set of remaining candidates is the same for a set s4 of
# four guesses and a set s5 of five guesses, the guess that's best for s4 is
# no worse than any others for s5 because all 6th guesses are equal in
# probability.  For a set s3 of 3 guesses with the same set of remaining
# candidates, the best for s3 is not necessarily the best for s4.  But, the
# best for s3 will have a higher chance of success than that for s4.  It's
# not obvious if something like this can be said for the average number of
# guesses.  I think it is true that, given eventual success, the average number
# of remaining guesses for s4 will always be less than s3.
#
# How to encode choice 2, the set of previous guesses?
# A. TreeSet of 2-byte integer indexes
#    size is 4 or 5 guesses, fitting in a binary tree of depth 3, so
#    7 slots of 2-byte words is 14 total bytes, assuming no overhead
# B. Bloom filter - binary number, a bit for each word, so
#    2315 bits = 290 bytes or
#    12972 bits = 1621 bytes
# C. Hash - bad
# D. String of int indexes - bad
# E. Linked list of 2-byte integer indexes (no worse than A - TreeSet)
#
# The number of 4-guess states is
# 12972 * 12971 * 12970 * 12969 / (4 * 3 * 2) = 1,179,276,444,946,215
# 2315 * 2314 * 2313 * 2312 / (4 * 3 * 2) = 1,193,621,329,290
#
# Pruning
#
# So, how do we avoid computation with this convergence strategy?  Maybe we
# could avoid computing a guess if we have an upper bound on how much the
# probability will improve.
#
# One safe prune is to not consider words that do not eliminate any others.
#
# Another, as described earlier, is that guesses that eliminate the same words
# have the same success probabilities and need not be explored.
#
# If a guess g1 eliminates a subset of what another guess g2 eliminates, then g1
# is inferior.  More generally, if a set of guesses s1 results in a set of
# remaining candidates that is a superset of another set of guesses, then s1
# is inferior.
#
# As described for the search space later, it's hard to come up with a max
# success probability < 1.0.  What if we didn't care about depth?  For most
# solutions, it's easy find guesses that are guaranteed to find them in 6 guesses.
# There will be many guesses that guarantee success for many solutions.
# So, instead of evaluating all choices, we just need to find a choice that
# has a success probability of 1.0.  We may quickly find that "trace" as a first
# guess leads to guaranteed success for at least 2000 out of the 2315 solutions
# by not expanding out many choices for each state.
#
# What if we only ever expanded the first guess candidate and built a complete
# policy?  We would know it's probability of success.  We could just follow
# sub-branches that have <1.0 chance of success and try to improve them.  This
# seems very practical.  It will boil down to hard sets of cases.
#
# Search Space
#
# Given the optimal tree/policy described earlier, what does the search space
# look like before we converge on it?
#
# At the top, it is a node representing all possible solutions.  Candidate
# best solutions from this node lead to a node for the set of remaining possible
# solution candidates.
# For a given candidate best guess at a given level, if it leads to the
# same remaining set of candidates as another branch at the same level, even
# for a totally different set of prior guesses, then they point to the same node
# in the "tree."  So, it's actually a DAG instead of a tree.
#
# Each guess in the tree has a min & max probability of success and a min & max
# average remaining depth. Once solved, the min & max in each pair will converge
# to the same value.  If a candidate best guess has a max that is less than
# another's min, it can be pruned, but don't prune child nodes shared with
# other branches!
#
# The min probability will be initialized to 1 divided by the size of the number
# of remaining solutions.  The max probability is initialized to 1.0.  As the
# min & max stats for the candidate best guesses are updated, the min probability
# is updated to the max of the min probabilities, and the
#
# For example, suppose the solution is "pitch", and the 4th guess "hutch" leads
# to a set of 4 remaining candidates ("catch", "match", "patch", "pitch").  A
# possible best guess candidate is created for each of the
# four candidates.  For "catch", there is a match in one case, and three remaining
# candidates in the three other cases).  So, the (success, avg remaining depth) for
# the four cases is (1.0, 1.0), (1/3, 2.0), (1/3, 2.0), (1/3, 2.0).  Thus the
# guess "catch" is the average of the four cases, (0.5, 1.75).  The guess "patch"
# has these cases, (1/3, 2.0), (1/3, 2.0), (1.0, 1.0), (1.0, 2.0) for an average
# of (2/3, 1.75).  Since "patch" has the highest probability of success, it is
# the optimal choice for the policy.  The other guesses can be discarded, even the
# ones with the same score because we only care about computing the probability
# of the first guess.  And, the score for the node with the 4 candidates and the
# "hutch" guess leading to the node is (2/3, 1.75).
#
# Hmmm . . . the example doesn't show an update to the min/max. An example will
# be explored in greater detail later.
#
# Data Structures
#
# class State (a.k.a node)
#     prior_guesses : TreeSet(twoByteInt)  # 14 bytes?
#     incoming_guesses : TreeSet(Guess)
#     remaining candidates : BloomFilter  # 290 bytes
#     alternative_next_guesses : TreeSet(Guess)  # this could be in the State class
#     prob_success : float
#     average_remaining_guesses : float
#
#
# class Guess
#     word : twoByteInt
#     prevState : State
#     prob_success : float
#     average_remaining_guesses : float
#     next_states : dict  # State -> TreeSet(twoByteInt)   # the States resulting from applying this Guess to the previous State mapped to the set of solutions that lead to the State, the size of which is proportional to the likelihood of arriving in the State
#
# queue: TreeSet(State)  # order by number of prior guesses and prob_success
#
# It turns out Python has unlimited size ints.  Based on my limited knowledge, the memory allocation can't be controlled
# easily anyway, so we just use these ints instead of creating twoByteInt.  We also use an int for the bloom filter.
#
# Algorithm
#
# - Create the top-level State/node as the set of all solution candidates for guess 1
# - Add State to the queue
# - Loop
#   - break if queue is empty
#   - Pop State from queue
#   - Expand(State)
#
# - Expand(State)
#   - Choose the seemingly best Guess candidate for the State (that has not yet been chosen)
#   - Add Guess to alternative_next_guesses
#   - Compute or identify next_states, the State for each
#     possible solution in the remaining candidates (from previous State)
#     - Since more than one solution could map to the same State, keep track
#       of which belong to which node or at least count them since that
#       corresponds to the likelihood of reaching the node
#   - update State's prob_success and average_remaining_guesses
#   - update incoming_guesses to the State and propagate backward
#   - if need to explore more Guesses, add this State back in queue
#   - Compute the next_states to the queue
#
#
#
# Example
#
#   wordle_solutions = ['abcd' + x for x in ['e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']] + ['egikm']
#   In this case, intuitively 'egikm' is the best first guess because it eliminates half of the other candidates while
#   the others only eliminate 'egikm'.
#
#   - Create a State to precede the first guess.
#     s0 = State(guess #0, {all candidates}, None)
#   - Put it in the queue
#   - Start the queue processing loop, popping the state s0
#       - Guess 'egikm,' g1, the remaining candidate that is expected to eliminate the most others.
#         - Add the guess, g1, to s.alternative_next_guesses
#         - Generate g.next_states, the dictionary of next states based on all candidate solutions (s.remaining_candidates)
#           For solution 'egikm,' a state with no remaining candidates and probability 1.0
#           State(guess #1, {}, 1.0) -> ['egikm']
#           The candidates with last letters in 'egikm' are mapped to a state where the other candidates are eliminated, but we don't know the probability.
#           s1 = State(guess #1, {'abcd' + x for x in 'egikm'}, None) -> ['abcd' + x for x in 'egikm']
#         - Update the min/max probability of the guess, g1, to [(1.0 * 1 + 0.0 * 9) / 10, (1.0 * 1 + 1.0 * 9) / 10] = [0.1, 1.0]
#           - Propagate it back to the state, s0: since there's only one guess, the same min/max is copied: s0 = State(guess #0, {all candidates}, [0.1, 1.0]).
#         - Put those states in the queue.
#       - Put s0 back on the queue to later generate another guess
#   - Pop next state based on higher guess # and number of remaining candidates (DFS)
#     s1 = State(guess #1, {'abcd' + x for x in 'egikm'}, [0.1, 1.0])
#       - g2 = Guess('abcde')
#         - State(#2, {}, 1.0)
#         - s2 = State(#2, {'abcd' + x for x in 'gikm'}, None)
#         - Update the min/max probability of the guess, g2, to [(1.0 * 1 + 0.0 * 4) / 5, (1.0 * 1 + 1.0 * 4) / 5] = [0.2, 1.0]
#           - Propagate it back to the state, s1: since there's only this one guess, it is modified to [0.2, 1.0].
#             - Propagate it back to the only incoming guess, g1, 'egikm', updating it to  [(1.0 * 1 + 0.2 * 1 + 0.0 * 8) / 10, (1.0 * 1 + 1.0 * 1 + 1.0 * 8) / 10] = [0.12, 1.0]
#               - Propagate [0.12, 1.0] to the top state, s0: since there's only the one guess, g1, and a state gets the probability is that of its best guess, s0 is modified to [0.12, 1.0].
#     s2 = State(guess #1, {'abcd' + x for x in 'gikm'}, None)
#       - g3 = Guess('abcdg')
#       - State(#3, {}, 1.0)
#       - s3 = State(#3, {'abcd' + x for x in 'ikm'}, None)
#       -  HERE!!
#       - g3 <- [0.25, 1.0], s2 <- [0.25, 1.0], g2 <- [(1.0 * 1 + 0.25 * 1 + 0.0 * 3) / 5, (1.0 * 1 + 1.0 * 1 + 1.0 * 3) / 5] = [0.25, 1.0], s1 <- [0.25, 1.0], g1 <- [??], s0 <- [??]
#   . . .
#     s = State(guess #0, {all candidates}, 0.0)
#       - Guess 'abcde'
#         - next states
#           State(guess #1, {}, 1.0) -> ['abcde']
#           State(guess #1, {'egikm'}, 1.0) -> ['egikm']
#           State(guess #1, {all not in ['egikm','abcde']}, 0.0) -> [all not in ['egikm','abcde']]
#         - Put new states in queue
#       - Guess 'abcdf'
#         - next states
#           State(guess #1, {}, 1.0) -> ['abcdf']
#           State(guess #1, {'egikm'}, 1.0) -> ['egikm']
#           State(guess #1, {all not in ['egikm','abcdf']}, 0.0) -> [all not in ['egikm','abcdf']]
#         - Put new states in queue
#       - Other guesses are like the previous two
#
#
import queue
import random
import json
import time
from time import process_time
from typing import Set, Any
import pickle


random.seed(333)

debug = False

wordle_solutions = []  # word strings read from file
wordle_herrings = []  # word strings read from file
guess_candidates = []  # this could be wordle_solutions or the union of wordle_solutions and wordle_herrings
word_indices = {}  # string -> int
remaining_candidates = []  # remaining_candidates[solution][guess] = remaining candidate set as bloom filter
all_guess_candidates = 0  # this is the bloom filter int representing the set of all, a binary 1 for each word.
all_solution_candidates = 0  # the bloom filter for just the solution candidates
init_state = None  # this is the root of the search tree
tl_start = 0  # initial cpu time marker; compute cpu time since tl_start was set with process_time() - tl_start


# Initialize data

with open('wordle_words_2315.txt') as f:
    wordle_solutions = json.load( f )
    wordle_solutions = wordle_solutions

with open('wordle_herrings.txt') as f:
    wordle_herrings = json.load( f )
    wordle_herrings = wordle_herrings


def init_globals():
    """ This computes the remaining_candidates matrix. """
    global guess_candidates
    global word_indices
    global all_solution_candidates
    global all_guess_candidates
    global remaining_candidates
    global tl_start
    # global all_candidates

    # guess candidates can be restricted to solutions or solutions + herrings
    guess_candidates = wordle_solutions
    #guess_candidates = wordle_solutions + wordle_herrings

    # TODO -- reorder wordle solutions and herrings according to a heuristic for best guess

    word_indices = {wordle_solutions[i]: i for i in range(len(wordle_solutions))}

    all_solution_candidates = 2 ** len(wordle_solutions) - 1
    all_guess_candidates = 2 ** len(guess_candidates) - 1

    tl_start = process_time()

    rem_cand_filename = "remaining_candidates_" + str(len(wordle_solutions)) + ".bin"
    remaining_candidates = read_remaining_candidates_from_file(rem_cand_filename)
    if remaining_candidates is None or len(remaining_candidates) != len(wordle_solutions):
        print("Computing remaining_candidates matrix")
    else:
        add_time = process_time() - tl_start
        print( "seconds elapsed after reading remaining_candidate sets from file is " + str( add_time ) )
        return

    # Compute remaining_candidates[solution][guess] = remaining candidate set as bloom filter
    # First allocate the big matrix
    remaining_candidates = [[all_solution_candidates for x in wordle_solutions] for y in guess_candidates]
    #remaining_candidates = pandas.array(remaining_candidates)
    # Now compute each set in the matrix

    for sol_i in range( len(wordle_solutions) ):
        solution = wordle_solutions[ sol_i ]
        for guess_i in range( len(guess_candidates) ):
            guess = guess_candidates[ guess_i ]
            if sol_i == guess_i:
                remaining_candidates[sol_i][guess_i] = 2 ** sol_i
            else:
                remaining_set = compute_remaining_candidates(solution, guess)
                # add_time = process_time() - tl_start
                # print( "seconds for computing " + solution + "-" + guess + " is " + str( add_time ) )
                remaining_candidates[sol_i][guess_i] = remaining_set
        add_time = process_time() - tl_start
        print( "seconds elapsed after computing sets for word #" + str(sol_i) + " (" + solution + ") is " + str( add_time ) )

    print("writing out remaining_candidates to file to load next time and avoid recomputing")
    write_remaining_candidates(rem_cand_filename)
    print("remaining_candidates written to file")
    add_time2 = process_time() - add_time
    print("seconds elapsed to write file is " +  str(add_time2))

    #print( "size of remaining_candidates = " + str(sys.getsizeof(remaining_candidates)))  # this doesn't do what you want

def compute_remaining_candidates(solution, guess):
    match_indices = set()  # the indices labeled green  # mi.copy()
    letters_in_wrong_place = set()  # the indices labeled yellow  # liwp.copy()
    min_numbers_of_letters = {}
    unmatched_letters = set()

    # evaluate letters in wrong guess against the solution
    solution_no_matches = solution
    for i in range(5):
        if guess[i] == solution[i]:
            match_indices.add(i)
            solution_no_matches = solution_no_matches[:i] + ' ' + solution_no_matches[i + 1:]
    counts = {letter: solution_no_matches.count(letter) for letter in set(solution_no_matches)}
    for i in range(5):
        if i not in match_indices:
            if guess[i] in solution:
                if guess[i] in solution_no_matches and counts[guess[i]] > 0:
                    letters_in_wrong_place.add(i)
                    counts[guess[i]] -= 1
            else:
                unmatched_letters.add(guess[i])
    for letter in set(guess):
        min_numbers_of_letters[letter] = min(solution.count(letter), guess.count(letter))

    # Determine possible next guesses
    remaining_set = 0
    mask = 1
    for s_i in range(len(wordle_solutions)):
        w = wordle_solutions[s_i]  # getting the actual string for the word

        # letters must match where we found the exact matching letters
        matches_positions = True
        for m in match_indices:
            if w[m] != solution[m]:
                matches_positions = False
                break
        if not matches_positions:
            continue

        # If the letter in position i was unmatched or in wrong position w[i] must not equal guess[i]
        matched_unmatched_position = False
        for z in set(range(5)) - match_indices:
            if w[z] == guess[z]:
                matched_unmatched_position = True
                break
        if matched_unmatched_position:
            continue

        # For letters found in the wrong position,
        # (1) the letter can't be in the same wrong position again,
        # (2) the number of letters found in the wrong position must be consistent
        has_all_letters = True
        for i in letters_in_wrong_place:
            if w[i] == guess[i] or \
                    min_numbers_of_letters[guess[i]] > w.count(guess[i]):
                has_all_letters = False
                break
        if not has_all_letters:
            continue

        # Make sure the candidate has no letters for which we found no matches
        no_forbidden_letters = True
        for u in unmatched_letters:
            if u in w:
                no_forbidden_letters = False
                break
        if not no_forbidden_letters:
            continue

        # set the bit for the possible candidate in the bloom filter
        remaining_set |= 2 ** s_i

    return remaining_set


def write_remaining_candidates(fn='remaining_candidates.bin'):
    """ Write the matrix to file so that we don't have to spend hours recomputing it! """
    with open(fn, 'wb') as f:
        pickle.dump(remaining_candidates, f)

def read_remaining_candidates_from_file(fn='remaining_candidates.bin'):
    """ Read the matrix to file so that we don't have to spend hours recomputing it! """
    cands = None
    try:
        f = open(fn, 'rb')
        cands = pickle.load(f)
    except Exception as e:
        print(fn + ' not found or pickle.load() failed')
        print(str(e))
    return cands


class State:
    """ A search state for the remaining possible candidate after a particular number of guesses. """

    alternative_next_guesses: Set[ Any ]  # Set[ Guess ]

    def __init__(self):
        # self.prior_state: State = None   # consider instead to look up the state in a set by prior guesses (or number of guesses) and remaining candidates
        self.prior_guesses = set()   # TreeSet(word_index)  # 14 bytes?
        self.incoming_guesses = set()  # TreeSet(Guess)
        self.remaining_candidates = 0  # BloomFilter as int # 290 bytes
        self.num_remaining_candidates = 0  # so we don't have to call num_ones_in_bits() all the time
        self.alternative_next_guesses = set()  # TreeSet(Guess)
        self.prob_success = (0.0, 1.0)
        self.average_remaining_guesses = (1.0, 6.0)

    def get_num_remaining_candidates(self):
        if self.num_remaining_candidates > 0:
            return self.num_remaining_candidates
        if self.remaining_candidates == 0:
            return 0
        self.num_remaining_candidates = num_ones_in_bits(self.remaining_candidates)
        return self.num_remaining_candidates

    def choose_next_guess( self ):
        """
        Choose the next guess alternative to add to the state.  This is used as
        a step in the search.  It might make sense to make this smart, but the
        way the search is currently configured, all guesses are added before
        choosing which one to dig deeper into, and which to dig deeper into
        is chosen elsewhere.  The rest of this text is the old description
        that assumed this should be smart.

        Choose the next best candidate word (to those in
        alternative_next_guesses), such as the one that has "the most
        information."  Is that the one that is expected to most reduce the set
        of candidates?  Not sure whether it makes sense to spend time on
        computing with respect to the remaining candidates.
        """
        g = Guess()
        g.word = nth_candidate(len(self.alternative_next_guesses) + 1,
                               self.remaining_candidates )
        g.prev_state = self
        return g

    def __lt__(self, other):
        """
        Return True if less than the other State
        :type other: State
        """
        if self is other:
            return False
        # if self.prob_success > other.prob_success:
        #     return True
        # if self.prob_success < other.prob_success:
        #     return False
        if len(self.prior_guesses) < len(other.prior_guesses):
            return True
        if len(self.prior_guesses) > len(other.prior_guesses):
            return False
        num_remaining_self = self.get_num_remaining_candidates()
        num_remaining_other = other.get_num_remaining_candidates()
        if num_remaining_self < num_remaining_other:
            return True
        if num_remaining_self > num_remaining_other:
            return False
        if self.remaining_candidates < other.remaining_candidates:
            return True
        return False

    def __le__(self, other):
        """
        Return True if less than or equal to the other State
        :type other: State
        """
        if self is other:
            return True
        # if self.prob_success > other.prob_success:
        #     return True
        # if self.prob_success < other.prob_success:
        #     return False
        if len(self.prior_guesses) < len(other.prior_guesses):
            return True
        if len(self.prior_guesses) > len(other.prior_guesses):
            return False
        num_remaining_self = self.get_num_remaining_candidates()
        num_remaining_other = other.get_num_remaining_candidates()
        if num_remaining_self < num_remaining_other:
            return True
        if num_remaining_self > num_remaining_other:
            return False
        if self.remaining_candidates < other.remaining_candidates:
            return True
        if self.remaining_candidates > other.remaining_candidates:
            return False
        return True

    def __gt__(self, other):
        """
        Return True if greater than the other State
        :type other: State
        """
        if self is other:
            return False
        # if self.prob_success < other.prob_success:
        #     return True
        # if self.prob_success > other.prob_success:
        #     return False
        if len(self.prior_guesses) > len(other.prior_guesses):
            return True
        if len(self.prior_guesses) < len(other.prior_guesses):
            return False
        num_remaining_self = self.get_num_remaining_candidates()
        num_remaining_other = other.get_num_remaining_candidates()
        if num_remaining_self > num_remaining_other:
            return True
        if num_remaining_self < num_remaining_other:
            return False
        if self.remaining_candidates > other.remaining_candidates:
            return True
        return False

    def __ge__(self, other):
        """
        Return True if greater than or equal to the other State
        :type other: State
        """
        if self is other:
            return True
        # if self.prob_success < other.prob_success:
        #     return True
        # if self.prob_success > other.prob_success:
        #     return False
        if len(self.prior_guesses) > len(other.prior_guesses):
            return True
        if len(self.prior_guesses) < len(other.prior_guesses):
            return False
        num_remaining_self = self.get_num_remaining_candidates()
        num_remaining_other = other.get_num_remaining_candidates()
        if num_remaining_self > num_remaining_other:
            return True
        if num_remaining_self < num_remaining_other:
            return False
        if self.remaining_candidates > other.remaining_candidates:
            return True
        if self.remaining_candidates < other.remaining_candidates:
            return False
        return True

    def __eq__(self, other):
        """
        Return True if the States are equal
        :type other: State
        """
        if self is other:
            return True
        # if self.prob_success != other.prob_success:
        #     return False
        if len(self.prior_guesses) != len(other.prior_guesses):
            return False
        if self.remaining_candidates != other.remaining_candidates:
            return False
        return True

    def __neq__(self, other):
        """
        Return True if the States are not equal
        :type other: State
        """
        return not self.__eq__(other)

    def __hash__(self):
        """ Computes a hash value to be used for a hash table (map or set). """
        return len(self.prior_guesses) * all_solution_candidates + self.remaining_candidates

    def __str__(self):
        """ A string representation of the State """
        return str(self.average_remaining_guesses) + ", " + str(self.prob_success) + ", " + str(self.prior_guesses) + ", alternatives = " + \
            str([g.word for g in self.alternative_next_guesses]) + " " + str(self.remaining_candidates)


class Guess:
    """
    The guess class is part of the search tree.  It is the transition from one state to others.  The tree is a kind of
    Markov Decision Process, and we are searching for the optimal policy -- the best next guesses for each state.
    """
    def __init__(self):
        self.word = 0
        self.prev_state = None  # State
        self.prob_success = (0.0, 1.0)
        self.average_remaining_guesses = (1.0, 6.0)
        self.next_states = {}  # State -> int  # the States resulting from applying this Guess to the previous State mapped to a count of solutions that lead to the State, which is proportional to the likelihood of arriving in the State

    def __str__(self):
        """ A string representation of the Guess """
        return str(self.average_remaining_guesses) + ", " + str(self.prob_success) + ", " + str(self.word) + ", prev state = " + str(self.prev_state)

    def update_prob_success(self):
        """
        Simply calculate the probability of success based on that of the next states weighted by probability,
        which is just the count of solutions that would transition to each state since each solution is equally likely.
        """
        num_child_states = sum(self.next_states.values())
        min_prob = sum([s.prob_success[0] * n for (s,n) in self.next_states.items()]) / num_child_states
        max_prob = sum([s.prob_success[1] * n for (s,n) in self.next_states.items()]) / num_child_states
        self.prob_success = (min_prob, max_prob)

    def update_average_remaining_guesses(self):
        """
        Get the weighted average expected number of guesses based on those of the next states and their likelihoods,
        which are the counts of solutions that lead to the states.
        """
        num_child_states = sum(self.next_states.values())
        min_garg = sum([s.average_remaining_guesses[0] * n for (s,n) in self.next_states.items()]) / num_child_states
        max_garg = sum([s.average_remaining_guesses[1] * n for (s,n) in self.next_states.items()]) / num_child_states
        self.average_remaining_guesses = (min_garg, max_garg)


state_cache = [{} for i in range(6)]
hits = 0
misses = 0

cache_on = True
def get_state(num_guesses: int, remaining_candidates: int):
    if not cache_on: return None
    global hits
    inner = state_cache[num_guesses]
    if remaining_candidates in inner:
        hits += 1
        return inner[remaining_candidates]
    return None

def get_or_cache_state(s: State):
    if not cache_on: return s
    global state_cache
    global hits
    global misses
    inner = state_cache[len(s.prior_guesses)]
    if s.remaining_candidates in inner.keys():
        cs = inner[s.remaining_candidates]
        if cs is not None:
            hits += 1
            return cs
        misses += 1
        inner[s.remaining_candidates] = s
        return s
    misses += 1
    inner[s.remaining_candidates] = s
    return s

def cache_size():
    return sum([len(state_cache[i]) for i in range(6)])


# lower number is higher priority
def q_priority(s: State):
    """
    A scoring of a state for the order of exploration.   This is specific to using a queue for managing search
    states.  A competing approach for expansion is to walk down the search tree instead of having a queue.
    """
    return (1.0 - s.prob_success[0], 1.0 - s.prob_success[1],
            len(s.prior_guesses), len(s.alternative_next_guesses), s.get_num_remaining_candidates())

def runq():
    """ The main search loop for using a queue of search states (superseded by run()). """
    global init_state
    init_globals()
    q = queue.PriorityQueue()  # TreeSet(State)  # order by number of prior guesses and prob_success
    init_state = State()
    init_state.remaining_candidates = all_solution_candidates
    q.put((q_priority(init_state), init_state))
    while not q.empty():
        (p, e) = q.get()
        s: State = e
        if debug:
            print("popped " + str(s))
        child_states = expand(s)
        for c in child_states:
            if c.prob_success[0] < c.prob_success[1]:
                q.put((q_priority(c), c))
        if len(s.alternative_next_guesses) < s.get_num_remaining_candidates():
            if (s.prob_success[0] < s.prob_success[1] and
                    (len(s.incoming_guesses) == 0 or
                     s.prob_success[1] >= max([max([g.prob_success[0] for g in i.prev_state.alternative_next_guesses]) for i in s.incoming_guesses]))):
                q.put((q_priority(s), s))
        if debug:
            print("length of queue = " + str(q.qsize()))

    print("init_state probability = " + str(init_state.prob_success))
    for g in init_state.alternative_next_guesses:
        print("prob of choosing " + wordle_solutions[g.word] + " = " + str(g.prob_success))

def all_guesses_done(s: State):
    """ Returns whether all of the alternative guesses for the State have been sufficiently explored to converge on
        a probability of success or on an expected number of guesses left. """
    if len(s.alternative_next_guesses) < s.get_num_remaining_candidates():
        return False
    for g in s.alternative_next_guesses:
        if not converged(g):
            return False
    return True

def converged(sg):
    """
    Whether the State or Guess has been sufficiently explored such that it has converged on a probability of winning
    or an expected number of remaining guesses.
    """
    if sg.prob_success[1] - sg.prob_success[0] > 1E-12:
        return False
    return True

def converged_arg(sg):
    """ Whether the average number of remaining guesses has converged. """
    if sg.average_remaining_guesses[1] - sg.average_remaining_guesses[0] > 1E-12:
        return False
    return True

def print_progress():
    """ Print some stats and progress on finding the best words """
    print("")
    print("cache_size = " + str(cache_size()) + ", hits = " + str(hits) + ", misses = " + str(misses) +
          ", hit/miss = " + (str(((0.0 + hits) / misses)) if misses != 0 else "N/A") + ", " + str((process_time() - tl_start) / 60) + " CPU minutes")
    print("first guesses found so far with policies guaranteeing 100% wins: " +
          str([wordle_solutions[g.word] for g in init_state.alternative_next_guesses if cmp(g.prob_success, (1.0, 1.0)) == 0]))
    converged_guesses = {wordle_solutions[g.word]: g.prob_success for g in init_state.alternative_next_guesses if
                         converged(g)}
    print(str(len(converged_guesses)) + " first guesses converged: " + str(converged_guesses))
    in_progress_guesses = {wordle_solutions[g.word]: g.prob_success for g in init_state.alternative_next_guesses
                           if not converged(g) and g.prob_success[0] >= 0.5}
    print(str(len(in_progress_guesses)) + " others with prob > 50%: " + str(in_progress_guesses))


_ct = 0  # a counter used to occasionally report progress
def occasionally_print_progress():
    """ Print out some feedback occasionally while the search is taking forever. """
    global _ct
    if _ct % 5000 == 0:
        print_progress()
    _ct += 1


def done(s: State):
    """ Whether the search/exploration of the state is complete, and the search can quit. """

    # An alternative strategy is commented out below.
    #return converged(s)   # That will return once a best word is found.
    return all_guesses_done(s)   # This won't return until the optimal policies of all first words are computed.

def cmp(pp1, pp2):
    """ Compare two pairs of floating point numbers while simply handling floating point error. """
    d0 = pp2[0] - pp1[0]
    if abs(d0) >= 1e-12:
        return -1 if d0 > 0 else 1
    d1 = pp2[1] - pp1[1]
    if abs(d1) >= 1e-12:
        return -1 if d1 > 0 else 1
    return 0

def choose_state(s: State):
    """ Smarts for choosing the next state to expand/explore. """

    # some options
    expand_all_alternatives = True
    best_chance_of_reducing_uncertainty = False  # unimplemented -- not sure how this would work, but the thought is to get the min & max range narrowed as opposed to finding the best.

    if expand_all_alternatives and len(s.alternative_next_guesses) < s.get_num_remaining_candidates():
        return s
    # get best scoring alternative guess that hasn't converged
    best: Guess = None
    for g in s.alternative_next_guesses:
        # check converged
        if converged(g):
            continue
        if best is None:
            best = g
            continue
        c = cmp(g.prob_success, best.prob_success)
        if c > 0:
            best = g
            continue
        elif c < 0:
            continue
        if len(g.next_states) < len(best.next_states):
            best = g
            continue
        elif len(g.next_states) > len(best.next_states):
            continue
        c = cmp(g.average_remaining_guesses, best.average_remaining_guesses)
        if c < 0:
            best = g
    if best is None or not best.next_states:
        # This is an error case and a good place to interrupt with a debugger.
        print("\n\n\nwhaaattttt?")
        print("\nThis is a good time to attach a debugger and pause.")
        time.sleep(30)

    # get best scoring result state that hasn't converged
    best_state: State = None
    for cs in best.next_states.keys():
        if converged(cs):
            continue
        if best_state is None:
            best_state = cs
            continue
        c = cmp(cs.prob_success, best_state.prob_success)
        if c > 0:
            best_state = cs
            continue
        elif c < 0:
            continue
        if cs.get_num_remaining_candidates() < best_state.get_num_remaining_candidates():
            best_state = cs
            continue
        elif cs.get_num_remaining_candidates() > best_state.get_num_remaining_candidates():
            continue
        c = cmp(cs.average_remaining_guesses, best_state.average_remaining_guesses)
        if c < 0:
            best_state = cs

    if best_state is None:
        # This is an error state, so we sleep so that it's easier to catch in a debugger.
        print("\n\n\nwhaaattttttttttttttttt?")
        print("\nThis is a good time to attach a debugger and pause.")
        time.sleep(30)
    best_state = choose_state(best_state)
    return best_state


def run():
    """ Initialize the search and start running it. """
    global init_state
    init_globals()
    init_state = State()
    init_state.remaining_candidates = all_solution_candidates
    run_no_init()

def run_no_init():
    """ Execute the search assuming that other things are initialized. """
    global init_state
    global tl_start
    tl_start = process_time()

    while not done(init_state):
        # Print out some feedback occasionally while the search is taking forever.
        occasionally_print_progress()

        # choose and expand a state
        s: State = choose_state(init_state)
        if debug:
            print("popped " + str(s))
        _ = expand(s)

    print_progress()  # print one last time at the end
    print("\ninit_state success probability = " + str(init_state.prob_success) + ", avg guesses = " + str(init_state.average_remaining_guesses))
    if debug:
        for g in init_state.alternative_next_guesses:
            print("prob success of choosing " + wordle_solutions[g.word] + " = " + str(g.prob_success) + "; avg guesses = " + str(g.average_remaining_guesses))
    add_time = process_time() - tl_start
    print("seconds elapsed to build policy = " + str(add_time))


def expand(s: State):
    """ Generate guesses for states and the states to which the guesses transition. """
    g = s.choose_next_guess()
    s.alternative_next_guesses.add(g)
    #   - Compute or identify next_states, the State for each
    #     possible solution in the remaining candidates (from previous State)
    #     - Since more than one solution could map to the same State, keep track
    #       of which belong to which node or at least count them since that
    #       corresponds to the likelihood of reaching the node
    pos = 0
    n = 1
    cands = s.remaining_candidates
    while True:
        candidate = nth_candidate(n, cands, pos, n-1)
        if candidate == -1:
            # don't compute g.prob_success here; it is iteratively computed as g's children are added below
            #g.prob_success = sum([ns.prob_success * g.next_states[ns] for ns in g.next_states.keys()]) / sum([g.next_states[ns] for ns in g.next_states.keys()])
            break
        n += 1  # for the next iteration of this loop
        pos = candidate + 1
        child_remaining_candidates = cands & remaining_candidates[candidate][g.word]
        cached_state = get_state(len(s.prior_guesses) + 1, child_remaining_candidates)
        is_new = False
        if cached_state is not None:
            child = cached_state
        else:
            is_new = True
            child = State()
            child.remaining_candidates = child_remaining_candidates
            child.prior_guesses = s.prior_guesses.copy()
            child.prior_guesses.add(g.word)
            child = get_or_cache_state(child)  # child should not change
        child.incoming_guesses.add(g)
        if child in g.next_states.keys():
            g.next_states[child] += 1
        else:
            g.next_states[child] = 1
            if is_new:
                # determine probability of success
                if child_remaining_candidates < 1:
                    raise Exception('Unexpected number of child_remaining_candidates, ' +
                                    str(child.get_num_remaining_candidates()) + ' < 1')
                child_prob = 1.0 / child.get_num_remaining_candidates()

                # The "HERE!" labels below indicate where the code is incomplete.
                ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###
                avg_guesses = child.get_num_remaining_candidates() / 2  ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###
                ###  HERE!!!!!  ###

                if len(s.prior_guesses) == 4 or child.get_num_remaining_candidates()== 1:
                    child.prob_success = (child_prob, child_prob)
                    ###  HERE!!!!!  ###
                    ###  HERE!!!!!  ###
                    child.average_remaining_guesses = (avg_guesses, avg_guesses)  ## HERE!!!!!
                    ###  HERE!!!!!  ###
                    ###  HERE!!!!!  ###
                elif len(s.prior_guesses) < 4:
                    child.prob_success = (child_prob, 1.0)
                    ###  HERE!!!!!  ###
                    ###  HERE!!!!!  ###
                    child.average_remaining_guesses = (1, avg_guesses)  ## HERE!!!!!
                    ###  HERE!!!!!  ###
                    ###  HERE!!!!!  ###
                else:
                    raise Exception('Unexpected number of prior guesses, ' + str(len(s.prior_guesses)) + ' > 4')
                if debug:
                    print(str(child))
    g.update_prob_success()
    propagate_guess_prob_success(s, g)
    return g.next_states.keys()


def update_guess_from_child_state_prob_success(guess: Guess, child_state: State, old_child_prob: tuple, new_child_prob: tuple):
    '''
    Update guess `prob_success` from its child state's `prob_success`.  Assumes child state is already in `guess.next_states`,
    and the child's old `prob_success` (`old_child_prob`) is reflected in the guess's `prob_success`.
    Return whether the guess's prob_success changed.
    :param guess:
    :param old_child_prob:
    :param new_child_prob:
    :return:
    '''
    if guess is None:
        return
    old_prob = guess.prob_success
    num_child_states = sum(guess.next_states.values())
    num_occs = guess.next_states[child_state]  # This assumes that the child has already been added to g.next_states

    min_prob = (new_child_prob[0] * num_occs - old_child_prob[0] * num_occs + old_prob[0] * num_child_states) / num_child_states
    max_prob = (new_child_prob[1] * num_occs - old_child_prob[1] * num_occs + old_prob[1] * num_child_states) / num_child_states
    guess.prob_success = (min_prob, max_prob)
    if cmp(guess.prob_success, old_prob) == 0:
        return False
    return True

def propagate_guess_prob_success(s: State, alt_guess: Guess):
    '''
    Update the parent state's prob_success based on an update to that of one of the alternative next guesses.
    A state's prob_success is the max of those of its alternative guesses in that state.
    :param s:
    :param alt_guess:
    :return:
    '''
    old_prob = s.prob_success
    # example: if alternative probs are [(0.0, 1.0), (0.1, 0.2)] then the parent is (0.1, 1.0)
    min_prob = max(ang.prob_success[0] for ang in s.alternative_next_guesses)
    all_alts = not (len(s.alternative_next_guesses) < s.get_num_remaining_candidates())
    if not all_alts:
        max_prob = 1.0
    else:
        max_prob = max(ang.prob_success[1] for ang in s.alternative_next_guesses)
    s.prob_success = (min_prob, max_prob)
    if debug:
        print(str(s) + " for " + str(len(s.alternative_next_guesses)) + " out of " + str(s.get_num_remaining_candidates()))
    for g in s.incoming_guesses:
        changed = update_guess_from_child_state_prob_success(g, s, old_prob, s.prob_success)
        if changed:
            parent_state = g.prev_state
            if parent_state is not None:
                propagate_guess_prob_success(parent_state, g)

def nth_candidate(n: int, candidates: int, pos=0, ones=0):
    """
    Return the index of the nth word in the candidate set bloom filter
    starting at position/index pos
    :param n for nth candidate in set to return; n > 0
    :param candidates the candidate set bloom filter
    :param pos the bit position from which to start looking for candidate set members
    :return the index of the nth member of the candidates or -1 if there are
    not that many candidates
    """
    if n <= 0:
        return -1  # HACK -- should throw an exception however that is done
    # This could be more efficient if we passed in the position of the (n-1)th
    # candidate.
    #ones = 0  # how many 1s found in binary
    mask = 1 << pos  # 2 ** pos
    while True:
        if candidates & mask > 0:
            ones += 1
            if ones == n:
                return pos
        pos += 1
        mask <<= 1
        if mask > candidates:
            return -1

def num_ones_in_bits(i: int) -> int:
    """
    Return the number of binary ones are in the int.  This is the number of items in the set for the bloom filter.
    """
    ones = 0  # how many 1s found in binary
    while i > 0:
        if i % 2 == 1:
            ones += 1
        i >>= 1
    return ones


def play(solution):
    """
    Play wordle for the provided solution based on the policy that has been computed.
    :return: how many guesses were attempted.
    """
    si = word_indices[solution]
    s: State = init_state
    child_candidates = None
    count = 0
    while True:
        # If no more guesses for states, pick random among remaining candidates
        if not s and child_candidates:
            csi = random.randint(1,num_ones_in_bits(child_candidates))
            guess = nth_candidate(csi, child_candidates)
            print(wordle_solutions[guess])
            count += 1
            if guess == si:
                print("win in random choice among " + str(num_ones_in_bits(child_candidates)) + " alternatives")
                break
            if guess < 0:
                print("error 1")
                break
            child_candidates = child_candidates & remaining_candidates[si][guess]
            continue
        if not s or not s.alternative_next_guesses:
            if s:
                child_candidates = s.remaining_candidates
                s = None
                continue
            print("error 2: s = " + str(s))
            break
        m = max([gg.prob_success for gg in s.alternative_next_guesses])
        gs = list(filter(lambda gg: (gg.prob_success == m), s.alternative_next_guesses))
        g = gs[0]
        w = wordle_solutions[g.word]
        print(w)
        count += 1
        if w == solution:
            print("win in strategic choice among " + str(s.get_num_remaining_candidates()) + " alternatives")
            break
        child_candidates = s.remaining_candidates & remaining_candidates[si][g.word]
        ss = list(filter(lambda cs: (cs.remaining_candidates == child_candidates), g.next_states.keys()))
        s = ss[0] if ss else None
    return count

def test():
    """ Build the policy """
    global wordle_solutions

    # You may uncomment a line below for a simpler test that doesn't include all 2315 words.
    # wordle_solutions = wordle_solutions[0:400]
    # wordle_solutions = ['abcd' + x for x in ['e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']] + ['dfhjl', 'egikm']
    run()

def tree_size(s: State):
    """
    Walks the tree for all guesses for all games and counts the states it visits.  This would be an accurate
    count of the states in memory if the cache were turned off (cache_on = False).  So, when compared with cache_size(),
    tree_size() gives an idea of how effective the cache is.
    """
    if s is None or not s.alternative_next_guesses:
        return 0
    ct = len(s.alternative_next_guesses)
    for g in s.alternative_next_guesses:
        if g is not None and g.next_states:
            ct += len(g.next_states)
            for ss in g.next_states:
                ct += tree_size(ss)
    return ct

if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    test()
