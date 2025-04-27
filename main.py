# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from nltk.tokenize import word_tokenize
import re
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk

nltk.download('vader_lexicon')
nltk.download('punkt')

# initial VADER SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def process_voc_data(data):

    cleaned_data = []
    # framework = {"BC", "CC"}
    # Define required fields per type
    required_fields_by_type = {
        "VoC": ["sub_type", "date", "name", "score", "sentiment", "channel", "description"],
        "Analytics": ["sub_type", "date", "name", "score", "sentiment", "channel", "description"],
        "Operation": ["sub_type", "channel", "name", "description"],
        "Insights": ["sub_type", "channel", "name", "description"]
    }

    for record in data:
        # Initialize an issues list to store any detected problems
        record["issues"] = []

        # Ensure required fields are not empty based on type
        required_fields = required_fields_by_type.get(record.get("type"), [])
        for field in required_fields:
            if field not in record or not record[field]:
                record["issues"].append(f"Missing or empty required field: {field}")

        # Detect duplicates (e.g., based on 'date', 'name', 'description')
        if any(
                existing_record["date"] == record["date"] and
                existing_record["name"].lower() == record["name"].lower() and
                existing_record["description"] == record["description"]
                for existing_record in cleaned_data
        ):
            continue  # Skip duplicate records

        # Remove extra spaces from all string fields
        for key in record:
            if isinstance(record[key], str):
                record[key] = record[key].strip()

        description = record["description"]
        #description = re.sub(r"[^a-zA-Z0-9.,!? ]", "", description)  # Remove unwanted special characters
        description = re.sub(r"\s+", " ", description).strip()  # Remove extra spaces
        description = str(TextBlob(description).correct())  # Correct spelling
        record["description"] = description  # Save cleaned description

        # # Handle multiple component categories as dictionary
        # if "component" in record and isinstance(record["component"], dict):
        #     for frame, model in record["component"].items():
        #         if frame not in framework:
        #             record["issues"].append(f"Invalid component model: {frame}")
        #         if not re.match(r"\d+(\.\d+)*", model):
        #             record["issues"].append(f"Invalid component version: {model}")
        # else:
        #     record["issues"].append("Component field must be a dictionary")


        if record["type"] in ["VoC", "Analytics"]:
        # Sentiment analysis using VADER
            score = int(record["score"])
            sentiment_scores = sia.polarity_scores(record["description"])
            print(f"Sentiment scores for '{record['description']}': {sentiment_scores}")

        # Determine the predicted sentiment
            predicted_sentiment = (
                "promoters" if sentiment_scores["compound"] > 0.5 else
                "detractors" if sentiment_scores["compound"] < -0.5 else
                "passives"
            )

        # Check if sentiment matches description
            if record["sentiment"] != predicted_sentiment:
                record["issues"].append(f"Inconsistent sentiment (Expected: {predicted_sentiment})")

            # Handling subtypes like NPS and CES

            if record["sub_type"] in ["CES", "CAST"]:
                    print("ces")
                    # CES scoring range: 0-5
                    if score == 5:
                        if predicted_sentiment != "promoters":
                            record["issues"].append(
                                f"Score mismatch: High score (5) suggests sentiment 'promoters', but found '{predicted_sentiment}'")
                    elif 3 <= score <= 4:
                        if predicted_sentiment != "passives":
                            record["issues"].append(
                                f"Score mismatch: Medium score (3-4) suggests sentiment 'passives', but found '{predicted_sentiment}'")
                    elif 0 <= score <= 2:
                        if predicted_sentiment != "detractors":
                            record["issues"].append(
                                f"Score mismatch: Low score (1-2) suggests sentiment 'detractors', but found '{predicted_sentiment}'")
                    else :
                        record["issues"].append(f"Invalid Score")

            #if record["sub_type"] == "NPS":
            else:
                    # NPS scoring range: 0-10
                    if 9 <= score <= 10 :
                        if predicted_sentiment != "promoters":
                            record["issues"].append(
                                f"Score mismatch: High score (9-10) suggests sentiment 'promoters', but found '{predicted_sentiment}'")
                    elif 7 <= score <= 8:
                        if predicted_sentiment != "passives":
                            record["issues"].append(
                                f"Score mismatch: Medium score (7-8) suggests sentiment 'passives', but found '{predicted_sentiment}'")
                    elif 0 <= score <= 6:
                        if predicted_sentiment != "detractors":
                            record["issues"].append(
                                f"Score mismatch: Low score (0-6) suggests sentiment 'detractors', but found '{predicted_sentiment}'")
                    else :
                        record["issues"].append(f"Invalid Score")
        # Append cleaned record to the results
        cleaned_data.append(record)

    return cleaned_data



# Example Usage
raw_data = [
    {
        "type": "VoC",
        "sub_type": "NPS",
        "date": "12/01/24",
        "name": " John Doe ",
        "score": "10",
        "sentiment": "passives",
        "channel": "Email",
        #"component": {"AC": "2.1.1", "CC": "3.2.1"},
        "description": "Amazing product!!! Highly recommend!! go"
    },
    {
        "type": "VoC",
        "sub_type": "CES",  # Example of sub_type for VoC
        "date": "01/16/24",
        "name": "Jane Smith",
        "score": "12",
        "sentiment": "promoters",
        "channel": "Email",
        #"component": {"BC": "2.1.1", "CC": "3.2.1"},
        "description": "Terrible service. Never coming back!"
    },
    {
        "type": "VoC",
        "sub_type": "CES",
        "date": "01/16/24",
        "name": "Jane Smith",
        "score": "1",
        "sentiment": "promoters",
        "channel": "Email",
        #"component": {"BC": "2.1.1", "CC": "3.2.1"},
        "description": "Excellent service! The staff was friendly and the process was smooth. I will definitely recommend it to others."
    },
{
        "type": "Insights",
        "sub_type": "painpoint",
        "date": "01/16/24",
        "name": "Cumbersome payment and transfer services",
        "vote": "55",
        #"component": {"BC": "2.1.1", "CC": "3.2.1"},
        "description": "Complicated processes in banks' payment and transfer services affect the customer experience."
    },
{
        "type": "Operation",
        "sub_type": "system",
        "date": "01/16/24",
        "name": "System maintenance",
        #"component": {"BC": "2.1.1", "CC": "3.2.1"},
        "description": "Regular maintenance     is performed on critical      systems to ensure their stability    and security."
    },
{
        "type": "Analytics",
        "sub_type": "traffic",
        "date": "01/16/24",
        "name": "traffic detect",
        "score": "3",
        "sentiment": "promoters",
        "channel": "Email",
        #"component": {"BC": "2.1.1", "CC": "3.2.1"},
        "description": "xx"
    }
]

file = "voc_data.csv"
df = pd.read_csv(file, keep_default_na=False).fillna("")
print(df)

processed_data = process_voc_data(df.to_dict(orient="records"))

#processed_data = process_voc_data(raw_data)
for record in processed_data:
      print(record)
