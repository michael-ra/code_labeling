from openai import OpenAI

client = OpenAI(api_key='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')
import pandas as pd

# Function to label the comments using GPT
def gpt_label_comment(comment):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",  # Update the model as needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Read this comment and label it according to the following criteria:\n{comment}\n\n"
                                        "- Label One 'positive': The person thinks positive about robots/AI.\n"
                                        "- Label Two 'negative': The person thinks negative about robots/AI.\n"
                                        "- Label Three 'neutral': The person is neutral about robots/AI.\n"
                                        "- Label Four 'Human characteristics': Assigns human traits to robots.\n"
                                        "- Label Five 'Overestimation of performance': Overestimates robot's performance.\n"
                                        "- Label Six 'Overestimation of autonomy': Overestimates robot's autonomy.\n\n"
                                        "Only choose one label for each of the comments. For every label, only write the number of the label as an output, followed after : and a very short reason."}
        ],
        max_tokens=60,
        temperature=0.1
    )

    # Extracting the label from the last message in the response
    return response.choices[0].message.content.strip()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Load the CSV file
    file_path = 'second_250_comments.csv'
    comments_df = pd.read_csv(file_path, delimiter=';')
    # Add a new column for labels
    comments_df['label'] = comments_df['text'].apply(gpt_label_comment)
    # Save the labeled data
    comments_df.to_csv('labeled_prompt_v5_g_comments.csv', index=False)
