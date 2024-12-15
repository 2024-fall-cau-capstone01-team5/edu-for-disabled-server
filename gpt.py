from openai import OpenAI
import os
from dotenv import load_dotenv
from json_parser import JsonParser

load_dotenv()
def AiReport(scenario_data, answers_data):

    scenario_info = JsonParser(scenario_data)
    answer_sheet = JsonParser(answers_data)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Scenario metadata is entered as JSON input for the first term. The metadata contains the scenario title and the number of questions. After that, the answer sheet is entered. You evaluate the given learning outcomes in detail. Please answer each question in detail in a narrative form. If an incorrect answer is found, please explain the incorrect answer by specifying the scenario and the correct answer. The output is Korean by using 일상생활에서 자연스러운 높임말."
            },
            {
                "role": "user",
                "content": "[scenario info]:\n"+scenario_info.__str__()+"\n[answer sheet]:\n"+answer_sheet.__str__()
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "learning_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "description": "[MAX_LENGTH=100] Did you complete all n questions well without Timeout? Please specify the total number of expected answers from [scenario info] and the actual number of input answers in the [answer sheet].",
                            "type": "string"
                        },
                        "agile": {
                            "description": "[MAX_LENGTH=100] Did it show a fast response speed?",
                            "type": "string"
                        },
                        "accuracy": {
                            "description": "[MAX_LENGTH=100] Did the questioner answer with the intended answer? How many correct answers? If there is a wrong answer, please specify and let me know.",
                            "type": "string"
                        },
                        "context": {
                            "description": "[MAX_LENGTH=100] Did you express yourself correctly in the situation of expressing your emotions? Please specify an answer that you think is awkward to express your emotions in each situation.",
                            "type": "string"
                        },
                        "pronunciation": {
                            "description": "[MAX_LENGTH=100] if there is a \"응답(소리내어 말하기)\", Please specify and let me know an answer that is recognized as mispronunciation or does not fit the situation.",
                            "type": "string"
                        },
                        "review": {
                            "description": "[MAX_LENGTH=300] A general review of this learning and suggestions for future learning directions",
                            "type": "string"
                        },
                        "correct_response_cnt": {
                            "description": "the number of correct answers",
                            "type": "integer"
                        },
                        "timeout_response_cnt":  {
                            "description": "the number of timeout(=시간 초과) or no-reply answers during recorded responses",
                            "type": "integer"
                        },
                        "additionalProperties": False
                    }
                }
            }
        }
    )

    # print(response.choices[0].message.content);
    # Placeholder logic - replace with your AI processing logic
    return response.choices[0].message.content