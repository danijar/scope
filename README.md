# 🔬 Scope

Scalable metrics logging and analysis.

## Features

- 🚀 **Scalable:** Quickly log and view petabytes of metrics, thousands of keys, and large videos.
- 🎞️ **Formats:** Log and view scalars, text, images, and videos. Easy to extend with custom formats.
- 🧑🏻‍🔬 **Productivity:** Metrics viewer with focus on power users and full keyboard support.
- ☁️ **Cloud support:** Directly write to and read from Cloud storage via pathlib interface.
- 🍃 **Lightweight:** The writer and reader measure only ~400 lines of Python code.
- 🧱 **Reliability:** Unit tested and used across diverse research projects.

## Usage

### Installation

```sh
pip install scope
```

### Writing

```python
import scope

writer = scope.Writer(logdir)
for step in range(3)
  video = np.zeros((100, 640, 360, 3), np.uint8)
  writer.add(step, {'foo': 42, 'bar': video, 'baz': 'Hello World'})
writer.flush()
```

### Viewing

```sh
python -m scope.viewer --basedir ... --port 8000
```

### Reading

```python
import scope

reader = scope.Reader(logdir)
print(reader.keys())               # ('foo', 'bar', 'baz')

print(reader.length('foo'))        # 3
steps, values = reader['foo']
print(steps)                       # np.array([0, 1, 2], np.int64)
print(values)                      # np.array([42, 42, 42], np.float64)

steps, filenames = reader['bar']
reader.load('bar', filenames[-1])  # np.zeros((100, 640, 360, 3), np.uint8)
```
