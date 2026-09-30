# Trivia Vault

A home for the trivia I collect, with a quiz mode that tests me on my own facts.

The facts live in a Google Sheet. The app reads the sheet's published CSV
link, so adding a row to the sheet adds it here within a few minutes.

## Sheet columns
`FACTS`, `SOURCE`, `TAGS`, `SURE?`, `QUESTION`, `ANSWER`, `WRONG 1`, `WRONG 2`, `WRONG 3`

- Only `FACTS` is required. `TAGS` can hold several topics separated by commas.
- A fact needs `QUESTION` and `ANSWER` to appear in the quiz. If some `WRONG`
  columns are empty, the quiz borrows answers from other facts with the same tag.

## Run it locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

No API keys needed: the app only reads the published sheet.
