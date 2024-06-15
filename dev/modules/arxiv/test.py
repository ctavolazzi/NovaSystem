import arxiv

# Create an API client
client = arxiv.Client()

# Perform a search
search = arxiv.Search(
  query=input("Enter the search query: "),
  max_results=10,
  sort_by=arxiv.SortCriterion.SubmittedDate
)

# Fetch results
for result in client.results(search):
  print(result.title)
