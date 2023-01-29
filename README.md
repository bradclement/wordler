# wordler
Python that finds the optimal policy to play wordle (including the best initial guess).

## Why?

The idea and challenge here is to **prove** what word or words are best.  The spoiler: there are 
multiple first words that can guarantee to always win within six guesses . . . as long as
you are smart enough to know what's the best guess in every situation or a computer that
can remember them all.

An additional challenge is to find the words that result in the fewest guesses on average.
No results on that yet.

There are probably no results here that haven't been found elsewhere.  A web search on
"wordle optimal policy" found a collection of mathematical results.

## Running it

1. download the code
   - This should be easy if you are reading this README
2. run `python wordler.py` from a command line terminal while in the same directory as wordler.py
   - Better would be to run it with a debugger as explained below
   - I'm using Python 3.10, but something recent should be fine. 

It's better to run wordler.py with a debugger (like PyCharm's) so that you can stop it 
instead of waiting hours (or days?) for it to complete.  You can then investigate and play
around as described later.

It will first take 2 or 3 hours to precompute a matrix for quick determination of 
remaining candidate words after a guess.  It is written to file (1.5 GB) so 
that the next time you run, you don't have to wait 2 or 3 hours again to recompute it.

Then, a policy will be computed for a yet unknown amount of time to determine the likelihoods
of winning for each word as an initial guess according to an optimal policy (playing perfectly). 

At the end of wordler.py in the test() function are some commented out lines for testing on
easier sets of words.  That may be a better way to get more familiar with how it works.

After precomputing the matrix, occasionally progress is reported out:

    cache_size = 0, hits = 0, misses = 0, hit/miss = N/A, 2.650000000000337e-05 CPU minutes
    first guesses found so far with policies guaranteeing 100% wins: []
    0 first guesses converged: {}
    0 others with prob > 50%: {}

On first report, essentially nothing has completed, yet.  But, after two hours you may see

    cache_size = 431186, hits = 19665584, misses = 431186, hit/miss = 45.60812271270403, 140.71542415000002 CPU minutes
    words with policies guaranteeing 100% wins : ['plate', 'table', 'petal']
    24 first guesses converged: {'crate': (0.9995680345572366, 0.9995680345572354), 'after': (0.998992080633549, 0.9989920806335493), 'react': (0.9987041036717075, 0.9987041036717063), 'alert': (0.9995680345572366, 0.9995680345572354), 'pleat': (0.9995680345572362, 0.9995680345572354), 'leapt': (0.999568034557236, 0.9995680345572354), 'trade': (0.9995680345572364, 0.9995680345572354), 'trace': (0.9991360691144711, 0.9991360691144708), 'least': (0.9987041036717065, 0.9987041036717063), 'bleat': (0.9995680345572362, 0.9995680345572354), 'plate': (1.0000000000000002, 1.0), 'alter': (0.9992224622030257, 0.9992224622030237), 'tread': (0.9995680345572362, 0.9995680345572354), 'steal': (0.9992800575953931, 0.9992800575953924), 'slate': (0.9991360691144714, 0.9991360691144708), 'table': (1.0000000000000013, 1.0), 'stale': (0.9991360691144716, 0.9991360691144708), 'leant': (0.9987041036717067, 0.9987041036717063), 'petal': (1.0000000000000004, 1.0), 'later': (0.9987904967602601, 0.9987904967602591), 'cleat': (0.9995680345572362, 0.9995680345572354), 'avert': (0.9995680345572364, 0.9995680345572354), 'cater': (0.9992191393919255, 0.9992191393919255), 'eclat': (0.9991360691144713, 0.9991360691144708)}
    1 others with prob > 50%: {'elate': (0.8614924846828584, 0.9991360691144708)}

This means that the optimal policy was found for 24 words, and three of them have an
always-win-within-6-guesses policy.  The policy "converges" when the min/max probabilities
(the pairs of numbers shown above) are the same. The words/guesses each start out with 
min = 0.0 and max = 1.0, meaning it could be anything.  As possible games are explored, it gets 
a better estimate of what the best choices are and how many will win, and the gap between
the min and max shrinks.

As you can see above "crate" converged on a probability of 0.9995680345572366.  If you
multiply that times 2315 (the number of all solution words), that is 2314.0.  This means
that if "crate" is your first guess, you always play perfectly, and you don't cheat, you
can expect to lose on one of the 2315 words. 

There is a done() function that determines when to stop searching.  By default, it tries to
compute an optimal policy for each word (aka guess) with this line: 

    return all_guesses_done(s)

You can instead use the commented out line above so that the program ends when just one word
converges on a 1.0 probability of success:

    return converged(s)

There's a play() function where once you've computed a policy, you can try it out:

    >>> play('maize')
    table
    carve
    gauze
    maize
    win in random choice among 1 alternatives
    4

In PyCharm, I modify the "Run Configuration" to "Run with Python Console" so that I can
pause the python run with the debugger and do the play command above.

You can play against all words and see how it did.  I think this one below was when "trace"
had the best-so-far policy.  Notice that there were two words that required 8 guesses.  That's
consistent with the 0.9991360691144718 win probability for "trace."

    counts = [play(w) for w in wordle_solutions]

    >>> max(counts)
    8
    
    >>> [wordle_solutions[i] for i in range(len(counts)) if counts[i] == 8]
    ['latch', 'batch']

wordle.py has a long discussion in comments at the top that describes how the code works.

Some preliminary code is there for optimizing for the fewest guesses.  It doesn't work yet,
and the part that needs work is labeled with "HERE!"

The policy search is currently restricted to the 2315 common 5-letter words.  The
"wordle_herrings.txt" file includes 10,657 other 5-letter words that the wordle
game accepts but will never be the correct answer.  The code can be configured to
guess using the additional herrings, but that hasn't been tried and will likely have bugs.

Python was probably a bad choice for run time efficiency.  This evolved from an interview
question and wasn't expected to get this far.

Results so far below.  In another run without using the cache, "parse" was found
to be (1.0, 1.0) as well.

    {
       "baker": (0.9996544276457885, 0.9996544276457883),
       "crate": (0.9995680345572366, 0.9995680345572354),
       "exalt": (0.9991360691144714, 0.9991360691144708),
       "feral": (0.9999999999999996, 1.0),                  always wins
       "break": (1.0, 1.0),
       "treat": (1.000000000000001, 1.0),                   always wins
       "layer": (0.9992080633549317, 0.9992080633549315),
       "lager": (0.998822545809239, 0.9988225458092386),
       "crane": (0.9991360691144705, 0.9991360691144708),
       "after": (0.998992080633549, 0.9989920806335493),
       "react": (0.9987041036717075, 0.9987041036717063),
       "alert": (0.9995680345572366, 0.9995680345572354),
       "agree": (0.9992564529263894, 0.9992564529263888),
       "terra": (0.9996091741232134, 0.999609174123213),
       "elate": (0.9991360691144713, 0.9991360691144708),
       "brave": (0.9999999999999998, 1.0),                  always wins
       "large": (0.9995680345572359, 0.9995680345572354),
       "water": (0.9989200863930889, 0.9989200863930886),
       "pleat": (0.9995680345572362, 0.9995680345572354),
       "leapt": (0.999568034557236, 0.9995680345572354),
       "gamer": (0.999247332940638, 0.9992473329406376),
       "baler": (0.9996864250859941, 0.9996864250859931),
       "trade": (0.9995680345572364, 0.9995680345572354),
       "blare": (1.0, 1.0),                                 always wins
       "trace": (0.9991360691144711, 0.9991360691144708),
       "least": (0.9987041036717065, 0.9987041036717063),
       "wager": (0.998704103671707, 0.9987041036717063),
       "latte": (0.9987580993520521, 0.9987580993520518),
       "bleat": (0.9995680345572362, 0.9995680345572354),
       "early": (1.0000000000000013, 1.0),                  always wins
       "gayer": (0.9991360691144705, 0.9991360691144708),
       "brace": (0.9991360691144711, 0.9991360691144708),
       "great": (0.9987041036717063, 0.9987041036717063),
       "grape": (1.0000000000000004, 1.0),                  always wins
       "grade": (1.0000000000000009, 1.0),                  always wins
       "plate": (1.0000000000000002, 1.0),                  always wins
       "elite": (0.9999999999999994, 1.0),                  always wins
       "dealt": (0.9991360691144705, 0.9991360691144708),
       "lathe": (0.9978401727861771, 0.9978401727861771),
       "carve": (0.9995680345572362, 0.9995680345572354),
       "earth": (0.9982721382289421, 0.9982721382289417),
       "farce": (0.9991360691144713, 0.9991360691144708),
       "alter": (0.9992224622030257, 0.9992224622030237),
       "tread": (0.9995680345572362, 0.9995680345572354),
       "gazer": (0.9986302148459707, 0.9986302148459704),
       "delta": (0.9991360691144713, 0.9991360691144708),
       "taker": (0.999222462203024, 0.9992224622030239),
       "steal": (0.9992800575953931, 0.9992800575953924),
       "taper": (0.9996400287976959, 0.9996400287976961),
       "slate": (0.9991360691144714, 0.9991360691144708),
       "relax": (0.9999999999999998, 1.0),                  always wins
       "regal": (0.9991360691144718, 0.9991360691144708),
       "table": (1.0000000000000013, 1.0),                  always wins
       "heart": (0.9987041036717057, 0.9987041036717063),
       "stale": (0.9991360691144716, 0.9991360691144708),
       "title": (0.9992552319952347, 0.9992552319952335),
       "renal": (1.0, 1.0),                                 always wins
       "tamer": (0.9992407880096867, 0.9992407880096864),
       "graze": (1.0000000000000009, 1.0),                  always wins
       "hater": (0.9981641468682512, 0.9981641468682505),
       "glare": (0.9995680345572359, 0.9995680345572354),
       "grate": (0.9987041036717073, 0.9987041036717063),
       "leant": (0.9987041036717067, 0.9987041036717063),
       "brake": (1.0000000000000004, 1.0),                  always wins
       "grave": (0.9999999999999994, 1.0),                  always wins
       "petal": (1.0000000000000004, 1.0),                  always wins
       "learn": (0.9999999999999998, 1.0),                  always wins
       "irate": (0.998704103671706, 0.9987041036717063),
       "drape": (1.0, 1.0),                                 always wins
       "later": (0.9987904967602601, 0.9987904967602591),
       "craze": (0.9996723020779033, 0.9996723020779027),
       "flare": (1.0000000000000004, 1.0),                  always wins
       "drake": (1.0000000000000007, 1.0),                  always wins
       "crave": (0.9995680345572354, 0.9995680345572354),
       "cleat": (0.9995680345572362, 0.9995680345572354),
       "paler": (0.9996914532551685, 0.9996914532551682),
       "relay": (0.9995680345572356, 0.9995680345572354),
       "eater": (0.9982056820069777, 0.9982056820069779),
       "avert": (0.9995680345572364, 0.9995680345572354),
       "grace": (0.9987041036717067, 0.9987041036717063),
       "cater": (0.9992191393919255, 0.9992191393919255),
       "eclat": (0.9991360691144713, 0.9991360691144708),
       "eager": (0.9984308194119978, 0.9984308194119981),
       "clear": (0.9996495374709655, 0.9996495374709645),
    }


