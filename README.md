# YABAFOC: Yet Another BrAinFuck Optimizing Compiler

YABAFOC is an optimizing brainfuck compiler written in python.

# Requirements

YABAFOC requires gcc in path currently but hopefully will support other C Compilers

# Speed

YABAFOC is the best in class; Outpacing [El brainfuck](https://copy.sh/brainfuck), [bfc](https://github.com/Wilfred/bfc), and even [Ρ‴ (Tritium)](https://github.com/rdebath/Brainfuck/tree/master/tritium) (somehow)
(We also outpace [Speedfuck](https://github.com/M4GNV5/Geschwindigkeitsficken) according to their readme but I didn't download and check it.)

To get the most speed out of YABAFOC, run it with the `--unsafe-optimizations` flag. This can increase speed up to 2x and more.

## But I want proof of YABAFOC's speed.

Well, download and run it yourself...

But if I must, here are the timing results for common benchmarks (on my machine):


`mandelbrot.b`: 276ms

`hanoi.b`: 4ms

`golden.b`: 7ms

`beer.b`: 2ms

`bench.b`: 2ms


As you can see, all of these are easily completed ahead of the competition (I'm going to regret saying this aren't I)

Because of this, I created my own benchmark: [fib40](/benchmarks/fib40.bff) ([Precompiled](/benchmarks/fib40.b))

YABAFOC runs fib40 in `12s 285ms`

For comparison, BFC takes `44s 935ms` and P‴ takes `17s 753ms`
