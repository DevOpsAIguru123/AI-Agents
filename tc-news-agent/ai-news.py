# ai_news.py

import feedparser
from newspaper import Article
import json
from datetime import datetime
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from groq import Groq
from dotenv import load_dotenv
import resend

# --------------------------
# Load Environment Variables
# --------------------------

# Load variables from .env file
load_dotenv()

# Retrieve Groq API Key from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    logging.error("Groq API key not found. Please set the GROQ_API_KEY in the .env file.")
    exit(1)

# Retrieve Resend API Key from environment variables
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
if not RESEND_API_KEY:
    logging.error("Resend API key not found. Please set the RESEND_API_KEY in the .env file.")
    exit(1)

# --------------------------
# Configuration Parameters
# --------------------------

# RSS feed URL for TechCrunch
RSS_FEED_URL = 'https://techcrunch.com/feed/'

# Maximum number of articles to process daily
MAX_ARTICLES = 5

# Output JSON file to store articles
OUTPUT_FILE = 'techcrunch_articles.json'

# Number of threads for parallel processing
MAX_WORKERS = 5

# --------------------------
# Logging Configuration
# --------------------------

logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_news.log"),
        logging.StreamHandler()
    ]
)

# --------------------------
# Initialize Groq Client
# --------------------------

client = Groq(api_key=GROQ_API_KEY)

# Initialize Resend client
resend.api_key = RESEND_API_KEY

# --------------------------
# Function Definitions
# --------------------------

def fetch_techcrunch_articles(feed_url=RSS_FEED_URL, max_articles=MAX_ARTICLES):
    """
    Fetches the latest articles from TechCrunch RSS feed.

    Args:
        feed_url (str): The RSS feed URL.
        max_articles (int): Maximum number of articles to fetch.

    Returns:
        list: A list of dictionaries containing article details.
    """
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries[:max_articles]:
            articles.append({
                'title': entry.title,
                'url': entry.link,
                'published_at': entry.published
            })
        logging.info(f"Fetched {len(articles)} articles from TechCrunch.")
        return articles
    except Exception as e:
        logging.error(f"Failed to fetch articles from RSS feed: {e}")
        return []

def extract_article_content(url):
    """
    Extracts and returns the full text of the article from the given URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str or None: The extracted article text, or None if extraction fails.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        if not article.text:
            logging.warning(f"No content found for URL: {url}")
            return None
        return article.text
    except Exception as e:
        logging.error(f"Error extracting content from {url}: {e}")
        return None

def summarize_text(content, stream=False):
    """
    Summarizes the given text using Groq Cloud AI's LLaMA model.

    Args:
        content (str): The text to summarize.
        stream (bool): Whether to use streaming responses.

    Returns:
        str or None: The summary text, or None if summarization fails.
    """
    try:
        # Make the API request
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Please provide a concise summary of the following text:\n\n{content}\n\nKeep the summary brief and focused on the key points."
                }
            ],
            model="llama3-8b-8192",  # Changed from llama-3.3-70b-versatile
            stream=stream
        )
        
        if stream:
            summary = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    summary += chunk.choices[0].delta.content
            return summary.strip() if summary else None
        else:
            return completion.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        return None

def load_existing_articles(filename=OUTPUT_FILE):
    """
    Loads existing articles from the JSON file to prevent duplicates.

    Args:
        filename (str): The JSON file name.

    Returns:
        list: A list of existing article dictionaries.
    """
    if not os.path.exists(filename):
        logging.info(f"No existing file found at {filename}. A new one will be created.")
        return []
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get('articles', [])
    except Exception as e:
        logging.error(f"Failed to load existing articles from {filename}: {e}")
        return []

def save_articles(articles, filename=OUTPUT_FILE):
    """
    Saves the articles to a JSON file.

    Args:
        articles (list): A list of article dictionaries.
        filename (str): The output JSON file name.
    """
    data = {
        'date': datetime.now().isoformat(),
        'articles': articles
    }
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Saved {len(articles)} articles to {filename}.")
    except Exception as e:
        logging.error(f"Failed to save articles to {filename}: {e}")

def send_daily_summary_email(articles):
    """
    Sends a single email containing summaries of all articles using Resend.

    Args:
        articles (list): List of article dictionaries containing title, published_at, and summary
    """
    try:
        # Build HTML content for all articles
        articles_html = ""
        for article in articles:
            if article.get('summary'):  # Only include articles with summaries
                articles_html += f"""
                <div style="margin-bottom: 30px;">
                    <h2>{article['title']}</h2>
                    <p><strong>Published:</strong> {article['published_at']}</p>
                    <p><strong>Summary:</strong></p>
                    <p>{article['summary']}</p>
                    <p><a href="{article['url']}">Read full article</a></p>
                </div>
                <hr>
                """

        if not articles_html:
            logging.info("No articles with summaries to send")
            return None

        html_content = f"""
        <h1>TechCrunch Daily News Summary</h1>
        <p>Here are today's top tech news summaries:</p>
        {articles_html}
        """

        params = {
            "from": "AI News <onboarding@resend.dev>",
            "to": ["vinoddevopscloud99@gmail.com"],
            "subject": f"TechCrunch Daily News Summary - {datetime.now().strftime('%Y-%m-%d')}",
            "html": html_content
        }

        response = resend.Emails.send(params)
        logging.info("Daily summary email sent successfully")
        return response
    except Exception as e:
        logging.error(f"Failed to send daily summary email: {e}")
        return None

def process_article(article, existing_urls, force_update=False):
    """
    Processes a single article: checks for duplicates, extracts content, and summarizes it.

    Args:
        article (dict): Article metadata.
        existing_urls (set): Set of URLs already processed.
        force_update (bool): Whether to force reprocessing of existing articles.

    Returns:
        dict or None: Article dictionary with content and summary added, or None if duplicate/extraction failed.
    """
    title = article['title']
    url = article['url']
    published_at = article['published_at']

    if url in existing_urls and not force_update:
        logging.info(f"Article already exists. Skipping: {title}")
        return None

    logging.info(f"Processing Article: {title}")

    # Extract content
    content = extract_article_content(url)
    if not content:
        logging.warning(f"Skipping article due to extraction failure: {title}")
        article['content'] = None
        article['summary'] = None
        return article

    # Summarize content
    summary = summarize_text(content, stream=False)  # Choose stream=True if needed
    if not summary:
        logging.warning(f"Summarization failed for article: {title}")
        article['summary'] = None
    else:
        article['summary'] = summary

    # Add content to the article
    article['content'] = content

    # After successful summarization, send email
    if article.get('summary'):
        logging.info(f"Generated summary for article: {title}")

    return article

def summarize_stored_articles(filename=OUTPUT_FILE):
    """
    Reads and summarizes articles from the stored JSON file that don't have summaries.

    Args:
        filename (str): The JSON file containing the articles.
    """
    try:
        # Load the articles
        with open(filename, 'r') as f:
            data = json.load(f)
            articles = data.get('articles', [])

        updated = False
        for article in articles:
            # Skip if article already has a summary or no content
            if article.get('summary') or not article.get('content'):
                continue

            # Generate summary using Groq
            summary = summarize_text(article['content'])
            if summary:
                article['summary'] = summary
                updated = True
                logging.info(f"Generated summary for article: {article['title']}")

        # Save updated articles if any changes were made
        if updated:
            save_articles(articles)
            logging.info("Saved updated articles with new summaries")

    except Exception as e:
        logging.error(f"Error processing stored articles: {e}")

def main():
    # Step 1: Load existing articles to prevent duplicates
    existing_articles = load_existing_articles()
    existing_urls = {article['url'] for article in existing_articles}
    logging.info(f"Loaded {len(existing_articles)} existing articles.")

    # Step 2: Fetch latest TechCrunch articles
    fetched_articles = fetch_techcrunch_articles()
    if not fetched_articles:
        logging.error("No articles fetched. Exiting.")
        return

    # Step 3: Process articles in parallel to extract content and summarize
    processed_articles = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_article = {
            executor.submit(process_article, article, existing_urls): article for article in fetched_articles
        }
        for future in as_completed(future_to_article):
            result = future.result()
            if result:
                processed_articles.append(result)
                # Display the summary for each processed article
                if result.get('summary'):
                    logging.info(f"\nArticle: {result['title']}")
                    logging.info(f"Summary: {result['summary']}\n")

    if not processed_articles:
        logging.info("No new articles were processed.")
        return

    # Step 4: Combine existing and new articles
    combined_articles = existing_articles + processed_articles
    logging.info(f"Total articles after combining: {len(combined_articles)}.")

    # Step 5: Save combined articles to JSON
    save_articles(combined_articles)
    
    # Step 6: Generate summaries for any articles missing them
    summarize_stored_articles()

    # Step 7: Send single email with all new article summaries
    if processed_articles:
        send_daily_summary_email(processed_articles)

if __name__ == "__main__":
    main()
