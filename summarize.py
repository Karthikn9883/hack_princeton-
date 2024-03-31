import os
import openai

# Function to read text from a file
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to summarize text using OpenAI's GPT-3.5 Turbo in a conversational manner
def summarize_text(text):
    openai.api_key = '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'  # Ensure to secure your API key properly

    try:
        # Utilize the chat-based model for summarizing
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the provided text, keeping the summary informative and concise."},
                {"role": "user", "content": text}
            ]
        )
        # Extract the summary from the response
        summary = response['choices'][0]['message']['content']
    except Exception as e:
        print(f"An error occurred: {e}")
        summary = "An error occurred while trying to summarize the text."
    return summary

# Main function to read the transcription and get the summary
def main():
    file_path = '/Users/Arshad/Desktop/virtual_machine/transcription.txt'  # Adjust the path to your .txt file as needed
    transcription_text = read_text_file(file_path)
    
    # Summarize the text
    summary = summarize_text(transcription_text)
    
    # Output the summary
    print("Summary:")
    print(summary)

if __name__ == "__main__":
    main()
