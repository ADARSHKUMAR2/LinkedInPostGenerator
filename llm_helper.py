from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


if __name__ == "__main__":
    response = llm.invoke("Two most important ingradient in samosa are ")
    print(response.content)




