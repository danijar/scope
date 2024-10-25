import pathlib

import scope
import numpy as np


class TestImage:

  def test_roundtrip(self, tmpdir):
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=0)
    img1 = np.ones((64, 128, 3), np.uint8) + 12
    img2 = np.ones((64, 128, 3), np.uint8) + 255
    writer.add(0, {'foo': img1})
    writer.add(5, {'foo': img2})
    writer.flush()
    assert {x.name for x in (logdir / 'scope').glob('*')} == {'foo.png'}
    assert (logdir / 'scope/foo.png/index').stat().st_size == (8 + 8) * 2
    assert len(list((logdir / 'scope/foo.png').glob('*'))) == 1 + 2
    reader = scope.Reader(logdir)
    assert reader.keys() == ('foo',)
    assert reader.length('foo') == 2
    steps, filenames = reader['foo']
    values = [reader.load('foo', x) for x  in filenames]
    assert (steps == np.array([0, 5])).all()
    assert (np.array(values) == np.array([img1, img2])).all()

  def test_workers(self, tmpdir):
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=8)
    for step in range(5):
      for key in ('foo', 'bar', 'baz'):
        writer.add(step, {key: np.full((64, 128, 3), step, np.uint8)})
    writer.flush()
    writer.flush()  # Block until previous flush is done.
    assert {x.name for x in (logdir / 'scope').glob('*')} == {
        'foo.png', 'bar.png', 'baz.png'}
    for key in ('foo', 'bar', 'baz'):
      assert (logdir / f'scope/{key}.png/index').stat().st_size == (8 + 8) * 5
      assert len(list((logdir / f'scope/{key}.png').glob('*'))) == 1 + 5
    reader = scope.Reader(logdir)
    assert reader.keys() == tuple(sorted(['foo', 'bar', 'baz']))
    for key in ('foo', 'bar', 'baz'):
      assert reader.length(key) == 5
      steps, filenames = reader[key]
      values = [reader.load(key, x) for x  in filenames]
      assert (steps == np.arange(5)).all()
      assert all(x.dtype == np.uint8 for x in values)
      reference = np.arange(5, dtype=np.uint8)[:, None, None, None]
      assert (np.array(values) == reference).all()

  def test_namescopes(self, tmpdir):
    img = np.ones((64, 128, 3), np.uint8) + 12
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=0)
    writer.add(0, {'foo/bar': img})
    writer.flush()
    assert {x.name for x in (logdir / 'scope').glob('*')} == {'foo-bar.png'}
    assert len(list((logdir / 'scope/foo-bar.png').glob('*'))) == 1 + 1
    reader = scope.Reader(logdir)
    assert reader.keys() == ('foo/bar',)
    assert reader.length('foo/bar') == 1
    _, filenames = reader['foo/bar']
    assert len(filenames) == 1
    assert (reader.load('foo/bar', filenames[0]) == img).all()
