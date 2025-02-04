# Q&A Web Application Project

This repository is a project to build a Q&A web application according to EU policies and citizen feedback based on RAG and LLMs model.

## Project Structure

- **SRC**
  - **data**
    - json and csv files scraped from the "Have Your Say" website grouped by different policy topics.
  - **database**
    - code for connecting to the database and storing the data.
  - **download**
    - pdf (attachments) files scraped from the "Have Your Say" website.
  - **frontend**
    - chatbot, frontend code developed with react and deployed on netlify.
  - **nlp**
    - **Chatbot**
      - a demo chatbot based on LangChain and OpenAI, deployed on Streamlit.
    - **DataPreprocessing**
      - data distribution analysis, data cleaning, and embedding with OpenAI embedding.
  - **scraping**
    - code for scraping data and pdf files from the "Have Your Say" website.
    - a pipline for scraping data and storing into database.

## Scraping Logic

### Text Data

1. **Get all initiative IDs and titles grouped by topics**
    - URL: `https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives?topic={topics}&size=10&language=EN`
    - Sample data format:
      ```json
      {
          "id": 12970,
          "status": "ACTIVE",
          "short_title": "Review of the EU school fruit, vegetables and milk scheme"
      }
      ```

2. **Get publication IDs for each initiative**
    - URL: `https://ec.europa.eu/info/law/better-regulation/brpapi/groupInitiatives/{initative_id}`
    - Sample data format:
      ```json
      {
          "id": 12970,
          "info": [
              {
                  "publicationId": 23208625,
                  "title": "Review of the EU school fruit, vegetables and milk scheme",
                  "type": "INIT_PLANNED",
                  "stage": "PLANNING_WORKFLOW",
                  "total_Feedback": 0,
                  "groupId": 12970,
                  "frontEndStage": "INIT_PLANNED",
                  "createdDate": "2021/03/30 12:08:04",
                  "publishedDate": "2021/04/07 13:08:04",
                  "endDate": null
              }
          ]
      }
      ```

3. **Get feedback for each publication ID**
    - URL: `https://ec.europa.eu/info/law/better-regulation/api/allFeedback?publicationId={publication_id}&keywords=&language=EN&page=0&size=10&sort=dateFeedback,DESC`
    - Sample data format:
      ```json
      {
          "id": 14081,
          "publicationId": 32884536,
          "frontEndStage": "ISC_WORKFLOW",
          "feedback": {
              "_embedded": {
                  "feedback": [
                      {
                          "language": "EN",
                          "id": 3466736,
                          "country": "BEL",
                          "surname": "",
                          "status": "PUBLISHED",
                          "firstName": "",
                          "feedback": "Hello, I'm a bit confused by this deleguated regulation...",
                          "historyEventOccurs": false,
                          "login": "",
                          "isDislikedByMe": false,
                          "isMyFeedback": false,
                          "isLikedByMe": false,
                          "referenceInitiative": "Ares(2024)3662375",
                          "attachments": [],
                          "dateFeedback": "2024/05/23 13:33:34",
                          "publication": "ANONYMOUS",
                          "userType": "EU_CITIZEN",
                          "publicationId": 32884536,
                          "publicationStatus": "OPEN"
                      }
                  ]
              }
          }
      }
      ```

### PDF Files

- Download PDF files with the URL: `https://ec.europa.eu/info/law/better-regulation/api/download/{documentId}`
- Download and store the file teporarily, extract the text and merge it into metadata feedback context.

### Web Application

- The web application is deployed at http://askthepublic.eu/.


