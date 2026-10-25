"""第5天运行：python check_week1.py。无需安装pytest。

这是验收工具，不是统计函数的答案。未完成stats.py前测试失败是预期结果。
"""

import copy
import unittest

from tasks import TASKS
from stats import summarize


class WeekOneChecks(unittest.TestCase):
    def test_01_normal(self):
        result = summarize(copy.deepcopy(TASKS))
        self.assertEqual(result["total"], 6)
        self.assertEqual(result["passed"], 3)
        self.assertEqual(result["failed"], 2)
        self.assertEqual(result["errors"], 1)
        self.assertAlmostEqual(result["success_rate"], 0.5)

    def test_02_empty(self):
        result = summarize([])
        self.assertEqual({k: result[k] for k in ["total", "passed", "failed", "errors"]},
                         {"total": 0, "passed": 0, "failed": 0, "errors": 0})
        self.assertIsNone(result["success_rate"])

    def test_03_missing_status(self):
        with self.assertRaises(ValueError):
            summarize([{"id": "X", "duration_ms": 1}])

    def test_04_unknown_status(self):
        with self.assertRaises(ValueError):
            summarize([{"id": "X", "status": "unknown", "duration_ms": 1}])

    def test_05_negative_duration(self):
        with self.assertRaises(ValueError):
            summarize([{"id": "X", "status": "pass", "duration_ms": -1}])

    def test_06_duplicate_id(self):
        with self.assertRaises(ValueError):
            summarize([TASKS[0].copy(), TASKS[0].copy()])

    def test_07_wrong_duration_type(self):
        for value in ["100", True, None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"id": "X", "status": "pass", "duration_ms": value}])

    def test_08_no_input_mutation(self):
        original = copy.deepcopy(TASKS)
        summarize(TASKS)
        self.assertEqual(TASKS, original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
