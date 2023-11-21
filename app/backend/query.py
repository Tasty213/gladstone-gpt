from query.llm_chain_factory import LLMChainFactory


def main():
    vortex_query = LLMChainFactory()

    while True:
        print()
        question = input("Question: ")

        answer, source = vortex_query.ask_question(question)

        print("\n\nSources:\n")
        for document in source:
            print(f"Link: {document.metadata['link']}")
            print(f"Text chunk: {document.page_content[:160]}...\n")
        print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
