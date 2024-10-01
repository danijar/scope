import pathlib

import scope
import numpy as np


class TestFloat:

  def test_roundtrip(self, tmpdir):
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=0)
    writer.add(0, {'foo': 12})
    writer.add(5, {'foo': 42, 'bar': np.float64(np.pi)})
    writer.flush()
    assert {x.name for x in logdir.glob('*')} == {'foo.float', 'bar.float'}
    assert (logdir / 'foo.float').stat().st_size == (8 + 8) * 2
    assert (logdir / 'bar.float').stat().st_size == (8 + 8) * 1
    reader = scope.Reader(logdir)
    assert reader.keys() == tuple(sorted(['foo', 'bar']))
    assert reader.length('foo') == 2
    assert reader.length('bar') == 1
    assert equal(reader['foo'], ([0, 5], [12, 42]), (np.int64, np.float64))
    assert equal(reader['bar'], ([5], [np.pi]), (np.int64, np.float64))

  def test_workers(self, tmpdir):
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=8)
    for step in range(10):
      writer.add(step, {'foo': step, 'bar': step})
    writer.flush()
    writer.flush()  # Block until previous flush is done.
    assert {x.name for x in logdir.glob('*')} == {'foo.float', 'bar.float'}
    assert (logdir / 'foo.float').stat().st_size == (8 + 8) * 10
    assert (logdir / 'bar.float').stat().st_size == (8 + 8) * 10
    reader = scope.Reader(logdir)
    assert equal(reader['foo'], (np.arange(10), np.arange(10)))
    assert equal(reader['bar'], (np.arange(10), np.arange(10)))

  def test_namescopes(self, tmpdir):
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=0)
    writer.add(0, {'foo/bar': 12})
    writer.flush()
    assert {x.name for x in logdir.glob('*')} == {'foo-bar.float'}
    reader = scope.Reader(logdir)
    assert reader.keys() == ('foo/bar',)
    assert reader.length('foo/bar') == 1
    assert equal(reader['foo/bar'], ([0], [12]), (np.int64, np.float64))

  # def test_slicing(self, tmpdir):
  #   logdir = pathlib.Path(tmpdir)
  #   writer = scope.Writer(logdir, workers=0)
  #   writer.add(0, {'foo': 12})
  #   writer.add(5, {'foo': 42})
  #   writer.flush()
  #   reader = scope.Reader(logdir)
  #   assert equal(reader['foo', 0], ([0], [12]))
  #   assert equal(reader['foo', :2], ([0], [12]))
  #   assert equal(reader['foo', :5], ([0], [12]))
  #   assert equal(reader['foo', :6], ([0, 5], [12, 42]))
  #   assert equal(reader['foo', 1:6], ([5], [42]))
  #   assert equal(reader['foo', :-1], ([], []))
  #   assert equal(reader['foo', 7:], ([], []))


def equal(actuals, references, dtypes=None):
  dtypes = dtypes or [x.dtype for x in actuals]
  assert len(actuals) == len(references) == len(dtypes)
  references = [np.asarray(x, d) for x, d in zip(actuals, dtypes)]
  return all((x == y).all() for x, y in zip(actuals, references))
