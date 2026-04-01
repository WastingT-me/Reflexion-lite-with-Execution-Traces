EASY_TASKS = [
    "HumanEval/0",   # has_close_elements
    "HumanEval/1",   # separate_paren_groups
    "HumanEval/2",   # truncate_number
    "HumanEval/3",   # below_zero
    "HumanEval/5",   # intersperse
    "HumanEval/8",   # sum_product
    "HumanEval/11",  # string_xor
    "HumanEval/12",  # longest
    "HumanEval/14",  # all_prefixes
    "HumanEval/18",  # how_many_times
]

MEDIUM_TASKS = [
    "HumanEval/6",   # parse_nested_parens
    "HumanEval/9",   # rolling_max
    "HumanEval/15",  # string_sequence
    "HumanEval/20",  # find_closest_elements
    "HumanEval/23",  # strlen
    "HumanEval/27",  # flip_case
    "HumanEval/30",  # get_positive
    "HumanEval/32",  # poly
    "HumanEval/34",  # unique
    "HumanEval/36",  # fizz_buzz
]

BUG_PRONE_TASKS = [
    "HumanEval/40",  # triples_sum_to_zero
    "HumanEval/43",  # pairs_sum_to_zero
    "HumanEval/46",  # fib4
    "HumanEval/48",  # is_palindrome
    "HumanEval/50",  # encode_shift
    "HumanEval/55",  # decode_shift
    "HumanEval/59",  # largest_prime_factor
    "HumanEval/63",  # fibfib
    "HumanEval/68",  # pluck
    "HumanEval/75",  # is_multiply_prime
]

SELECTED_TASK_IDS = EASY_TASKS + MEDIUM_TASKS + BUG_PRONE_TASKS

TRACE_TASK_IDS = [
    "HumanEval/3",   # below_zero
    "HumanEval/5",   # intersperse
    "HumanEval/8",   # sum_product
    "HumanEval/9",   # rolling_max
    "HumanEval/0",   # has_close_elements
]

assert len(SELECTED_TASK_IDS) == 30
assert len(set(SELECTED_TASK_IDS)) == 30


TASK_GROUP_BY_ID = {}
for t in EASY_TASKS:
    TASK_GROUP_BY_ID[t] = "easy"
for t in MEDIUM_TASKS:
    TASK_GROUP_BY_ID[t] = "medium"
for t in BUG_PRONE_TASKS:
    TASK_GROUP_BY_ID[t] = "bug-prone"


def get_group(task_id: str) -> str:
    return TASK_GROUP_BY_ID[task_id]