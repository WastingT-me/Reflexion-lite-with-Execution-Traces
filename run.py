# run.py

import argparse
import os

from task_registry import (
    SELECTED_TASK_IDS,
    TRACE_TASK_IDS,
    get_group,
)

from utils import (
    ensure_results_dir,
    load_humaneval_dataset,
    filter_dataset_by_task_ids,
    load_model_and_tokenizer,
    solve_task_baseline,
    solve_task_reflexion_lite,
    take_last_attempt_per_task,
    save_jsonl,
    print_method_comparison_table,
)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--method",
        type=str,
        required=True,
        choices=["baseline", "reflexion-lite", "reflexion+trace", "all"],
    )

    parser.add_argument("--model-name", type=str, default="mistralai/Mistral-7B-Instruct-v0.3")
    parser.add_argument("--hf-token", type=str, default=None)

    parser.add_argument("--results-dir", type=str, default="results")

    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--timeout", type=int, default=10)

    parser.add_argument("--max-iters", type=int, default=3)

    parser.add_argument(
        "--trace-only",
        action="store_true",
        help="Run only 5 selected trace tasks",
    )

    return parser.parse_args()


def run_baseline(args, dataset_rows, tokenizer, model):
    results = []

    for problem in dataset_rows:
        task_id = problem["task_id"]
        group = get_group(task_id)

        row = solve_task_baseline(
            problem=problem,
            group=group,
            tokenizer=tokenizer,
            model=model,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            timeout=args.timeout,
        )

        results.append(row)

    save_jsonl(os.path.join(args.results_dir, "baseline.jsonl"), results)
    return results


def run_reflexion_lite(args, dataset_rows, tokenizer, model):
    all_rows = []

    for problem in dataset_rows:
        task_id = problem["task_id"]
        group = get_group(task_id)

        rows = solve_task_reflexion_lite(
            problem=problem,
            group=group,
            tokenizer=tokenizer,
            model=model,
            max_iters=args.max_iters,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            timeout=args.timeout,
        )

        all_rows.extend(rows)

    save_jsonl(os.path.join(args.results_dir, "reflexion_lite.jsonl"), all_rows)
    return all_rows


def run_reflexion_trace(*args, **kwargs):
    raise NotImplementedError("reflexion+trace будет добавлен позже")


def main():
    args = parse_args()

    ensure_results_dir(args.results_dir)

    dataset_rows = load_humaneval_dataset()

    target_ids = TRACE_TASK_IDS if args.trace_only else SELECTED_TASK_IDS
    dataset_rows = filter_dataset_by_task_ids(dataset_rows, target_ids)

    tokenizer, model = load_model_and_tokenizer(
        model_name=args.model_name,
        hf_token=args.hf_token,
    )

    if args.method == "baseline":
        run_baseline(args, dataset_rows, tokenizer, model)
        return

    if args.method == "reflexion-lite":
        baseline_rows = run_baseline(args, dataset_rows, tokenizer, model)
        reflexion_rows = run_reflexion_lite(args, dataset_rows, tokenizer, model)

        reflexion_final = take_last_attempt_per_task(reflexion_rows)

        print_method_comparison_table(
            baseline_rows,
            reflexion_final,
            other_label="R-1",
        )
        return

    if args.method == "reflexion+trace":
        run_reflexion_trace(args, dataset_rows, tokenizer, model)
        return

    if args.method == "all":
        baseline_rows = run_baseline(args, dataset_rows, tokenizer, model)
        reflexion_rows = run_reflexion_lite(args, dataset_rows, tokenizer, model)

        reflexion_final = take_last_attempt_per_task(reflexion_rows)

        print_method_comparison_table(
            baseline_rows,
            reflexion_final,
            other_label="R-1",
        )

        try:
            run_reflexion_trace(args, dataset_rows, tokenizer, model)
        except NotImplementedError as e:
            print(str(e))


if __name__ == "__main__":
    main()