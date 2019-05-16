How to compile a specialized interpreter
========================================

`PYTHONPATH` must include `$(top_srcdir)/src"`


Step 1: Trace
-------------

First, make a trace file for the program you want to run fast. Currently, this
requires using another version of Mit, e.g. the "master" branch. Run it like
this:

    $ mit --trace /tmp/myprog.trace myprog [arguments]

An empty file is also acceptable as a trace file. Of course it won't make a
very fast interpreter. However, the option of using an empty trace file is
useful for bootstrapping.

Trace files can be slow to generate, so you may want to keep a library of
them. However, trace files can also be very big (hundreds of megabytes per
second of execution). Fortunately, trace files are extremely compressible.
The "zstd" compression tool achieves a 500:1 compression ratio.


Step 2: Predictor
-----------------

The script "gen-predictor" reads a trace file and approximates it by a
predictor: a lookup table that guesses the next instruction based on the
previous instructions. Run it like this:

    $ ./gen-predictor myprog.trace myprog.predictor_pickle

The result will be written to "myprog.predictor_pickle".

The script is slow, because it has to replay the whole trace. You may want to
keep a library of predictor files, which are typically small (tens of
kilobytes). It is for this reason that the "gen-predictor" script has been
separated out from the rest of the procedure.


Step 3: Labels
--------------

The script "gen-labels" reads a predictor file and constructs a suitable
control-flow graph for the specialized interpreter. Run it like this:

    $ ./gen-labels myprog.predictor_pickle myprog.labels_pickle

The result will be written to "myprog.labels_pickle".

The script is fast, but it has nonetheless been separated out from the rest of
the procedure, so that it is possible to generate a ".labels_pickle" file in
other ways, if desired, or to distribute them.


Step 4: Instructions
--------------------

The script "gen-specializer" reads a labels file and writes out a C source
file. Run it like this:

    $ ./gen-specializer my_prog.labels_pickle >instructions.c