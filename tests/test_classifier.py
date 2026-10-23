import unittest

from src.classifier import classify


def evaluate(text):
    return classify({"title": text, "summary": ""})


class ClassifierTests(unittest.TestCase):
    def test_requires_both_topics(self):
        self.assertFalse(evaluate("Large language models for biology")["selected"])
        self.assertFalse(evaluate("Software maintenance practices")["selected"])

    def test_accepts_combined_topics(self):
        result = evaluate("Software maintenance using large language models")
        self.assertTrue(result["selected"])
        self.assertEqual(result["score"], 3)

    def test_aliases_do_not_increase_score(self):
        short = evaluate("Code generation with LLM")
        repeated = evaluate(
            "Code generation with LLM, LLMs and large language models"
        )
        self.assertEqual(short["score"], repeated["score"])
        self.assertEqual(repeated["score"], 3)

    def test_hyphenated_expression(self):
        self.assertTrue(
            evaluate("AI-assisted software development")["selected"]
        )

    def test_unrelated_article(self):
        result = evaluate("Observations of distant galaxies")
        self.assertFalse(result["selected"])
        self.assertEqual(result["score"], 0)

    def test_score_is_capped(self):
        result = evaluate(
            "Software engineering, code generation and program repair "
            "using machine learning, deep learning and reinforcement learning"
        )
        self.assertEqual(result["score"], 5)


if __name__ == "__main__":
    unittest.main()
