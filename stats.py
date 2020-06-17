"""Calculate different stats over all candidates.

Unlike other scripts, this works offline on exported CSV file
(I run out of Google Spreadsheet API quote).
"""

import scorecard
import csv
from pprint import pprint

scorer = scorecard.Scorer()
with open('candidates.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")
    for idx, line in enumerate(reader, start=1):

        print("Parsing line", idx)

        tags = scorer.get_tags_for_candidate(line)
        try:
            candidate_scores = scorer.score_candidate(line, tags)
        except Exception as e:
            print("Failed on data")
            pprint(line)
            raise e

        name = line["Your name"]
        print("Candidate", idx, name, "scores", sum(candidate_scores.values()))

scorer.print_scores()