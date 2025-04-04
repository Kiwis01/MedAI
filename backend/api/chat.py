import requests
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_KEY")

class MedicalExperts:
    def __init__(self):
        self.experts = {
            "Cardiology": "Deals with conditions related to the heart and blood vessels, such as heart disease, arrhythmias, and high blood pressure.",
            "Neurology": "Focuses on disorders of the brain, spinal cord, and nervous system, including stroke, epilepsy, and migraines.",
            "Dermatology": "Specializes in diseases of the skin, hair, and nails, including acne, eczema, and skin cancer.",
            "Oncology": "Concerned with the diagnosis and treatment of cancers, using therapies like chemotherapy, radiation, and immunotherapy.",
            "General Medicine": "Covers a broad range of common illnesses and conditions, including internal medicine and non-specialized care.",
            "Pediatrics": "Focuses on the health and medical care of infants, children, and adolescents, including developmental and infectious diseases."
        }

    def find_expert(self, text):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        headers = {
            "Content-Type": "application/json"
        }

        expert_info = "\n".join([f"{k}: {v}" for k, v in self.experts.items()])

        data = {
            "generationConfig": {
                "stopSequences": ["Title"],
                "temperature": 1.0,
                "maxOutputTokens": 200,
                "topP": 0.8,
                "topK": 10
            },
            "systemInstruction": {
                "parts": [
                    { "text": "Based on the symptoms listed by the user, suggest the most accurate study of medicine from the dictionary below." },
                    { "text": expert_info },
                    { "text": "Only provide the name of the study of medicine, example: if user presents some sort of brain discomfort return 'Neurology' only." }
                ]
            },
            "contents": [
                {
                    "parts": [
                        { "text": text }
                    ]
                }
            ]
        }

        response = requests.post(url, json=data, headers=headers)
        return response


def chat(text, prediction=None, study_medicine=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "generationConfig": {
            "stopSequences": ["Title"],
            "temperature": 1.0,
            "maxOutputTokens": 200,
            "topP": 0.8,
            "topK": 10
        },
        "systemInstruction": {
            "parts": [
                { "text": "You are collaborating with medical professionals to assist users in understanding their symptoms. Your primary goal is to provide honest, accurate, and reliable information based on the listed symptoms." },
                { "text": "Keep in mind that the output should not exceed 200 tokens. Ensure that responses are concise, relevant, and well-structured." },
                { "text": f"Consider that the tumor prediction from the image is {prediction}. If prediction is 'None' and symptoms indicate possible brain tumor, recommend uploading an image for classification." },
                { "text": f"Give a diagnosis and treatment options based on the symptoms and the study of medicine {study_medicine}." },
                {"text": "Try to provide treatment options or home remedies if possible."},
                { "text": "If the user just wants to have a conversation, there is no need to mention medical terms."}
            ]
        },
        "contents": [
            {
                "parts": [
                    { "text": text }
                ]
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    return response


# ------------------------ CLI ENTRY POINT ------------------------

if __name__ == "__main__":
    expert = MedicalExperts()
    print("Welcome to the medical chatbot! Type your symptoms below or 'q' to quit.\n")

    while True:
        user_text = input("")
        if user_text.lower() == 'q':
            break

        try:
            anomaly = expert.find_expert(user_text).json()
            anomaly_text = anomaly["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            print("Error retrieving expert recommendation. Please try again.")
            continue

        print(f"Suggested Medical Specialty: {anomaly_text}")

        response = chat(user_text, prediction=None, study_medicine=anomaly_text)
        response_data = response.json()

        try:
            response_text = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(response_text)
        except (KeyError, IndexError):
            print("Error generating response from the chatbot.")
