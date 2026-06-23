## Query the Constitution of Guyana using Natural Language

A simple app to query the constitution of Guyana

### Data Preperation Steps
- pdf of the constitution obtained from https://mola.gov.gy/laws-of-guyana.
- pdf is parsed and chapter_header, page_number and accompanying text collected. Used pdfplumber because needed detailed access to pdf file. A dictionary object created {"section_header": x(str), "page_number": y(int), "text": z(str)}
- use openai text-embedding-3-small model to create text embeddings
- load data into duckdb

### Data Retrieval Steps
- user asks question
- use openai text-embedding-3-small model to create text embeddings for the question
- do a simple cosine similarity search against the duckdb and pull top 5 answers
- send results to LLM to format into human readable text and output

