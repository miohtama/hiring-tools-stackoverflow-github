import locale
from collections import Counter, defaultdict
from typing import Set
import statistics


# Parse thousand separators
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def one_point_if_not_empty(x):
    if x.strip():
        return 1
    else:
        return 0


def calculate_checkbox_match_likeness(value):
    """Used to determinate likeness with the tech stack.

    E.g.

        Node.js, PostgreSQL, Redis, MongoDB, Websockets, Docker, Amazon Web Services, Bash/UNIX scripting
        -> likeness=9, score=2

        Node.js, Docker
        -> likeness=1, score=0
    """

    # Google spreadsheet separates values by command
    return len(value.split(","))


def score_by_checkbox_matches(thresholds):
    """Give a different amount of points to the candidate how many checkboxes matches on the form"""

    def _inner(value):
        likeness = calculate_checkbox_match_likeness(value)

        for threshold, score in thresholds:
            if likeness >= threshold:
                return score
        return 0

    return _inner


def score_by_line_count(thresholds):
    """Give a different score based on how many entries there the user inputed e.g. for delivered products"""

    def _inner(value):

        lines = value.split("\n")
        # https://stackoverflow.com/a/3393470/315168
        filled_line_count = len(list(filter(bool, lines)))

        for threshold, score in thresholds:
            if filled_line_count >= threshold:
                return score
        return 0

    return _inner


def score_by_value_threshold(thresholds):
    """Give a different amount of points if the candidates number value exceeds a threshold level"""

    def _inner(value):

        value = locale.atof(value) if value else 0

        for threshold, score in thresholds:
            if value >= threshold:
                return score
        return 0

    return _inner


def score_by_answer(thresholds):
    """Give a different amount of points for different choice answer"""

    def _inner(value):
        for answer, score in thresholds:
            if value == answer:
                return score
        return 0

    return _inner


# Scoring formula for TypeScript full stack candidates
SCORING = {

    # Has homepage
    "Homepage / portfolio / blog / Twitter / link": one_point_if_not_empty,

    # How well the users prior tech stack experience matches with what our company uses - max 2 points
    "Have you used any of the following technologies?": score_by_checkbox_matches([(8, 2), (4, 1)]),

    # Has worked with hacker programming languages
    "Have you worked with any of the following programming languages?": one_point_if_not_empty,

    # Open source contributions means the user can at least use Github/git on a basic level
    "List of open source projects you have contributed in": one_point_if_not_empty,

    # Github repo count is proxy for opensource contributions - max 3 points
    # We prefer this metric because it is very hard to fake
    "Github repo count": score_by_value_threshold([(100, 3), (50, 2), (10, 1)]),

    # StackOverflow rep is a proxy for a good communicator - max 3
    # We prefer this metric because it is very hard to fake
    # "StackOverflow rep": score_by_value_threshold([(2000, 3), (500, 2), (20, 1)]),

    # 1 score if remote team experience
    "Have you worked with remote teams before": score_by_answer([("Yes", 1)]),

    # How many delivered products the user lists - max 2 points
    "Delivered products": score_by_line_count([(4, 2), (1, 1)]),

    # You have some domain insight to the esports world so it gives you one point
    "Do you play competitive multiplayer games on PC, console or mobile?": score_by_answer([("Yes", 1)]),

}


class Scorer:
    """Calculate scores for the."""

    def __init__(self):
        # This is a tag -> scoring question -> list of raw score parameters
        self.summaries = defaultdict(lambda: defaultdict(list))

    def get_tags_for_candidate(self, line):

        tags = set()
        country = "country_" + line["Your country"]

        # tags.add(country)

        experience = float(line["Number of years in software development"])
        if 0 < experience < 4:
            tags.add("experience_0_4")
        elif 4 <= experience < 7:
            tags.add("experience_4_7")
        else:
            tags.add("experience_7+")

        return set(tags)

    def score_candidate(self, line: dict, tags: Set[str]) -> dict:
        """Calculate scores for one candidate and update summaries.

        @return individual scores, total score
        """

        candidate_scores = {}

        for column, func in SCORING.items():
            value = line[column]
            score = func(value)

            candidate_scores[column] = score
            for t in tags:
                self.summaries[t][column].append(score)
            self.summaries["all"][column].append(score)

        total = sum(candidate_scores.values())
        for t in tags:
            self.summaries[t]["total"].append(total)

        return candidate_scores

    def print_scores(self):
        for category, question_data in self.summaries.items():
            for question, values in question_data.items():
                print("Category", category, "question", question, min(values), max(values), statistics.mean(values), statistics.median(values))



