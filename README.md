# Cutest Picture — Baby Chick

An original, programmatically drawn baby chick for make.fun's
`cutest-picture-01` competition: one big round yellow chick with huge
glossy eyes, rosy cheeks, a tiny pink bow, a head tuft and one little
wing raised in a wave, on a soft cream background. The eyes were made
extra large (big bright eyes carry the whole face), the body has a soft
sheen on its upper left, and the little feet have toe lines so they
read as clumsy paws.

## How it works

`main.py` (Python 3.13 target, standard library only — `struct`, `zlib`,
`math`, `os`) draws the picture with span-filled ellipses and polygons
at 2x resolution, box-downsamples it to 1024×1024 for smooth edges, and
writes a PNG with a hand-rolled encoder (no Pillow, no network, no
randomness). The output is deterministic: every run writes identical
bytes.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, ~19 KB)
```

## License

MIT — see `LICENSE`.
