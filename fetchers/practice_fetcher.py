def fetch_practice(skill):
    return [
        {
            "skill": skill,
            "title": f"{skill} LeetCode Problems",
            "url": f"https://leetcode.com/problemset/all/?topic={skill.replace(' ', '%20')}",
            "platform": "LeetCode",
            "resource_type": "practice",
            "difficulty": "intermediate"
        },
        {
            "skill": skill,
            "title": f"{skill} HackerRank Challenges",
            "url": f"https://www.hackerrank.com/domains/tutorials/10-days-of-{skill.replace(' ', '-')}",
            "platform": "HackerRank",
            "resource_type": "practice",
            "difficulty": "beginner"
        },
        {
            "skill": skill,
            "title": f"{skill} Kaggle Notebooks",
            "url": f"https://www.kaggle.com/search?q={skill.replace(' ', '+')}",
            "platform": "Kaggle",
            "resource_type": "practice",
            "difficulty": "intermediate"
        }
    ]