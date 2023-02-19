import requests
from pprint import pprint
import pandas as pd
from dotenv import load_dotenv
import os
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--token', type=str, help='github token')
args = parser.parse_args()

gh_token = None
if args.token:
    gh_token = args.token
else:
    load_dotenv()
    gh_token = os.getenv("GITHUB_TOKEN")


# github graphql url
url = 'https://api.github.com/graphql'
headers = {"Authorization": "Bearer " + gh_token}

os.mkdir("results")

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

with open("queries/contributed_repositories.gql", "r") as f:
    query = f.read()


result = run_query(query)
df = pd.DataFrame(result['data']['viewer']['repositoriesContributedTo']['nodes'])
df = df[df["visibility"] == "PUBLIC"] # lets only look at public repos

df.to_csv('results/repositories_contributed_to.csv', index=False)

with open("queries/merged_pull_requests.gql", "r") as f:
    pr_query = f.read()

pr_result = run_query(pr_query)
pr_df = pd.DataFrame(pr_result['data']['viewer']['pullRequests']['nodes'])
# pr_df.to_csv('merged_pull_requests.csv', index=False)
pr_df["repository"] = pr_df["repository"].apply(lambda x: x["nameWithOwner"])
pr_df["repository_owner"] = pr_df["repository"].apply(lambda x: x.split("/")[0])
pr_df = pr_df[pr_df["repository_owner"] != "osbm"]

# now get the stars for each repo
star_query = """
{
  repository(owner: "%s", name: "%s") {
    stargazers {
      totalCount
    }
  }
}
"""

repos = pr_df["repository"].unique()
star_counts = []
for repo in repos:
    owner, name = repo.split("/")
    query = star_query % (owner, name)
    result = run_query(query)
    star_counts.append((repo, result["data"]["repository"]["stargazers"]["totalCount"]))

stars_of_pr_df = pd.DataFrame(star_counts, columns=["repository", "stars"])
pr_df = pr_df.merge(stars_of_pr_df, on="repository")
pr_df = pr_df.sort_values(by="stars", ascending=False)
pr_df.to_csv('results/merged_pull_requests_with_stars.csv', index=False)
