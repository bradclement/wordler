# wordler
Python that finds the optimal policy to play wordle (including the best initial guess).

Run wordler.py with a debugger so that you can stop it before it uses all of the RAM on your
computer.  It will first take 2 or 3 hours to precompute a matrix for quick determination
of remaining candidate words after a guess.  It is written to file (1.5 GB) so that the next time
you run, you don't have to wait 2 or 3 hours to recompute it.

Then, a policy will be computed for an indefinite time to determine the likelihoods of winning 
for each word as an initial guess. 

At the end of wordler.py in the test() function are some commented out lines for testing on
easier sets of words.  That may be a better way to get more familiar with how it works.

After precomputing the matrix, occasionally, a line for progress is written out:

    - - - [] - - -
    - - - [] - - -
    - - - [] - - -
    - - - [] - - -

Essentially, nothing has completed, yet.  But, you may eventually see

    - - - [('parse', 1.0)] - - -

This means that the policy converged for the initial guess, "parse," with a 1.0 (100%)
probability of guessing a word in 6 guesses.  Eventually, other words will converge.
Spoiler alert!  "parse" is the only word we've found so far that has a guaranteed 
always-win policy.  The guess policy for some other good choices will fail for one or
two out of the 2315 words.

There is a done() function that determines when to stop searching.  By default, it tries to
compute an optimal policy for each word (aka guess) with this line: 

    return all_guesses_done(s)

You can instead use the commented out line above to stop the search when one word
converges on a 1.0 probability of success:

    return converged(s)

wordle.py has a long discussion in comments at the top that describes how the code works.
