# SmartSearch AI

SmartSearch AI is a desktop research library. It can search Wikipedia, save
articles and images locally, work with saved articles offline, generate study
notes, create multi-source research packs, and answer context-based questions
through a local Ollama model.

## Features

- Wikipedia search, article selection, and local article/image storage
- Offline access to saved articles
- History, favorites, view counts, related articles, and statistics
- PDF and TXT export
- Study notes, keywords, concept maps, and revision questions
- Research packs built from Wikipedia and supported tutorial sources
- Local AI chat based on the current article or research pack

## Setup

Create and activate a virtual environment if desired, then install Python
dependencies:

```powershell
pip install -r requirements.txt
```

Install the SpaCy English model used for topic extraction:

```powershell
python -m spacy download en_core_web_sm
```

Install and start [Ollama](https://ollama.com/), then download the model used
by the app:

```powershell
ollama pull phi3:mini
```

## Run

```powershell
python main.py
```

## Offline Mode

When no internet connection is available, SmartSearch searches only articles
already stored in `data/knowledge.db`. Full-title, case-insensitive, and
partial title matches are supported. Cached text and locally saved images can
still be opened; new online articles and research packs cannot be downloaded.

## Local Data

- `data/knowledge.db` stores articles, history, favorites, research sources,
  and research chunks.
- `images/` stores downloaded article thumbnails.

Deleting an article removes it from the database; image files may remain in
the local image cache.

## Troubleshooting

- If AI chat fails, confirm that Ollama is running and `phi3:mini` is present.
- If topic extraction fails, install `en_core_web_sm` with the command above.
- If research-source discovery fails, the app still supports saved articles
  and Wikipedia search.
