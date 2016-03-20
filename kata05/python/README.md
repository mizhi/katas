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

Additionally, I do two things that may affect performance.
