import requests

def fetch_github(skill):
    url = f"https://api.github.com/search/repositories?q={skill}+project&sort=stars"
    res = requests.get(url).json()
    resources = []
    for repo in res.get("items", [])[:5]:
        resources.append({
            "skill": skill,
            "title": repo["name"],
            "url": repo["html_url"],
            "platform": "GitHub",
            "resource_type": "project",
            "difficulty": "intermediate"
        })
    return resources