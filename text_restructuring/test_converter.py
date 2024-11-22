from text_restructuring.asl_converter import convert_to_asl


def test_conversion():
    # Test cases
    # List of English test sentences
    test_sentences = [
        "I will call you tomorrow",
        "She wants to eat pizza",
        "The meeting is next week",
        "Are you going to the park?",
        "He needs help with homework",
        "I am studying for the exam",
        "We are visiting our friends today",
        "Where are my keys?",
        "How are you?",
        "Open the door",
        "I don't understand this question",
        "Please sit here",
        "What is your favorite color?",
        "He is working in the kitchen",
        "Where are you going?",
        "Do you like movies?",
        "I am feeling cold",
        "The children are playing outside",
        "Give me the pen",
        "I went to the doctor yesterday",
        "Why are you sad?",
        "She is driving to work",
        "Can you help me find my phone?",
        "The book is on the table",
        "I am going shopping",
        "They are learning sign language",
        "Please close the window",
        "My friend lives in New York",
        "I will be there soon",
        "Are you coming to dinner?",
        "Who is your teacher?"
    ]

    for sentence in test_sentences:
        print(f"\nEnglish: {sentence}")
        asl_text = convert_to_asl(sentence)
        print(f"ASL: {asl_text}")


if __name__ == "__main__":
    test_conversion()
