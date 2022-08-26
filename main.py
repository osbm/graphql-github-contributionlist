import requests
from pprint import pprint
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


# github graphql url
url = 'https://api.github.com/graphql'
headers = {"Authorization": "Bearer " + os.getenv("GITHUB_TOKEN")}

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query = """
{
  viewer {
    repositoriesContributedTo(first: 100, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
      totalCount
      nodes {
        nameWithOwner, visibility
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

result = run_query(query) # Execute the query
pprint(result)
df = pd.DataFrame(result['data']['viewer']['repositoriesContributedTo']['nodes'])

# save to csv withou index
df.to_csv('repositories_contributed_to.csv', index=False)

print(df)

# save df as yml file
