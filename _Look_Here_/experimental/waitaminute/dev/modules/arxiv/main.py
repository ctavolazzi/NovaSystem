import arxiv
import os
from datetime import datetime
import questionary

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()

def save_paper_metadata(paper, folder):
    access_date = datetime.now().strftime("%Y-%m-%d")
    sanitized_title = sanitize_filename(paper.title[:50])
    filename = f"{sanitized_title}_{access_date}.txt"
    filepath = os.path.join(folder, filename)
    arxiv_url = f"http://arxiv.org/abs/{paper.get_short_id()}"  # Constructing the arXiv entry URL
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f"Title: {paper.title}\n")
        file.write(f"Authors: {', '.join(author.name for author in paper.authors)}\n")
        file.write(f"Abstract: {paper.summary}\n")
        file.write(f"Published: {paper.published}\n")
        file.write(f"Updated: {paper.updated}\n")
        file.write(f"arXiv ID: {paper.get_short_id()}\n")
        file.write(f"Category: {paper.primary_category}\n")
        file.write(f"arXiv URL: {arxiv_url}\n")
        if paper.pdf_url != arxiv_url:
            file.write(f"PDF URL: {paper.pdf_url}\n")
    print(f"Saved: {filepath}")

def main():
    query = questionary.text("Enter your search query:").ask()
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=10,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = list(client.results(search))
    
    if not results:
        print("No results found. Try a different search query.")
        return
    
    choices = [
        {
            'name': f"{paper.title[:75]}... ({paper.published})",
            'value': paper
        }
        for paper in results
    ]
    
    instruction = ("Instructions: Navigate with arrow keys, select/deselect with space, "
                   "and confirm your selection with enter.")
    print(instruction)
    
    selected_papers = questionary.checkbox(
        "Select the papers you want to save:",
        choices=choices
    ).ask()

    if not selected_papers:
        print("No papers selected.")
        return
    
    folder = "arxiv_papers"
    os.makedirs(folder, exist_ok=True)

    for paper in selected_papers:
        save_paper_metadata(paper, folder)
    
    print("All selected papers have been saved.")

if __name__ == "__main__":
    main()
