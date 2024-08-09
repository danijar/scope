import pathlib

import scope
import numpy as np


class TestVideo:

  def test_roundtrip(self, tmpdir):
    logdir = pathlib.Path(tmpdir)
    writer = scope.Writer(logdir, workers=0)
    vid1 = np.ones((5, 64, 128, 3), np.uint8) + 12
    vid2 = np.ones((5, 64, 128, 3), np.uint8) + 255
    writer.add(0, {'foo': vid1})
    writer.add(5, {'foo': vid2})
    writer.flush()
    assert {x.name for x in logdir.glob('*')} == {'foo.mp4'}
    assert (logdir / 'foo.mp4' / 'index').stat().st_size == (8 + 8) * 2
    assert len(list((logdir / 'foo.mp4').glob('*'))) == 1 + 2
    reader = scope.Reader(logdir)
    assert reader.keys() == ('foo',)
    assert reader.length('foo') == 2
    steps, values = reader['foo']
    assert (steps == np.array([0, 5])).all()
    assert np.allclose(values, [vid1, vid2], rtol=0.1)
