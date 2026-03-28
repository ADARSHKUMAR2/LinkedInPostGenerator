import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import re

def process_posts(raw_file_path, processed_file_path="data/processed_posts.json"):
    enriched_posts = []
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        for post in posts:
            clean_text = re.sub(r'[\ud800-\udfff]', '', post['text'])
            metadata = extract_metadata(clean_text)
            post['text'] = clean_text  # Update the original dict with the clean text just in case
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags = get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags[tag] for tag in current_tags}
        post['tags'] = list(new_tags)

    with open(processed_file_path, 'w', encoding='utf-8') as out_file:
        json.dump(enriched_posts, out_file, indent=4)

    print(f"\n✅ Successfully saved {len(enriched_posts)} posts to {processed_file_path}!")


def extract_metadata(post_text):
    # 1. Use Python to count the lines! It is 100x faster and 100% accurate.
    # We add 1 because a text with no newlines is still 1 line.
    actual_line_count = post_text.count('\n') + post_text.count('\\n') + 1

    # 2. Updated prompt with hyper-specific rules
    template = '''
        You are an expert social media analyzer. Read the following LinkedIn post and extract its language and two topical tags.

        CRITICAL RULES:
        1. Return ONLY a valid JSON object. No preamble, no formatting blocks.
        2. The JSON object MUST have exactly these two keys: "language" and "tags".
        3. "tags": An array of exactly two strings representing the MAIN TOPICS of the post (e.g., "Mental Health", "Job Search", "Toxic Workplace", "LinkedIn Creators"). DO NOT use meta-tags like "Data Cleaning".
        4. "language": Must be exactly "English" or "Hinglish". If the post contains ANY Hindi words written in English letters (e.g., "sapne", "achi baat", "toh"), you MUST classify it as "Hinglish".

        EXAMPLE OUTPUT:
        {{
            "language": "Hinglish",
            "tags": ["Job Search", "Mental Health"]
        }}

        POST TO ANALYZE:  
        {post}
        '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post_text})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)

        # 3. Inject our perfectly calculated Python line count into the LLM's JSON!
        res["line_count"] = actual_line_count

    except OutputParserException:
        raise OutputParserException("Context too big or invalid JSON returned. Unable to parse.")
    print(res)
    return res


def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    # Loop through each post and extract the tags
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])  # Add the tags to the set

    unique_tags_list = ','.join(unique_tags)

    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should be follow title case convention. example: "Motivation", "Job Search"
    3. Output should be a JSON object, No preamble
    3. Output should have mapping of original tag and the unified tag. 
       For example: {{"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation}}

    Here is the list of tags: 
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": str(unique_tags_list)})
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res


if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")