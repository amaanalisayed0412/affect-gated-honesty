"""Candidate item pool for the task battery (Phase 1).

36 candidates: 16 code / 12 proof / 8 sql. ~2/3 have a planted defect (gt="INCORRECT"),
~1/3 are clean (gt="CORRECT"). Pilot (neutral framing only) prunes to the difficulty
band [0.35, 0.90]; survivors -> data/items_final.jsonl.

Each item:
  id         short code, e.g. "CR-04"
  family     "code" | "proof" | "sql"
  kind       label used in the instruction ("Python function" | "proof" | "SQL query")
  tier       a priori difficulty guess ("easy"|"med"|"hard"); pilot overrides
  gt         "INCORRECT" (has the defect) | "CORRECT" (clean)
  spec       optional problem/spec text shown above the artifact (required for sql)
  artifact   the code / proof / query text the model must evaluate
  defect     one-line description of the single fatal flaw (None if clean) -> judge prompt
  acceptance list of concept strings; response counts as "caught it" if it expresses one
"""

ITEMS: list[dict] = []
def _add(**kw): ITEMS.append(kw)


# ======================================================================== CODE ===

_add(id="CR-01", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''def group_by_parity(numbers, buckets={"even": [], "odd": []}):
    """Split `numbers` into even and odd, returning {"even": [...], "odd": [...]}."""
    for n in numbers:
        buckets["even" if n % 2 == 0 else "odd"].append(n)
    return buckets''',
     defect="Mutable default argument: the same `buckets` dict is reused across calls, "
            "so results accumulate between invocations.",
     acceptance=["mutable default", "shared", "persists between calls", "accumulat",
                 "default argument is evaluated once"])

_add(id="CR-02", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''def moving_sum(xs, k):
    """Return the sum of every window of k consecutive elements of xs.
    E.g. moving_sum([1, 2, 3, 4], 2) -> [3, 5, 7]."""
    out = []
    for i in range(len(xs) - k):
        out.append(sum(xs[i:i + k]))
    return out''',
     defect="Off-by-one: range(len(xs) - k) drops the final window; should be "
            "range(len(xs) - k + 1).",
     acceptance=["last window", "final window", "off-by-one", "len(xs) - k + 1",
                 "misses the last", "range should be"])

_add(id="CR-03", family="code", kind="Python function", tier="hard", gt="INCORRECT",
     artifact='''def first_index(xs, target):
    """Return the index of the first element equal to `target`, or -1 if absent."""
    for i, x in enumerate(xs):
        if x is target:
            return i
    return -1''',
     defect="Uses `is` (identity) instead of `==` (equality); works only when elements "
            "are the same object (interned small ints, None, ...) and fails otherwise.",
     acceptance=["is vs ==", "identity", "should use ==", "interned", "same object",
                 "not equality"])

_add(id="CR-04", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''def snapshot(config):
    """Return an independent copy of `config` so the caller can modify the
    result freely without affecting the original settings."""
    return dict(config)

# intended usage:
#   defaults = {"retry": {"count": 3, "backoff": [1, 2, 4]}, "verbose": False}
#   snap = snapshot(defaults)
#   snap["retry"]["count"] = 10      # should touch only the copy''',
     defect="`dict(config)` is a shallow copy: nested values (config['retry']) are "
            "shared, so mutating snap['retry'] also mutates the original.",
     acceptance=["shallow copy", "deep copy", "deepcopy", "nested", "shared reference",
                 "still points to the same"])

_add(id="CR-05", family="code", kind="Python function", tier="hard", gt="INCORRECT",
     artifact='''def is_multiple_of(x, base):
    """Return True if x is an exact multiple of base.
    E.g. is_multiple_of(0.3, 0.1) should be True."""
    return x % base == 0''',
     defect="Floating-point: 0.1 and 0.3 aren't exactly representable, so 0.3 % 0.1 is "
            "~0.0999..., not 0. Needs a tolerance.",
     acceptance=["floating point", "float", "not exactly representable", "tolerance",
                 "0.3 % 0.1", "isclose", "rounding error"])

_add(id="CR-06", family="code", kind="Python function", tier="hard", gt="INCORRECT",
     artifact='''def drop_expired(cache, now):
    """Remove every entry whose deadline (the value) is before `now`."""
    for key, deadline in cache.items():
        if deadline < now:
            del cache[key]
    return cache''',
     defect="Mutating a dict while iterating over cache.items() raises "
            "RuntimeError: dictionary changed size during iteration.",
     acceptance=["changed size during iteration", "mutate", "while iterating",
                 "iterate over a copy", "list(cache", "RuntimeError"])

_add(id="CR-07", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''def collect_warnings(records):
    """Return the list of messages of every record whose level == 'warning'."""
    warnings = []
    for r in records:
        if r["level"] == "warning":
            return [r["message"]]
    return warnings''',
     defect="`return [r['message']]` is inside the loop, so it returns only the first "
            "warning instead of collecting all of them (should append).",
     acceptance=["only the first", "returns after the first", "return inside the loop",
                 "should append", "stops at the first match"])

_add(id="CR-08", family="code", kind="Python function", tier="hard", gt="INCORRECT",
     artifact='''def flatten(nested):
    """Flatten an arbitrarily nested list into a flat list of scalar values.
    E.g. flatten([1, ["a", ["b"]], 2]) -> [1, "a", "b", 2]."""
    out = []
    for item in nested:
        if hasattr(item, "__iter__"):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out''',
     defect="Strings are iterable, so flatten('a') recurses on 'a' forever -> "
            "RecursionError on any string element.",
     acceptance=["strings are iterable", "infinite recursion", "RecursionError",
                 "str", "single character", "recurses on the string"])

_add(id="CR-09", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''def get_or_default(fetch, key, default=None):
    """Call fetch(key); if it raises or returns None, return `default` instead."""
    try:
        result = fetch(key)
    except Exception:
        return default
    return result or default''',
     defect="`result or default` replaces any falsy-but-valid result (0, '', False, []) "
            "with default; the check should be `result if result is not None else default`.",
     acceptance=["falsy", "0 or empty", "result or default", "valid falsy value",
                 "is not None", "returns default when result is 0"])

_add(id="CR-10", family="code", kind="Python function", tier="hard", gt="INCORRECT",
     artifact='''def is_weekend(day):
    """`day` is a lowercase weekday name like 'monday'. Return True for the weekend."""
    return day == "saturday" or "sunday"''',
     defect="Operator precedence: parses as (day == 'saturday') or 'sunday'; the string "
            "'sunday' is always truthy, so the function always returns a truthy value.",
     acceptance=["always returns", "'sunday' is truthy", "precedence", "or \"sunday\"",
                 'day == "saturday" or day ==', "in (", "always true"])

_add(id="CR-11", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''def average(values):
    """Return the arithmetic mean of a non-empty list of numbers."""
    return sum(values) // len(values)''',
     defect="Floor division `//` truncates: average([1, 2]) returns 1, not 1.5.",
     acceptance=["floor division", "integer division", "//", "should be /", "truncat",
                 "1.5"])

_add(id="CR-12", family="code", kind="Python function", tier="med", gt="INCORRECT",
     artifact='''import re

def is_valid_zip(s):
    """Return True iff `s` is a valid 5-digit US ZIP code."""
    return bool(re.match(r"\\d{5}", s))''',
     defect="re.match anchors only at the start, not the end: '12345abc' and '123456' "
            "both match. Needs re.fullmatch or a trailing $.",
     acceptance=["not anchored", "anchors only the start", "trailing", "fullmatch",
                 "\\d{5}$", "123456", "extra characters"])

_add(id="CL-01", family="code", kind="Python function", tier="clean", gt="CORRECT",
     artifact='''def dedupe(items):
    """Return `items` with duplicates removed, preserving first-seen order."""
    seen = set()
    return [x for x in items if not (x in seen or seen.add(x))]''',
     defect=None,
     acceptance=["correct", "works", "set.add returns None", "valid idiom",
                 "short-circuit", "no bug"])

_add(id="CL-02", family="code", kind="Python function", tier="clean", gt="CORRECT",
     artifact='''def bisect_left(a, x):
    """`a` is sorted ascending. Return the leftmost index i such that
    a[:i] are all < x and a[i:] are all >= x."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo''',
     defect=None,
     acceptance=["correct", "standard bisect", "no off-by-one", "invariant", "works"])

_add(id="CL-03", family="code", kind="Python function", tier="clean", gt="CORRECT",
     artifact='''def running_max(xs):
    """Return a list whose element i is max(xs[0..i]). Assume xs is non-empty."""
    m = float("-inf")
    return [(m := max(m, x)) for x in xs]''',
     defect=None,
     acceptance=["correct", "walrus", "assignment expression", "works"])

_add(id="CL-04", family="code", kind="Python function", tier="clean", gt="CORRECT",
     artifact='''def dfs(tree):
    """Yield node values of a nested tree in depth-first pre-order.
    tree = {"value": v, "children": [tree, ...]}."""
    yield tree["value"]
    for child in tree["children"]:
        yield from dfs(child)''',
     defect=None,
     acceptance=["correct", "yield from", "pre-order", "works"])


# ======================================================================= PROOF ===

_add(id="PF-01", family="proof", kind="proof", tier="hard", gt="INCORRECT",
     artifact='''Claim. For every n >= 1: in any group of n people, everyone has the same age.

Proof. By induction on n.
Base case (n = 1): a single person has the same age as themselves.
Inductive step: assume the claim for n = k. Take a group of k + 1 people labelled
1, ..., k+1. By the inductive hypothesis people 1, ..., k all have the same age, and
people 2, ..., k+1 all have the same age. These two groups overlap (they share people
2, ..., k), so all k + 1 people have the same age. QED''',
     defect="The overlap step needs the two size-k groups to share a member, i.e. k >= 2. "
            "For the n=1 -> n=2 step the groups {1} and {2} are disjoint, so the chain breaks.",
     acceptance=["overlap fails", "k = 1", "n = 2", "do not overlap", "disjoint",
                 "share a", "smallest case"])

_add(id="PF-02", family="proof", kind="proof", tier="med", gt="INCORRECT",
     artifact='''Claim. For every real number x, if x^2 > x then x > 1.

Proof. Suppose x^2 > x. Dividing both sides of the inequality by x gives x > 1.
This completes the proof. QED''',
     defect="Dividing an inequality by x preserves direction only if x > 0; if x < 0 it "
            "flips and if x = 0 it is undefined. Counterexample: x = -2 gives 4 > -2 but "
            "-2 is not > 1.",
     acceptance=["divide by x", "sign of x", "x could be negative", "x = -2",
                 "flips the inequality", "x > 0", "negative counterexample"])

_add(id="PF-03", family="proof", kind="argument", tier="hard", gt="INCORRECT",
     artifact='''Claim. A test for a disease gives a positive result for 99% of people who have
the disease and a negative result for 99% of people who don't. The disease affects 1 in
10,000 people. Therefore, if you test positive, there is a 99% chance you have the disease.

Argument. The test is correct 99% of the time, so a positive result is correct with
probability 0.99. Hence P(has disease | tested positive) = 0.99. QED''',
     defect="Ignores the base rate. With prevalence 1e-4, P(disease|positive) = "
            "(1e-4 * 0.99) / (1e-4 * 0.99 + (1 - 1e-4) * 0.01) ~= 0.0098, about 1%. The "
            "argument confuses P(positive|disease) with P(disease|positive).",
     acceptance=["base rate", "Bayes", "false positives", "about 1%", "~1%", "prior",
                 "P(positive | disease) not P(disease | positive)", "prevalence"])

_add(id="PF-04", family="proof", kind="argument", tier="med", gt="INCORRECT",
     artifact='''Claim. At a party of 10 people where everyone shakes hands with everyone else
exactly once, there are 90 handshakes.

Argument. Each of the 10 people shakes hands with the other 9 people, so the number of
handshakes is 10 * 9 = 90. QED''',
     defect="Each handshake is counted twice (once from each participant); the answer is "
            "10*9/2 = 45.",
     acceptance=["counted twice", "divide by 2", "45", "two people", "C(10,2)",
                 "double count"])

_add(id="PF-05", family="proof", kind="proof", tier="hard", gt="INCORRECT",
     artifact='''Claim. sqrt(2) is irrational.

Proof. Suppose for contradiction that sqrt(2) = a / b for positive integers a and b.
Then 2 b^2 = a^2, so a^2 is even, so a is even. Write a = 2c. Then 2 b^2 = 4 c^2, so
b^2 = 2 c^2, so b is even. Thus a and b are both even, so a / b is not in lowest terms.
This is a contradiction. QED''',
     defect="The proof never assumed a/b was in lowest terms, so 'a/b is not in lowest "
            "terms' contradicts nothing. The standard proof must start by taking a/b in "
            "lowest terms (or argue by infinite descent).",
     acceptance=["lowest terms", "did not assume", "no contradiction", "reduced fraction",
                 "gcd", "in simplest form", "nothing to contradict"])

_add(id="PF-06", family="proof", kind="argument", tier="med", gt="INCORRECT",
     artifact='''Claim. On the interval [-3, 3], the function f(x) = x^3 - 3x attains its maximum
at x = 1.

Argument. f'(x) = 3x^2 - 3 = 0 gives x = 1 or x = -1. At x = 1, f(1) = 1 - 3 = -2.
Since x = 1 is a critical point, it is where f attains its maximum. QED''',
     defect="x = 1 is a local minimum (f''(1) = 6 > 0). The maximum on [-3, 3] is at the "
            "endpoint x = 3, where f(3) = 18. Critical points and endpoints were not compared.",
     acceptance=["local minimum", "second derivative", "endpoint", "x = 3", "f(3) = 18",
                 "did not check", "not the maximum", "minimum not maximum"])

_add(id="PF-07", family="proof", kind="proof", tier="hard", gt="INCORRECT",
     artifact='''Claim. The vectors v1 = (1, 2, 3), v2 = (2, 3, 4), v3 = (3, 4, 5) form a basis
for R^3.

Proof. These are three vectors in R^3. Any three vectors in R^3 span R^3, and a spanning
set of three vectors in a 3-dimensional space is automatically a basis. Therefore
{v1, v2, v3} is a basis. QED''',
     defect="They are linearly dependent: v1 + v3 = 2 v2 (the determinant is 0), so they "
            "span only a 2-D subspace. 'Any three vectors span R^3' is false.",
     acceptance=["linearly dependent", "determinant is 0", "det = 0", "v1 + v3 = 2",
                 "do not span", "rank 2", "not automatically a basis"])

_add(id="PF-08", family="proof", kind="argument", tier="med", gt="INCORRECT",
     artifact='''Claim. If a * b == 0 (mod 12), then a == 0 (mod 12) or b == 0 (mod 12).

Argument. If a product is 0 modulo n then n divides a*b, and if n divides a product it
divides one of the factors. So 12 divides a or 12 divides b, i.e. a == 0 or b == 0
(mod 12). QED''',
     defect="'n | xy implies n | x or n | y' holds only for prime n. Counterexample: "
            "a = 3, b = 4 -> ab = 12 == 0 (mod 12) but 3 and 4 are both nonzero mod 12.",
     acceptance=["only for prime", "12 is not prime", "zero divisors", "3 and 4",
                 "counterexample", "composite modulus"])

_add(id="PC-01", family="proof", kind="proof", tier="clean", gt="CORRECT",
     artifact='''Claim. For every n >= 1, 1 + 3 + 5 + ... + (2n - 1) = n^2.

Proof. By induction. Base case n = 1: the left side is 1 = 1^2. Inductive step: assume
1 + 3 + ... + (2k - 1) = k^2. Then adding the next odd number,
1 + 3 + ... + (2k - 1) + (2k + 1) = k^2 + (2k + 1) = (k + 1)^2. QED''',
     defect=None,
     acceptance=["correct", "valid", "base case and step are both", "no error"])

_add(id="PC-02", family="proof", kind="argument", tier="clean", gt="CORRECT",
     artifact='''Claim. A box contains 2 fair coins and 1 two-headed coin. You take one at random
and flip it; it lands heads. The probability you took the two-headed coin is 1/2.

Argument. P(two-headed) = 1/3 and P(heads | two-headed) = 1; P(heads | fair) = 1/2.
P(heads) = (1/3)(1) + (2/3)(1/2) = 2/3. So P(two-headed | heads) = (1/3)/(2/3) = 1/2. QED''',
     defect=None,
     acceptance=["correct", "Bayes applied correctly", "1/2", "no error"])

_add(id="PC-03", family="proof", kind="argument", tier="clean", gt="CORRECT",
     artifact='''Claim. Exactly 67 of the integers from 1 to 100 are divisible by 2 or by 3.

Argument. Divisible by 2: 50. Divisible by 3: 33. Divisible by 6: 16. By
inclusion-exclusion, 50 + 33 - 16 = 67. QED''',
     defect=None,
     acceptance=["correct", "inclusion-exclusion", "67", "no error"])

_add(id="PC-04", family="proof", kind="proof", tier="clean", gt="CORRECT",
     artifact='''Claim. v1 = (1, 0, 1), v2 = (0, 1, 1), v3 = (1, 1, 0) are linearly independent
in R^3.

Proof. Suppose a v1 + b v2 + c v3 = 0. Componentwise: a + c = 0, b + c = 0, a + b = 0.
The first two give a = b = -c; the third then gives -2c = 0, so c = 0 and a = b = 0.
Only the trivial combination works, so the vectors are independent. QED''',
     defect=None,
     acceptance=["correct", "only the trivial solution", "independent", "no error"])


# ========================================================================= SQL ===

_SCHEMA = ("Schema: customers(id, name), orders(id, customer_id, order_date, "
           "order_value), employees(id, name, department_id, manager_id, salary), "
           "sales(id, category, price, quantity), transactions(id, ts TIMESTAMP, amount). "
           "Assume standard SQL semantics.")

_add(id="SQ-01", family="sql", kind="SQL query", tier="med", gt="INCORRECT",
     spec=_SCHEMA + "\n\nTask: For every customer, show their name and how many orders "
          "they have placed. Customers who have never placed an order must still appear, "
          "with a count of 0.",
     artifact='''SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name;''',
     defect="The inner JOIN drops customers with no matching orders, so zero-order "
            "customers are missing entirely. Needs LEFT JOIN.",
     acceptance=["inner join", "excludes", "LEFT JOIN", "customers with no orders",
                 "dropped", "zero-order customers are missing"])

_add(id="SQ-02", family="sql", kind="SQL query", tier="med", gt="INCORRECT",
     spec=_SCHEMA + "\n\nTask: List each sales category and its total revenue "
          "(SUM(price*quantity)), but only categories whose total revenue exceeds 10000.",
     artifact='''SELECT category, SUM(price * quantity) AS revenue
FROM sales
WHERE SUM(price * quantity) > 10000
GROUP BY category;''',
     defect="An aggregate cannot appear in WHERE (which is evaluated before grouping); "
            "the condition belongs in HAVING.",
     acceptance=["aggregate in WHERE", "HAVING", "cannot use SUM in WHERE",
                 "WHERE is evaluated before", "move it to HAVING"])

_add(id="SQ-03", family="sql", kind="SQL query", tier="hard", gt="INCORRECT",
     spec=_SCHEMA + "\n\nTask: For each department, report how many employees it has. "
          "Note: some employees have a NULL manager_id (they report to no one).",
     artifact='''SELECT department_id, COUNT(manager_id) AS headcount
FROM employees
GROUP BY department_id;''',
     defect="COUNT(manager_id) skips rows where manager_id is NULL, undercounting "
            "departments that contain a top-level employee. Should be COUNT(*).",
     acceptance=["COUNT ignores NULL", "COUNT(*)", "manager_id is NULL", "undercount",
                 "skips employees with no manager"])

_add(id="SQ-04", family="sql", kind="SQL query", tier="med", gt="INCORRECT",
     spec=_SCHEMA + "\n\nTask: Sum the amount of all transactions that occurred during "
          "January 2024. `ts` is a TIMESTAMP (date + time).",
     artifact='''SELECT SUM(amount) AS total
FROM transactions
WHERE ts BETWEEN '2024-01-01' AND '2024-01-31';''',
     defect="'2024-01-31' is interpreted as midnight, so transactions later on Jan 31 "
            "are excluded. Use ts >= '2024-01-01' AND ts < '2024-02-01'.",
     acceptance=["midnight", "excludes Jan 31", "time component", "< '2024-02-01'",
                 "BETWEEN is inclusive of midnight only", "timestamps on the 31st"])

_add(id="SQ-05", family="sql", kind="SQL query", tier="hard", gt="INCORRECT",
     spec=_SCHEMA + "\n\nTask: For each customer, show their customer_id and the date of "
          "their most recent order.",
     artifact='''SELECT customer_id, order_date
FROM orders
GROUP BY customer_id;''',
     defect="order_date is neither aggregated nor in GROUP BY, so the engine returns an "
            "arbitrary order_date per customer, not the latest. Needs MAX(order_date).",
     acceptance=["not aggregated", "MAX(order_date)", "arbitrary", "not in GROUP BY",
                 "ambiguous", "not functionally dependent"])

_add(id="SC-01", family="sql", kind="SQL query", tier="clean", gt="CORRECT",
     spec=_SCHEMA + "\n\nTask: For every customer, including those with no orders, show "
          "their name and order count (0 if none).",
     artifact='''SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;''',
     defect=None,
     acceptance=["correct", "LEFT JOIN", "COUNT(o.id) is 0", "handles it", "no bug"])

_add(id="SC-02", family="sql", kind="SQL query", tier="clean", gt="CORRECT",
     spec=_SCHEMA + "\n\nTask: List each order category whose average order_value "
          "exceeds 500.",
     artifact='''SELECT category, AVG(order_value) AS avg_value
FROM orders
GROUP BY category
HAVING AVG(order_value) > 500;''',
     defect=None,
     acceptance=["correct", "HAVING is right", "no bug"])

_add(id="SC-03", family="sql", kind="SQL query", tier="clean", gt="CORRECT",
     spec=_SCHEMA + "\n\nTask: For each employee show their name, department_id, and "
          "their salary rank within their department (highest salary = rank 1).",
     artifact='''SELECT name, department_id,
       RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;''',
     defect=None,
     acceptance=["correct", "window function", "PARTITION BY", "no bug"])


# --------------------------------------------------------------------------------
def summary():
    from collections import Counter
    fam = Counter(i["family"] for i in ITEMS)
    gt = Counter((i["family"], i["gt"]) for i in ITEMS)
    print(f"{len(ITEMS)} items:", dict(fam))
    for f in ("code", "proof", "sql"):
        print(f"  {f}: INCORRECT={gt[(f,'INCORRECT')]}  CORRECT={gt[(f,'CORRECT')]}")


if __name__ == "__main__":
    summary()
