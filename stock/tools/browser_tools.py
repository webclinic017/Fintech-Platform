import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html
from langchain_openai import AzureChatOpenAI

load_dotenv()

default_llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_KEY"),
)


class BrowserTools:

    @tool("Scrape website content")
    def scrape_and_summarize_website(website):
        """Useful to scrape and summarize a website content"""
        # url = f"https://chrome.browserless.io/content?token={os.environ['BROWSERLESS_API_KEY']}"
        url = f"https://chrome.browserless.io/content?token=348255af-73bf-4816-8716-a592e3352fe6"
        payload = json.dumps({"url": website})
        headers = {"cache-control": "no-cache", "content-type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        with open("scraped_data.html", "w") as file:
            file.write(response.text)

        elements = partition_html(text=response.text)
        # print(elements)
        with open("scraped_data.txt", "w") as file:
            file.write("\n".join(map(str, elements)))

        content = "\n\n".join([str(el) for el in elements])

        with open("scraped_content.txt", "w") as file:
            file.write(content)

        content = [content[i : i + 8000] for i in range(0, len(content), 8000)]

        # print(content)
        summaries = []
        for chunk in content:
            agent = Agent(
                role="Principal Researcher",
                goal="Do amazing research and summaries based on the content you are working with",
                backstory="You're a Principal Researcher at a big company and you need to do research about a given topic.",
                allow_delegation=False,
                llm=default_llm,
            )

            task = Task(
                agent=agent,
                description=f"Analyze and summarize the content below, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}",
            )
            summary = task.execute()
            summaries.append(summary)
        print(summaries)
        return "\n\n".join(summaries)
