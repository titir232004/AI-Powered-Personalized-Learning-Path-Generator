def fetch_articles(skill):
    return [
        {
            "skill": skill,
            "title": f"{skill} Official Docs",
            "url": f"https://www.google.com/search?q={skill}+documentation",
            "platform": "Docs",
            "resource_type": "article",
            "difficulty": "beginner"
        },
        {
            "skill": skill,
            "title": f"{skill} freeCodeCamp Tutorials",
            "url": f"https://www.freecodecamp.org/news/search/?query={skill.replace(' ', '+')}",
            "platform": "freeCodeCamp",
            "resource_type": "article",
            "difficulty": "beginner"
        }
    ]