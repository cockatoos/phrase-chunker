# phrase-chunker
NLP utility to break down article into suitable-size phrases

## Overview

This repository defines a Python script, `json_io.py`,
which processes an article text file and splits it into a collection
of phrases.
The phrases are uploaded onto the Firebase Firestore used by the Cockatoos application.

> The logic for splitting the article into phrases is based on
> rule-based heuristics defined on natural language processing metadata
> (e.g. part-of-speech tagging, word dependencies) obtained from the spaCy 
> language model.

## Getting Started

You must have `python3.x` installed.

```bash
$ cd /path/to/phrase-chunker
$ pip install -U spacy
$ python -m spacy download en_core_web_sm
```

To process an article (for example, `nfl.txt`):

```bash
$ python json_io.py nfl.txt
```
