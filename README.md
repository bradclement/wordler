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

Results so far below.

    {
       "baker": (0.9996544276457885, 0.9996544276457883),
       "payer": (0.9996400287976959, 0.9996400287976961),
       "shore": (0.9988480921526283, 0.9988480921526277),
       "eagle": (0.9987373317826883, 0.9987373317826881),
       "spade": (1.0000000000000002, 1.0),
       "snare": (0.9995680345572362, 0.9995680345572354),
       "reuse": (0.9996256299496048, 0.999625629949604),
       "yearn": (1.0000000000000004, 1.0),
       "spire": (0.9999999999999998, 1.0),
       "taste": (0.9995680345572359, 0.9995680345572354),
       "creak": (0.9999999999999998, 1.0),
       "nurse": (0.9995680345572354, 0.9995680345572354),
       "range": (0.9995680345572359, 0.9995680345572354),
       "crate": (0.9995680345572366, 0.9995680345572354),
       "exalt": (0.9991360691144714, 0.9991360691144708),
       "super": (0.9996400287976968, 0.9996400287976961),
       "haste": (0.9987041036717067, 0.9987041036717063),
       "share": (0.9995680345572362, 0.9995680345572354),
       "feral": (0.9999999999999996, 1.0),
       "swine": (1.0000000000000007, 1.0),
       "spore": (0.9996297439062026, 0.9996297439062019),
       "paste": (0.9995680345572356, 0.9995680345572354),
       "spear": (0.9996511048346906, 0.9996511048346901),
       "bathe": (0.9974082073434122, 0.9974082073434125),
       "break": (1.0, 1.0),
       "treat": (1.000000000000001, 1.0),
       "layer": (0.9992080633549317, 0.9992080633549315),
       "stake": (0.9982721382289417, 0.9982721382289417),
       "lager": (0.998822545809239, 0.9988225458092386),
       "phase": (0.9995680345572354, 0.9995680345572354),
       "leash": (0.9991360691144721, 0.9991360691144708),
       "crane": (0.9991360691144705, 0.9991360691144708),
       "spare": (0.9999999999999996, 1.0),
       "after": (0.998992080633549, 0.9989920806335493),
       "chafe": (0.9987041036717067, 0.9987041036717063),
       "snore": (0.9994240460763146, 0.9994240460763139),
       "power": (0.9993520518358527, 0.9993520518358532),
       "heard": (0.9995680345572352, 0.9995680345572354),
       "pearl": (1.0000000000000004, 1.0),
       "react": (0.9987041036717075, 0.9987041036717063),
       "clean": (1.0000000000000009, 1.0),
       "glade": (0.9995680345572354, 0.9995680345572354),
       "shale": (0.9995680345572356, 0.9995680345572354),
       "saner": (0.9988577836849977, 0.9988577836849974),
       "flake": (0.9999999999999996, 1.0),
       "alert": (0.9995680345572366, 0.9995680345572354),
       "agree": (0.9992564529263894, 0.9992564529263888),
       "recap": (1.0000000000000009, 1.0),
       "teach": (0.9978401727861769, 0.9978401727861771),
       "purge": (1.0000000000000002, 1.0),
       "debar": (0.9989560835133188, 0.998956083513319),
       "algae": (0.998704103671706, 0.9987041036717063),
       "terra": (0.9996091741232134, 0.999609174123213),
       "snipe": (1.0000000000000002, 1.0),
       "sinew": (1.0000000000000009, 1.0),
       "fella": (0.9999999999999996, 1.0),
       "elate": (0.9991360691144713, 0.9991360691144708),
       "brave": (0.9999999999999998, 1.0),
       "beach": (0.998704103671706, 0.9987041036717063),
       "large": (0.9995680345572359, 0.9995680345572354),
       "water": (0.9989200863930889, 0.9989200863930886),
       "worse": (0.999568034557235, 0.9995680345572354),
       "cheap": (0.9995680345572366, 0.9995680345572354),
       "pleat": (0.9995680345572362, 0.9995680345572354),
       "resin": (0.999568034557236, 0.9995680345572354),
       "leapt": (0.999568034557236, 0.9995680345572354),
       "shave": (0.999568034557235, 0.9995680345572354),
       "blame": (1.0000000000000004, 1.0),
       "salve": (0.9995680345572359, 0.9995680345572354),
       "gamer": (0.999247332940638, 0.9992473329406376),
       "singe": (0.9995680345572356, 0.9995680345572354),
       "baler": (0.9996864250859941, 0.9996864250859931),
       "prose": (0.9996297439062025, 0.9996297439062019),
       "trade": (0.9995680345572364, 0.9995680345572354),
       "pause": (1.0000000000000004, 1.0),
       "safer": (0.9992433546492755, 0.9992433546492752),
       "blare": (1.0, 1.0),
       "place": (1.0000000000000016, 1.0),
       "rearm": (1.0000000000000002, 1.0),
       "trace": (0.9991360691144711, 0.9991360691144708),
       "spine": (1.0000000000000009, 1.0),
       "bread": (1.0000000000000009, 1.0),
       "teary": (0.9991360691144708, 0.9991360691144708),
       "dread": (0.9992086171567817, 0.9992086171567812),
       "least": (0.9987041036717065, 0.9987041036717063),
       "arise": (0.9995680345572356, 0.9995680345572354),
       "wafer": (0.9991360691144713, 0.9991360691144708),
       "rinse": (1.0000000000000009, 1.0),
       "cable": (1.0, 1.0),
       "peach": (0.9991360691144711, 0.9991360691144708),
       "snake": (0.9995680345572362, 0.9995680345572354),
       "probe": (0.9996544276457883, 0.9996544276457883),
       "shear": (0.9989680825533966, 0.9989680825533959),
       "fable": (0.9999999999999998, 1.0),
       "stead": (0.9988480921526277, 0.9988480921526278),
       "state": (0.9980164031556087, 0.9980164031556085),
       "scale": (1.0000000000000004, 1.0),
       "wager": (0.998704103671707, 0.9987041036717063),
       "glaze": (1.0000000000000009, 1.0),
       "glean": (0.9995680345572352, 0.9995680345572354),
       "blaze": (1.0000000000000004, 1.0),
       "latte": (0.9987580993520521, 0.9987580993520518),
       "bleat": (0.9995680345572362, 0.9995680345572354),
       "plead": (1.000000000000001, 1.0),
       "early": (1.0000000000000013, 1.0),
       "weary": (0.9995680345572359, 0.9995680345572354),
       "swore": (0.9995680345572354, 0.9995680345572354),
       "slave": (0.9995680345572356, 0.9995680345572354),
       "caper": (0.9996741313326513, 0.9996741313326513),
       "gayer": (0.9991360691144705, 0.9991360691144708),
       "risen": (0.9995680345572359, 0.9995680345572354),
       "label": (1.0, 1.0),
       "asset": (0.9987041036717065, 0.9987041036717063),
       "realm": (1.0000000000000004, 1.0),
       "sneer": (0.9996220302375808, 0.999622030237581),
       "rebar": (0.9996511048346901, 0.9996511048346901),
       "reach": (0.9987041036717063, 0.9987041036717063),
       "shame": (0.9995680345572356, 0.9995680345572354),
       "plane": (0.9995680345572356, 0.9995680345572354),
       "panel": (0.999568034557236, 0.9995680345572354),
       "meant": (0.9995680345572352, 0.9995680345572354),
       "beast": (0.9995680345572356, 0.9995680345572354),
       "brace": (0.9991360691144711, 0.9991360691144708),
       "great": (0.9987041036717063, 0.9987041036717063),
       "grape": (1.0000000000000004, 1.0),
       "grade": (1.0000000000000009, 1.0),
       "plate": (1.0000000000000002, 1.0),
       "elite": (0.9999999999999994, 1.0),
       "sweat": (0.9995680345572364, 0.9995680345572354),
       "smite": (0.9995680345572356, 0.9995680345572354),
       "sauce": (0.9991360691144711, 0.9991360691144708),
       "poker": (0.9996400287976961, 0.9996400287976961),
       "dealt": (0.9991360691144705, 0.9991360691144708),
       "suite": (0.9995680345572354, 0.9995680345572354),
       "amber": (0.9997089917017158, 0.9997089917017165),
       "snide": (0.9995680345572362, 0.9995680345572354),
       "steam": (0.998704103671707, 0.9987041036717063),
       "space": (0.9995680345572354, 0.9995680345572354),
       "lathe": (0.9978401727861771, 0.9978401727861771),
       "carve": (0.9995680345572362, 0.9995680345572354),
       "waste": (0.999568034557235, 0.9995680345572354),
       "earth": (0.9982721382289421, 0.9982721382289417),
       "farce": (0.9991360691144713, 0.9991360691144708),
       "rouse": (0.9991360691144713, 0.9991360691144708),
       "poser": (0.9996220302375813, 0.999622030237581),
       "steak": (0.998704103671706, 0.9987041036717063),
       "shape": (0.9995680345572359, 0.9995680345572354),
       "abled": (1.0000000000000009, 1.0),
       "alter": (0.9992224622030257, 0.9992224622030237),
       "sober": (0.9992080633549317, 0.9992080633549315),
       "tread": (0.9995680345572362, 0.9995680345572354),
       "waver": (0.9989589632829377, 0.9989589632829374),
       "prone": (0.9991840652747787, 0.9991840652747781),
       "saute": (0.9987041036717067, 0.9987041036717063),
       "gazer": (0.9986302148459707, 0.9986302148459704),
       "delta": (0.9991360691144713, 0.9991360691144708),
       "taker": (0.999222462203024, 0.9992224622030239),
       "angle": (0.9991360691144703, 0.9991360691144708),
       "steal": (0.9992800575953931, 0.9992800575953924),
       "ready": (0.9995680345572359, 0.9995680345572354),
       "sower": (0.9993520518358541, 0.9993520518358532),
       "taper": (0.9996400287976959, 0.9996400287976961),
       "slate": (0.9991360691144714, 0.9991360691144708),
       "cedar": (0.9984476241900648, 0.9984476241900648),
       "stave": (0.9984161267098632, 0.9984161267098632),
       "relax": (0.9999999999999998, 1.0),
       "dream": (1.0, 1.0),
       "leach": (0.9991360691144716, 0.9991360691144708),
       "regal": (0.9991360691144718, 0.9991360691144708),
       "maker": (0.9992473329406377, 0.9992473329406376),
       "table": (1.0000000000000013, 1.0),
       "heart": (0.9987041036717057, 0.9987041036717063),
       "repay": (1.0000000000000007, 1.0),
       "stale": (0.9991360691144716, 0.9991360691144708),
       "penal": (1.0000000000000004, 1.0),
       "title": (0.9992552319952347, 0.9992552319952335),
       "shade": (0.999568034557236, 0.9995680345572354),
       "chase": (0.998704103671706, 0.9987041036717063),
       "stage": (0.9979841612670983, 0.9979841612670987),
       "beard": (1.0000000000000007, 1.0),
       "parse": (1.0000000000000004, 1.0),
       "false": (0.9995680345572359, 0.9995680345572354),
       "store": (0.999222462203024, 0.9992224622030237),
       "erase": (0.9992440604751618, 0.999244060475162),
       "feast": (0.9987041036717065, 0.9987041036717063),
       "cheat": (0.9974082073434127, 0.9974082073434125),
       "arose": (0.9988480921526278, 0.9988480921526278),
       "utile": (0.9995680345572362, 0.9995680345572354),
       "renal": (1.0, 1.0),
       "caste": (0.9995680345572356, 0.9995680345572354),
       "horse": (0.9987041036717067, 0.9987041036717063),
       "prove": (0.9996544276457885, 0.9996544276457883),
       "surer": (0.9992430319860124, 0.9992430319860126),
       "tamer": (0.9992407880096867, 0.9992407880096864),
       "graze": (1.0000000000000009, 1.0),
       "pedal": (1.0000000000000002, 1.0),
       "hater": (0.9981641468682512, 0.9981641468682505),
       "baste": (0.9995680345572352, 0.9995680345572354),
       "amble": (1.0000000000000009, 1.0),
       "shire": (0.9995680345572359, 0.9995680345572354),
       "paper": (0.9989266313240395, 0.9989266313240395),
       "skate": (0.998704103671706, 0.9987041036717063),
       "glare": (0.9995680345572359, 0.9995680345572354),
       "angel": (0.9991360691144713, 0.9991360691144708),
       "parer": (0.9994452379293524, 0.9994452379293528),
       "anger": (0.9988019071681815, 0.9988019071681813),
       "sneak": (1.0000000000000007, 1.0),
       "score": (0.9995680345572354, 0.9995680345572354),
       "lance": (0.9992594878124034, 0.9992594878124036),
       "smear": (0.9996579182756294, 0.9996579182756289),
       "grate": (0.9987041036717073, 0.9987041036717063),
       "leant": (0.9987041036717067, 0.9987041036717063),
       "since": (0.9995680345572356, 0.9995680345572354),
       "brake": (1.0000000000000004, 1.0),
       "grave": (0.9999999999999994, 1.0),
       "petal": (1.0000000000000004, 1.0),
       "surge": (0.9991360691144706, 0.9991360691144708),
       "learn": (0.9999999999999998, 1.0),
       "irate": (0.998704103671706, 0.9987041036717063),
       "drape": (1.0, 1.0),
       "purse": (1.0000000000000009, 1.0),
       "curse": (1.0000000000000002, 1.0),
       "scare": (1.0000000000000002, 1.0),
       "later": (0.9987904967602601, 0.9987904967602591),
       "craze": (0.9996723020779033, 0.9996723020779027),
       "flare": (1.0000000000000004, 1.0),
       "barge": (0.9995680345572354, 0.9995680345572354),
       "shake": (0.9995680345572354, 0.9995680345572354),
       "drake": (1.0000000000000007, 1.0),
       "crave": (0.9995680345572354, 0.9995680345572354),
       "spite": (1.0000000000000002, 1.0),
       "siren": (1.0, 1.0),
       "cleat": (0.9995680345572362, 0.9995680345572354),
       "legal": (0.9982721382289413, 0.9982721382289417),
       "paler": (0.9996914532551685, 0.9996914532551682),
       "peace": (0.999568034557235, 0.9995680345572354),
       "haute": (0.9982721382289419, 0.9982721382289417),
       "swear": (0.9995680345572359, 0.9995680345572354),
       "relay": (0.9995680345572356, 0.9995680345572354),
       "eater": (0.9982056820069777, 0.9982056820069779),
       "cause": (0.9999999999999996, 1.0),
       "raise": (0.9991360691144706, 0.9991360691144708),
       "blade": (1.0, 1.0),
       "avert": (0.9995680345572364, 0.9995680345572354),
       "bagel": (0.9987041036717067, 0.9987041036717063),
       "tease": (0.9992800575953928, 0.9992800575953924),
       "grace": (0.9987041036717067, 0.9987041036717063),
       "cater": (0.9992191393919255, 0.9992191393919255),
       "stare": (0.9987041036717065, 0.9987041036717063),
       "flame": (1.0000000000000002, 1.0),
       "eclat": (0.9991360691144713, 0.9991360691144708),
       "shine": (0.9991360691144711, 0.9991360691144708),
       "yeast": (0.9982721382289417, 0.9982721382289417),
       "cream": (1.0000000000000009, 1.0),
       "eager": (0.9984308194119978, 0.9984308194119981),
       "clear": (0.9996495374709655, 0.9996495374709645),
    }


