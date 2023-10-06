# [Gladstone-GPT](https://gladstone-gpt-87ede1bc199a.herokuapp.com/)
## The unofficial Liberal Democrat chatbot
With access to all Liberal Democrat policy since 2019 including blog posts from the federal party website, Gladstone can answer most questions about what the Lib Dems would do in government.

Technologies/Tools/Libraries used:
* Scrapy to mine party policy from the website
* ChromaDB to store and index its database of documents
* Langchain to interface with OpenAI's Chat-GPT-3.5-turbo
* React to provide a Web UI
* Google ReCaptcha to prevent bot's spamming it
* AWS dynamo DB for storing user data
* Heroku for hosting
* NewRelic to interpret OpenTelementry tracing and metrics data

### Try it out!
[Try our Gladstone GPT](https://gladstone-gpt-87ede1bc199a.herokuapp.com/)

## How does it work?

1. A user fills out a canvass analysis form which is stored in an AWS database.
2. This data is used to look up the local party information and provided to the chatbot.
3. The user submits a question which is sent to the server alongside the local party info for answer generation.
4. The question is encoded into a collection of numbers that represent the question's contextual meaning, for instance, the word bank in "bank left" and "rob a bank" have different contextual meanings so get assigned different numbers.
5. A database of pre-collected documents that detail the party's policy position is searched using the Maximal Marginal Relevance (MMR) algorithm, returning a selection of documents that most closely match the question asked whilst aiming to ensure the greatest variety.
6. The original question, system prompt and returned documents are submitted to GPT-3.5-turbo for response generation.
7. WebSocket messages are used to stream the response back as it's generated ensuring the user gets a quick response.

## Why did you make this?

1. I wanted to learn more about how AI works.
2. I'm a Liberal Democrat.

## It said the Lib Dems think XYZ and it's wrong

1. Please read the disclaimer at the top of the page when you open it.
2. Raise an issue and I'll see if there are any extra documents that I can add to make it better.

## Authors
[George Sykes](https://github.com/Tasty213)

## License
This project is licensed under the MIT license - see the LICENSE.md file for details

## Acknowledgments
- [Langchain Framework](https://python.langchain.com/en/latest/index.html)
- [OpenAI](https://openai.com/)
- [Chroma DB](https://www.trychroma.com/)
- [Patrick Kalkman](https://github.com/PatrickKalkman) who's [original project](https://github.com/PatrickKalkman/python-docuvortex) I shamelessly forked.


