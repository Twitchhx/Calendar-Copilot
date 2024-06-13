from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re, os

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.tutorDB
tutor_collection = db.tutors

def parse_availability(availability):
    days = {
        "Saturday": [],
        "Sunday": [],
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
    }

    # Define patterns for days and times
    day_patterns = {
        "Saturday": re.compile(r"\bsaturday\b", re.IGNORECASE),
        "Sunday": re.compile(r"\bsunday\b", re.IGNORECASE),
        "Monday": re.compile(r"\bmonday\b", re.IGNORECASE),
        "Tuesday": re.compile(r"\btuesday\b", re.IGNORECASE),
        "Wednesday": re.compile(r"\bwednesday\b", re.IGNORECASE),
        "Thursday": re.compile(r"\bthursday\b", re.IGNORECASE),
        "Friday": re.compile(r"\bfriday\b", re.IGNORECASE),
        "weekends": re.compile(r"\bweekend\b|\bweekends\b", re.IGNORECASE),
        "otherwise": re.compile(r"\botherwise\b", re.IGNORECASE),
    }

    time_pattern = re.compile(r"\b(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight))\b", re.IGNORECASE)
    after_pattern = re.compile(r"\bafter\s+(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight))\b", re.IGNORECASE)
    before_pattern = re.compile(r"\bbefore\s+(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight))\b", re.IGNORECASE)
    between_pattern = re.compile(r"\bbetween\s+(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight)?)\s+and\s+(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight)?)\b", re.IGNORECASE)
    from_to_pattern = re.compile(r"\bfrom\s+(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight))\s+to\s+(\d{1,2}(:\d{2})?\s*(?:pm|am|noon|midnight))\b", re.IGNORECASE)
    noon_pattern = re.compile(r"\bnoon\b", re.IGNORECASE)
    midnight_pattern = re.compile(r"\bmidnight\b", re.IGNORECASE)

    # Use patterns to replace noon and midnight with 12 pm and 12 am
    availability = noon_pattern.sub("12pm", availability)
    availability = midnight_pattern.sub("12am", availability)



    # Split the availability string into clauses
    clauses = availability.split(",")
    for clause in clauses:
        times = time_pattern.findall(clause)
        if times:
            start_time = times[0][0].lower()
            end_time = times[1][0].lower() if len(times) > 1 else None


            # Handle "before" keyword
            before_match = before_pattern.search(clause)
            if before_match:
                start_time = '12pm'
                end_time = before_match.group(1).lower()
            # Handle "after" keyword
            after_match = after_pattern.search(clause)
            if after_match:
                start_time = after_match.group(1).lower()
                end_time = '12am'
            # Handle "between" keyword
            between_match = between_pattern.search(clause)
            if between_match:
                start_time = between_match.group(1).lower()
                end_time = between_match.group(3).lower()
            # Handle "from - to" case
            from_to_match = from_to_pattern.search(clause)
            if from_to_match:
                start_time = from_to_match.group(1).lower()
                end_time = from_to_match.group(3).lower()


            for day, pattern in day_patterns.items():
                if pattern.search(clause):
                    if day == "weekends" or day == "weekend":
                        if not days["Friday"]:
                            days["Friday"].append((start_time, end_time))
                        if not days["Saturday"]:
                            days["Saturday"].append((start_time, end_time))
                    elif day == "otherwise":
                        for weekday in days:
                            if not days[weekday]:  # Only if the day has no previous time slots
                                days[weekday].append((start_time, end_time))
                    else:
                        if not days[day]:
                            days[day].append((start_time, end_time))

    return days


@app.route('/extract-time-slots', methods=['POST'])
def extract_time_slots():
    try:
        data = request.get_json()
        availability = data['availability']

        # Parse the availability into a dictionary
        time_slots = parse_availability(availability)

        return jsonify({'time_slots': time_slots})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/save-availability', methods=['POST'])
def save_availability():
    try:
        data = request.get_json()
        availability = data['availability']
        time_slots = data['time_slots']

        # Save to MongoDB
        tutor_collection.insert_one({'availability': availability, 'time_slots': time_slots})

        return jsonify({'message': 'Availability saved successfully.'})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({'error': 'An error occurred while saving your availability.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
