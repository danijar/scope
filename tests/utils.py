import numpy as np


def equal(actuals, references, dtypes=None):
  dtypes = dtypes or [x.dtype for x in actuals]
  assert len(actuals) == len(references) == len(dtypes)
  references = [np.asarray(x, d) for x, d in zip(actuals, dtypes)]
  return all((x == y).all() for x, y in zip(actuals, references))
