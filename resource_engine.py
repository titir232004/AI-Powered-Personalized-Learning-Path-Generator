import sys, os
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from RESOURCE_ENGINE.skills_fetcher import fetch_skills
from supabase_store import store_resources
from fetchers.youtube_fetcher import fetch_youtube
from fetchers.github_fetcher import fetch_github
from fetchers.article_fetcher import fetch_articles
from fetchers.practice_fetcher import fetch_practice

def run_engine():
    detected_skills = fetch_skills()
    print("Detected Skills:", detected_skills)

    for skill in detected_skills:
        print(f"\nFetching resources for {skill}")
        resources = []

        # 4 fetchers
        resources.extend(fetch_youtube(skill))
        resources.extend(fetch_github(skill))
        resources.extend(fetch_articles(skill))
        resources.extend(fetch_practice(skill))

        if resources:
            store_resources(resources)
        else:
            print(f"No resources found for {skill}")

if __name__ == "__main__":
    run_engine()