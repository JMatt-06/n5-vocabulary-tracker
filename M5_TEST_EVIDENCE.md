# M5 Test Evidence

## Submission checklist

- CI run: push these changes, then open the [CI workflow runs](https://github.com/JMatt-06/n5-vocabulary-tracker/actions/workflows/ci.yml) and submit the URL of the green run. The workflow already runs the complete pytest suite on every push and pull request.
- Repository: [github.com/JMatt-06/n5-vocabulary-tracker](https://github.com/JMatt-06/n5-vocabulary-tracker)
- Prompt-and-diff log: this file, `M5_TEST_EVIDENCE.md`.
- End-to-end screenshot: run `DATABASE_PATH=/tmp/m5-vocabulary.sqlite3 python app.py`, open `http://127.0.0.1:8000`, enter a word such as `食べる`, `たべる`, `to eat`, `verb`, click **Save word**, and capture the page showing **Saved.** and the word in **Your vocabulary**. Attach the PNG or a short screen recording.

For a submission, include the screenshot beside the green Actions run link; the local `127.0.0.1` address is only for capturing the evidence and is not the repository URL.

## Prompt-and-diff log

User request: write an acceptance test for the M5 thin slice, add unit tests
for the underlying logic, generate coverage, inject a user-relevant fault,
show the suite failing, restore the code, and show it passing.

Final implementation diff:

- Added `test_user_can_add_and_list_vocabulary_in_newest_first_order` to
  `tests/test_walking_skeleton.py`.
- Added `tests/test_vocabulary_store.py` with tests for trimming/defaults,
  valid statuses, invalid required fields, invalid statuses, and ordering.
- Added `pytest-cov==6.0.0` to both development requirement files.
- Working application code is restored; there is no final diff in `app.py`.

## Test run output

Command:

```text
/usr/local/py-utils/venvs/pytest/bin/python -m pytest -q tests/test_walking_skeleton.py tests/test_vocabulary_store.py
```

Result:

```text
.........                                                                [100%]
9 passed in 1.08s
```

## Coverage report

Command:

```text
/usr/local/py-utils/venvs/pytest/bin/python -m pytest --cov=app --cov-report=term-missing --cov-report=html:coverage_html --cov-report=xml:coverage.xml
```

Result:

```text
Name     Stmts   Miss  Cover   Missing
--------------------------------------
app.py      74     14    81%   88, 92-93, 98-100, 121-129
--------------------------------------
TOTAL       74     14    81%

9 passed in 1.66s
```

Generated reports: `coverage.xml` and `coverage_html/index.html`.

## Bug injection evidence

### 1. Fault diff

```diff
diff --git a/app.py b/app.py
@@
-                ORDER BY id DESC
+                ORDER BY id ASC
```

This made the list oldest-first, moving a newly saved word away from the top
of the user's vocabulary shelf.

### 2. Suite failing with the fault

```text
.F......F                                                                [100%]
2 failed, 7 passed in 1.61s

FAILED tests/test_walking_skeleton.py::test_user_can_add_and_list_vocabulary_in_newest_first_order
assert [1, 2] == [2, 1]

FAILED tests/test_vocabulary_store.py::test_list_entries_returns_newest_entry_first
assert 1 == 2
```

### 3. Fix restoring green

```diff
diff --git a/app.py b/app.py
 @@
-                ORDER BY id ASC
+                ORDER BY id DESC
```

After restoring the line, the same suite produced:

```text
.........                                                                [100%]
9 passed in 1.08s
```