from text_restructuring.asl_converter import convert_to_asl

def main():
    while True:
        text = input("Enter text to convert to ASL: ")
        asl_translation = convert_to_asl(text)
        print(asl_translation)

if __name__ == "__main__":
    main()
