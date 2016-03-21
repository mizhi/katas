Introduction
============

Implements a [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter).

`bloom.py` is self-contained module and driver program.
`test_bloom.py` is the test driver for this exercise.

The tests require the [flexmock](https://pypi.python.org/pypi/flexmock) mocking
package.

A virtualenv is probably the best way to go:

```sh
$ virtualenv --python=python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

To run the driver program, first activate the virtualenv, then run:

```sh
$ python bloom.py
```

To run tests:

```sh
$ python test_bloom.py
```

Hashing Function
================
The choice of MD5 as the hashing function is arbitrary in order to keep focused
on the kata. I've not bothered to confirm how uniformly distributed the hashes
it provides are.

Additionally, I do a few things that may affect performance:

1. I take the modulus of the computed hash by the bit capacity of the bitset. I
don't know how this affects where the bit positions wind up. It may be arguably
better to determine a required bitlength for the position index and fill the
bits into that from the MD5 in a deterministic way.

2. Bloom filters call for k hashing functions. In this case, I simply use MD5
repeatedly by updating the hash with repetitions of the element. It may be
better to use a mixture of hashing functions.

3. MD5 is probably pretty slow compared to other hashing functions, but it's
available and easy to use in Python.
