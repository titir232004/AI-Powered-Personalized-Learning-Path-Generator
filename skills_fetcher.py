# skills_fetcher.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from skills_mapping import SKILLS_MAPPING


def fetch_skills():
    """
    Fetch skills from skills_mapping instead of assessment_results table
    """

    skills = list(SKILLS_MAPPING.keys())

    print("Detected Skills:", skills)

    return skills