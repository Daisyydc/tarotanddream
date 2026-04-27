---
language: 
- en
pretty_name: "Tarot cards readings"
tags:
- ChatGPT
- Tarot
license: mit
task_categories:
- question-answering
- text-generation
---

This is a dataset of 5,770 high quality tarot cards readings produced by ChatGPT based on 3 randomly drawn cards. It can be used to train smaller models for use in a tarot application.

The prompt used to produce these readings was:

> Give me a one paragraph tarot reading if I pull the cards CARD1, CARD2 and CARD3.\n\nReading:\n

The CSV dataset contains the following columns: *Card 1*, *Card 2*, *Card 3*, *Reading*

There are also 2 Python scripts included:

* make_dataset.py: This file was used to create the dataset using the ChatGPT API.
* train_dataset.py: This file can be used as an example on how to train a base model using the dataset.