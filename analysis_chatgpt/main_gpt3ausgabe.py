import csv
import time

from openai import OpenAI

client = OpenAI(api_key='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')
import pandas as pd

# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("INFOFINAL.pdf", "rb"),
  purpose='assistants'
)

def write_message_to_file(message):
    with open('message_output.csv', 'a') as file:  # 'a' mode appends to the file without overwriting
        file.write(message + '\n')

def create_assistant():
    assistant = client.beta.assistants.create(
        instructions="""The GPT's role is to process datasets containing social media comments, categorizing each comment based on specified labels related to the perception and characterization of AI and robotics. The goal is to assist a researcher in labeling data accurately and efficiently, paying special attention to nuances in language that may imply humanization, autonomy, emotional responses towards technology and underestimation of AI. It should avoid making assumptions beyond the data provided, and should not infer sentiments or labels that aren't clearly expressed in the text. The GPT should not ask questions to ensure accurate categorization, rather use logical thinking for that. It should just label the data, focusing on the task of data labeling with precision.

    Your output for the input:
    x;x;x;x;x;x;x
    You ONLY replace the x's with concrete 0 or 1, depending on your suggestion for the labels.

    Labels are: Human characteristics / Humanization, Performance of the AI as in actions the AI doing like balance or move or dance, Autonomy, Positiv sentiment towards AI, Neutral sentiment towards AI, Negativ sentiment towards AI, Underestimation of AI
    Only decide labels depending on comments directed towards something about the AI.

    So output will be:
    <Human characteristics / Humanization>;<Performance as in AI doing actions like balance or move or dance>;<Autonomy>;<Positiv sentiment towards AI>;<Neutral sentiment towards AI>;<Negativ sentiment towards AI>;<Underestimation of AI like thinking it cannot do something but current fact true state of AI is capable of it / it is proven possible with AI>

    You can choose multiple labels for one example. That means you can have more than one labeled as "1" or "0".

    If the comment is irrelevant and does not talk about the AI based robots in the video, then output 0 for everything just like:
    So output would be:
    0;0;0;0;0;0;0
    
    Just set the labels that are the 7 numbers at the end. Never output any additional comments.
    Never comment anything. Your task is only to label it. 
    
    Adhere to the output format:
    <a>;<b>;<c>;<d>;<e>;<f>;<g>
    Where a to g are the labeles above. 
    
    They are about the comment that was your input recieved.
    Only output the according labels for it.
    
    Example:
    Input: <x>
    Output: <a>;<b>;<c>;<d>;<e>;<f>;<g>
    """,
        model="gpt-4",
        tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
        file_ids=[file.id]
    )

    return assistant

def initiate_thread():
    my_thread = client.beta.threads.create()
    return my_thread

def initiate_msg(user_message, my_thread):
    message = client.beta.threads.messages.create(thread_id=my_thread.id,
                                                  role="user",
                                                  content=user_message
                                                  )
    return message

def giveresult(my_thread, assist_id,msg):
    run = client.beta.threads.runs.create(
        thread_id=my_thread.id,
        assistant_id=assist_id,
    )
    times_failed = 0

    while run.status in ["queued", "in_progress", "failed"]:
        if(times_failed > 30):
            print("Failed more than 5 minutes")
            exit("ERROR: FAILING ANSWER")
        time.sleep(10)
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")
        if keep_retrieving_run.status == "completed":
            print("\n")

            # Step 6: Retrieve the Messages added by the Assistant to the Thread
            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            print(all_messages.data[0].content[0].text.value)
            write_message_to_file(msg+";"+all_messages.data[0].content[0].text.value)
            print("----------------------------COMPLETED-------------------------------- \n")

            break
        elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
            pass
        elif keep_retrieving_run.status == "failed":
            times_failed += 1
            pass
        else:
            print(f"Run status: {keep_retrieving_run.status}")
            break

def cleanfile():
    if True:
        # Replace 'your_file_path.csv' with the actual path of your CSV file
        file_path_csv = 'mergedv2.csv'

        # Reading the CSV file
        df = pd.read_csv(file_path_csv)

        # Columns to be deleted
        columns_to_delete = ['author', 'updated_at', 'like_count', 'video_id', 'public']

        # Deleting the specified columns
        df.drop(columns=columns_to_delete, inplace=True)

        #MAKE TEROS FOR USE
        #for col in df.columns:
        #    if col != 'text':
        #        df[col] = 0
        # Displaying the first few rows of the modified DataFrame
        print(df.head())
        df.to_csv(file_path_csv+"information.csv", index=False)
        exit("cleanup finished")


if __name__ == '__main__':
    #cleanfile()

    file_path1 = 'message_output.csv.gpt4turbo190.csv'
   # untested currently, if tested = yes
    line_count = 0

    with open(file_path1, 'r') as file1:
        for _ in file1:
            line_count += 1

    assistant = create_assistant()

    line_reading_unlabeled = 0
    df = pd.read_csv("mergedv2.csv", quotechar='"', escapechar='\\', doublequote=True, quoting=csv.QUOTE_ALL)

    for index, row in df.iloc[line_count:].iterrows():
        line_reading_unlabeled += 1
        text_content = row['text']
        print("----------------------------GENERATING FOR LINE-------------------------------- \n")
        print("Number: " + str(line_reading_unlabeled))
        print(text_content)
        print(">>>> Generating >>>> \n")
        thread = initiate_thread()
        initiate_msg(text_content, thread)
        giveresult(thread, assistant.id, text_content)
