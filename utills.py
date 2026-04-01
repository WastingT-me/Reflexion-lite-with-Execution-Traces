import ast
import io
import os
import re
import json
import traceback
import contextlib
import multiprocessing as mp
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"


def ensure_results_dir(path: str = "results") -> None:
    os.makedirs(path, exist_ok=True)


def save_jsonl(path: str, rows: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_humaneval_dataset() -> List[Dict[str, Any]]:
    ds = load_dataset("openai/openai_humaneval", split="test")
    return [dict(row) for row in ds]


def filter_dataset_by_task_ids(
    dataset_rows: List[Dict[str, Any]],
    task_ids: List[str],
) -> List[Dict[str, Any]]:
    task_ids_set = set(task_ids)
    return [row for row in dataset_rows if row["task_id"] in task_ids_set]


def take_last_attempt_per_task(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best = {}
    for row in rows:
        task_id = row["task_id"]
        if task_id not in best or row["attempt"] > best[task_id]["attempt"]:
            best[task_id] = row
    return list(best.values())


def load_model_and_tokenizer(
    model_name: str = DEFAULT_MODEL_NAME,
    hf_token: Optional[str] = None,
):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        token=hf_token if hf_token else None,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        token=hf_token if hf_token else None,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
    )
    model.eval()
    return tokenizer, model


@torch.inference_mode()
def generate_from_prompt(
    prompt: str,
    tokenizer,
    model,
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.95,
) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    do_sample = temperature > 0

    gen_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if do_sample:
        gen_kwargs["temperature"] = temperature
        gen_kwargs["top_p"] = top_p

    outputs = model.generate(**inputs, **gen_kwargs)
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


def build_baseline_prompt(problem: Dict[str, Any]) -> str:
    return f"""You are solving a HumanEval Python programming task.

Write a complete correct Python solution for the function below.
Return only Python code.

{problem['prompt']}
"""


def build_reflection_prompt(
    problem: Dict[str, Any],
    previous_code: str,
    feedback_text: str,
) -> str:
    return f"""You are improving a previous failed solution to a HumanEval Python task.

Task:
{problem['prompt']}

Previous solution:
```python
{previous_code}
```

Feedback from execution:
{feedback_text}

Write a corrected complete Python solution.
Return only Python code.
"""


def build_trace_reflection_prompt(
    problem: Dict[str, Any],
    previous_code: str,
    trace_feedback: str,
    execution_feedback: str,
) -> str:
    return f"""You are improving a previous failed solution to a HumanEval Python task.

Task:
{problem['prompt']}

Previous solution:
```python
{previous_code}
```

Semantic trace feedback:
{trace_feedback}

Feedback from execution:
{execution_feedback}

Write a corrected complete Python solution.
Return only Python code.
"""


def extract_python_code(text: str) -> str:
    text = text.strip()

    blocks = re.findall(r"```python\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if blocks:
        return blocks[0].strip()

    blocks = re.findall(r"```\s*(.*?)```", text, flags=re.DOTALL)
    if blocks:
        return blocks[0].strip()

    return text


def shorten_text(text: str, max_len: int = 1200) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "\n... <truncated>"


def shorten_error(error_text: Optional[str]) -> Optional[str]:
    if not error_text:
        return None
    return error_text.replace("\n", " ").strip()


def print_task_status(
    task_id: str,
    group: str,
    passed: bool,
    error_text: Optional[str] = None,
) -> None:
    if passed:
        print(f"{task_id} ({group}) PASSED")
    else:
        print(f"{task_id} ({group}) FAILED Error: {shorten_error(error_text)}")


def _run_code_worker(queue, problem: Dict[str, Any], generated_code: str) -> None:
    try:
        namespace = {}
        full_program = (
            generated_code.strip()
            + "\n\n"
            + problem["test"]
            + f"\ncheck({problem['entry_point']})"
        )

        stdout_buffer = io.StringIO()
        with contextlib.redirect_stdout(stdout_buffer):
            exec(full_program, namespace, namespace)

        queue.put({
            "passed": True,
            "error": None,
            "stdout": stdout_buffer.getvalue(),
        })
    except Exception as e:
        queue.put({
            "passed": False,
            "error": repr(e),
            "stdout": traceback.format_exc(),
        })


def run_code_with_tests(
    problem: Dict[str, Any],
    generated_code: str,
    timeout: int = 10,
) -> Tuple[bool, Optional[str], str]:
    queue = mp.Queue()
    proc = mp.Process(target=_run_code_worker, args=(queue, problem, generated_code))
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return False, 'TimeoutError("Execution timed out")', ""

    if queue.empty():
        return False, 'RuntimeError("No result returned from worker")', ""

    result = queue.get()
    return result["passed"], result["error"], result["stdout"]


def compute_group_metrics(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    by_group = defaultdict(list)

    for row in rows:
        by_group[row["group"]].append(int(row["passed"]))

    metrics = {}
    for group in ["easy", "medium", "bug-prone"]:
        vals = by_group.get(group, [])
        metrics[group] = sum(vals) / len(vals) if vals else 0.0

    return metrics


def print_method_comparison_table(
    baseline_rows: List[Dict[str, Any]],
    other_rows: List[Dict[str, Any]],
    other_label: str = "R-1",
) -> None:
    baseline_metrics = compute_group_metrics(baseline_rows)
    other_metrics = compute_group_metrics(other_rows)

    print()
    print(f'{"Group":<12} {"Baseline":<10} {other_label:<10}')
    print("-" * 34)
    print(f'{"Easy":<12} {baseline_metrics["easy"]:<10.1f} {other_metrics["easy"]:<10.1f}')
    print(f'{"Medium":<12} {baseline_metrics["medium"]:<10.1f} {other_metrics["medium"]:<10.1f}')
    print(f'{"Bug-prone":<12} {baseline_metrics["bug-prone"]:<10.1f} {other_metrics["bug-prone"]:<10.1f}')


def solve_task_baseline(
    problem: Dict[str, Any],
    group: str,
    tokenizer,
    model,
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.95,
    timeout: int = 10,
) -> Dict[str, Any]:
    prompt = build_baseline_prompt(problem)
    raw_output = generate_from_prompt(
        prompt=prompt,
        tokenizer=tokenizer,
        model=model,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    code = extract_python_code(raw_output)

    passed, error_text, exec_output = run_code_with_tests(
        problem=problem,
        generated_code=code,
        timeout=timeout,
    )

    row = {
        "task_id": problem["task_id"],
        "entry_point": problem["entry_point"],
        "group": group,
        "method": "baseline",
        "attempt": 1,
        "prompt": prompt,
        "generated_code": code,
        "test_passed": passed,
        "error_text": error_text,
        "reflection_text": "",
        "passed": passed,
        "error": error_text,
        "exec_output": exec_output,
    }

    print_task_status(problem["task_id"], group, passed, error_text)
    return row


def solve_task_reflexion_lite(
    problem: Dict[str, Any],
    group: str,
    tokenizer,
    model,
    max_iters: int = 3,
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.95,
    timeout: int = 10,
) -> List[Dict[str, Any]]:
    rows = []

    prompt = build_baseline_prompt(problem)
    raw_output = generate_from_prompt(
        prompt=prompt,
        tokenizer=tokenizer,
        model=model,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    code = extract_python_code(raw_output)

    passed, error_text, exec_output = run_code_with_tests(
        problem=problem,
        generated_code=code,
        timeout=timeout,
    )

    rows.append({
        "task_id": problem["task_id"],
        "entry_point": problem["entry_point"],
        "group": group,
        "method": "reflexion",
        "attempt": 1,
        "prompt": prompt,
        "generated_code": code,
        "test_passed": passed,
        "error_text": error_text,
        "reflection_text": "",
        "passed": passed,
        "error": error_text,
        "exec_output": exec_output,
    })

    if passed:
        print_task_status(problem["task_id"], group, True, None)
        return rows

    previous_code = code
    previous_error = error_text

    for attempt in range(2, max_iters + 1):
        reflection_text = f"Execution failed with error:\n{previous_error or 'UnknownError'}"
        reflection_text = shorten_text(reflection_text)

        prompt = build_reflection_prompt(
            problem=problem,
            previous_code=previous_code,
            feedback_text=reflection_text,
        )

        raw_output = generate_from_prompt(
            prompt=prompt,
            tokenizer=tokenizer,
            model=model,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        code = extract_python_code(raw_output)

        passed, error_text, exec_output = run_code_with_tests(
            problem=problem,
            generated_code=code,
            timeout=timeout,
        )

        rows.append({
            "task_id": problem["task_id"],
            "entry_point": problem["entry_point"],
            "group": group,
            "method": "reflexion",
            "attempt": attempt,
            "prompt": prompt,
            "generated_code": code,
            "test_passed": passed,
            "error_text": error_text,
            "reflection_text": reflection_text,
            "passed": passed,
            "error": error_text,
            "exec_output": exec_output,
        })

        if passed:
            print_task_status(problem["task_id"], group, True, None)
            return rows

        previous_code = code
        previous_error = error_text

    print_task_status(problem["task_id"], group, False, previous_error)
    return rows


def solve_task_reflexion_trace(
    problem: Dict[str, Any],
    group: str,
    trace_feedback: str,
    tokenizer,
    model,
    max_iters: int = 3,
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.95,
    timeout: int = 10,
) -> List[Dict[str, Any]]:
    rows = []

    prompt = build_baseline_prompt(problem)
    raw_output = generate_from_prompt(
        prompt=prompt,
        tokenizer=tokenizer,
        model=model,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    code = extract_python_code(raw_output)

    passed, error_text, exec_output = run_code_with_tests(
        problem=problem,
        generated_code=code,
        timeout=timeout,
    )

    rows.append({
        "task_id": problem["task_id"],
        "entry_point": problem["entry_point"],
        "group": group,
        "method": "reflexion+trace",
        "attempt": 1,
        "prompt": prompt,
        "generated_code": code,
        "test_passed": passed,
        "error_text": error_text,
        "reflection_text": "",
        "trace_feedback": "",
        "passed": passed,
        "error": error_text,
        "exec_output": exec_output,
    })

    if passed:
        print_task_status(problem["task_id"], group, True, None)
        return rows

    previous_code = code
    previous_error = error_text
    trace_feedback_short = shorten_text(trace_feedback)

    for attempt in range(2, max_iters + 1):
        execution_feedback = f"Execution failed with error:\n{previous_error or 'UnknownError'}"
        execution_feedback = shorten_text(execution_feedback)
        reflection_text = trace_feedback_short + "\n\n" + execution_feedback

        prompt = build_trace_reflection_prompt(
            problem=problem,
            previous_code=previous_code,
            trace_feedback=trace_feedback_short,
            execution_feedback=execution_feedback,
        )

        raw_output = generate_from_prompt(
            prompt=prompt,
            tokenizer=tokenizer,
            model=model,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        code = extract_python_code(raw_output)

        passed, error_text, exec_output = run_code_with_tests(
            problem=problem,
            generated_code=code,
            timeout=timeout,
        )

        rows.append({
            "task_id": problem["task_id"],
            "entry_point": problem["entry_point"],
            "group": group,
            "method": "reflexion+trace",
            "attempt": attempt,
            "prompt": prompt,
            "generated_code": code,
            "test_passed": passed,
            "error_text": error_text,
            "reflection_text": reflection_text,
            "trace_feedback": trace_feedback_short,
            "passed": passed,
            "error": error_text,
            "exec_output": exec_output,
        })

        if passed:
            print_task_status(problem["task_id"], group, True, None)
            return rows

        previous_code = code
        previous_error = error_text

    print_task_status(problem["task_id"], group, False, previous_error)
    return rows


def extract_humaneval_tests_for_tasks(
    selected_tasks: List[Dict[str, str]],
    dataset_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    by_task_id = {row["task_id"]: row for row in dataset_rows}

    def get_source_segment_safe(source: str, node: ast.AST) -> str:
        seg = ast.get_source_segment(source, node)
        if seg is not None:
            return seg
        try:
            return ast.unparse(node)
        except Exception:
            return repr(node)

    def literal_eval_safe(node: ast.AST) -> Any:
        try:
            return ast.literal_eval(node)
        except Exception as e:
            raise ValueError(f"Cannot literal-eval node: {ast.dump(node)}") from e

    def find_candidate_call(node: ast.AST) -> Optional[ast.Call]:
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "candidate":
                return node
            for arg in node.args:
                found = find_candidate_call(arg)
                if found is not None:
                    return found
            for kw in node.keywords:
                found = find_candidate_call(kw.value)
                if found is not None:
                    return found
        for child in ast.iter_child_nodes(node):
            found = find_candidate_call(child)
            if found is not None:
                return found
        return None

    def extract_expected_from_assert_test(test_node: ast.AST) -> Any:
        if (
            isinstance(test_node, ast.Compare)
            and len(test_node.ops) == 1
            and len(test_node.comparators) == 1
        ):
            left = test_node.left
            right = test_node.comparators[0]
            left_has_candidate = find_candidate_call(left) is not None
            right_has_candidate = find_candidate_call(right) is not None
            if left_has_candidate and not right_has_candidate:
                return literal_eval_safe(right)
            if right_has_candidate and not left_has_candidate:
                return literal_eval_safe(left)
            raise ValueError("Could not determine expected side in comparison.")

        if isinstance(test_node, ast.Call) and find_candidate_call(test_node) is not None:
            return True

        if isinstance(test_node, ast.UnaryOp) and isinstance(test_node.op, ast.Not):
            if find_candidate_call(test_node.operand) is not None:
                return False

        raise ValueError(f"Unsupported assert form: {ast.dump(test_node)}")

    def extract_assert_cases(test_code: str) -> List[Dict[str, Any]]:
        tree = ast.parse(test_code)
        cases = []

        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name != "check":
                continue

            assert_index = 0
            for stmt in node.body:
                if not isinstance(stmt, ast.Assert):
                    continue
                try:
                    candidate_call = find_candidate_call(stmt.test)
                    if candidate_call is None:
                        continue
                    args = [literal_eval_safe(arg) for arg in candidate_call.args]
                    expected = extract_expected_from_assert_test(stmt.test)
                except Exception as e:
                    cases.append({
                        "assert_index": assert_index,
                        "call_expr": get_source_segment_safe(test_code, stmt),
                        "args": None,
                        "expected": None,
                        "assertion_source": get_source_segment_safe(test_code, stmt),
                        "parse_error": str(e),
                    })
                    assert_index += 1
                    continue

                cases.append({
                    "assert_index": assert_index,
                    "call_expr": get_source_segment_safe(test_code, candidate_call),
                    "args": args,
                    "expected": expected,
                    "assertion_source": get_source_segment_safe(test_code, stmt),
                })
                assert_index += 1

        return cases

    out_rows = []

    for item in selected_tasks:
        task_id = item["task_id"]
        entry_point = item["entry_point"]

        if task_id not in by_task_id:
            raise KeyError(f"{task_id} not found in HumanEval dataset")

        row = by_task_id[task_id]
        raw_test = row["test"]
        extracted = extract_assert_cases(raw_test)

        out_rows.append({
            "task_id": task_id,
            "entry_point": entry_point,
            "raw_test": raw_test,
            "asserts": extracted,
        })

    return out_rows