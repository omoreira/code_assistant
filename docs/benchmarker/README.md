# Benchmarker

The `benchmarker` module manages benchmark specifications and generates a
Python benchmark harness in a target repository's root `benchmark/` folder.

```python
from benchmarker import BenchmarkGenerator

generator = BenchmarkGenerator("/path/to/new_assistant")
generator.create_specification()  # benchmark/benchmark.pseudo
generator.generate()             # benchmark/benchmark.py
```

Without an LLM interface, generation creates a command timing harness that
reports every run plus mean and median duration. Pass an LLM interface to
generate code tailored to the contents of `benchmark.pseudo`.

```bash
python -m benchmarker.benchmarker /path/to/new_assistant --create-spec
python -m benchmarker.benchmarker /path/to/new_assistant --generate
python /path/to/new_assistant/benchmark/benchmark.py --warmups 1 --iterations 5 -- python -m my_app
```

The generated harness accepts warm-up and iteration options before `--`, then
the command and its arguments after `--`.
