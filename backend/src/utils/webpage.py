import asyncio
from typing import Tuple
import tenacity
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from urllib.parse import urlparse
from src.clients.llm import LLMClient


class WebPageUtil:

    @classmethod
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, max=10)
    )
    async def get_content(cls, url: str) -> str:
        loader = WebBaseLoader(url)
        documents = loader.load()
        content = documents[0].page_content
        return content


    @classmethod
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, max=10)
    )
    async def get_metadata(cls, url: str) -> Tuple[str, dict]:
        loader = WebBaseLoader(url)
        html_contents = await loader.fetch_all([url])
        metadata = await cls.parse_metadata(html_contents[0], url)
        documents = loader.load()
        metadata['title'] = documents[0].metadata['title']
        return metadata

    @classmethod
    async def parse2markdown(cls, url: str) -> str:
        content = await cls.get_content(url)
        return await cls.text2markdown(content)

    @classmethod
    async def text2markdown(cls, content: str) -> str:
        prompt = f"""
       Structure the following content into Markdown based on its semantic meaning.

       **Strict requirements:**
       1. The original content must be preserved verbatim. Do not change any words.
       2. The original language must be maintained. Do not translate.

       <content>{content}</content>
       """
        return LLMClient.generate_text(prompt)

    @classmethod
    async def parse_metadata(cls, page_content: str, url: str) -> dict:
        # Parse page content
        soup = BeautifulSoup(page_content, "html.parser")

        # Find all <link> tags
        link_tags = soup.find_all("link", rel=["icon", "shortcut icon"])

        # Get favicon URL
        favicon_url = None
        for link in link_tags:
            href = link.get("href")
            if href:
                # If href is relative path, concatenate to absolute path
                if href.startswith('http'):
                    favicon_url = href
                else:
                    domain = urlparse(url).netloc
                    scheme = urlparse(url).scheme
                    favicon_url = f"{scheme}://{domain}" + href  # Concatenate to absolute URL
                break  # Stop after finding first favicon

        return {
            "favicon_url": favicon_url
        }

async def main():
    url = "https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk"
    content1 = await WebPageUtil.get_content(url)
    print(content1)
    metadata = await WebPageUtil.get_metadata(url)
    print(metadata)
    markdown = await WebPageUtil.text2markdown(content1)
    print(markdown)

if __name__ == "__main__":
    asyncio.run(main())
