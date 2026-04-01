# Reflexion-lite with Execution Traces: Improving Code Generation with WebAssembly interpreter inside the transformer weights

This repo holds the code and log files for reproduction the [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366). As an innovation, a trace obtained from Transformer-VM has been added to the original reflexion. Transformer-VM is "A standard softmax-ReGLU transformer whose weights are computed analytically that correctly simulates a WebAssembly virtual machine on arbitrary programs" (see Percepta blog [Can LLMs Be Computers?](https://www.percepta.ai/blog/can-llms-be-computers)). 

## Methods

### `baseline`

Single-pass code generation and evaluation on the selected tasks.

### `reflexion-lite`

Baseline generation followed by iterative repair using execution error feedback.

### `reflexion+trace`

Same loop as `reflexion-lite`, but reflection feedback is extended with semantic trace feedback from transformer that simulates a WebAssembly virtual machine.

## Main parameters

### Required

* `--method`

  * `baseline`
  * `reflexion-lite`
  * `reflexion+trace`
  * `all`

### Optional

* `--model-name` — Hugging Face model name
* `--hf-token` — optional Hugging Face token
* `--results-dir` — output directory, default: `results`
* `--max-new-tokens` — generation length, default: `512`
* `--temperature` — generation temperature, default: `0.2`
* `--top-p` — nucleus sampling parameter, default: `0.95`
* `--timeout` — per-task execution timeout in seconds, default: `10`
* `--max-iters` — max attempts for `reflexion-lite` and `reflexion+trace`, default: `3`
* `--trace-only` — run only the 5 selected trace tasks

## Quick Start

```bash
python run.py --method baseline
```

for `reflexion+trace` on the pilot 5 tasks use `--trace-only` pls

```bash
python run.py --method reflexion+trace --trace-only
```

You can use your Hugging Face token by simply adding `--hf-token YOUR_TOKEN`

The description will be continued...