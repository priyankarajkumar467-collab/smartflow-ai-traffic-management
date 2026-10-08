import json
import os


# ============================================================
# SMARTFLOW - 3 USER QUALITATIVE VALIDATION
# ============================================================

OUTPUT_FILE = "results/user_feedback.json"


print("\n========================================")
print("SMARTFLOW USER FEEDBACK")
print("========================================")

print("\nCollecting Review 2 qualitative feedback.")
print("Enter feedback from 3 users.\n")


feedback = []


for user_number in range(1, 4):

    print("----------------------------------------")
    print(f"USER {user_number}")
    print("----------------------------------------")

    name = input("User name/ID: ")

    usefulness = input(
        "How useful is SmartFlow? (1-5): "
    )

    understanding = input(
        "How easy was the system to understand? (1-5): "
    )

    confidence = input(
        "How confident are you in the adaptive signal decision? (1-5): "
    )

    suggestion = input(
        "One suggestion for improvement: "
    )

    feedback.append({
        "user_id": user_number,
        "name_or_id": name,
        "usefulness_rating": int(usefulness),
        "understanding_rating": int(understanding),
        "confidence_rating": int(confidence),
        "suggestion": suggestion
    })


# ------------------------------------------------------------
# Calculate average ratings
# ------------------------------------------------------------

average_usefulness = round(
    sum(user["usefulness_rating"] for user in feedback) / 3,
    2
)

average_understanding = round(
    sum(user["understanding_rating"] for user in feedback) / 3,
    2
)

average_confidence = round(
    sum(user["confidence_rating"] for user in feedback) / 3,
    2
)


# ------------------------------------------------------------
# Create final feedback report
# ------------------------------------------------------------

feedback_results = {

    "project": "AI-Based Adaptive Traffic Signal Management",

    "case_study": "Oppanakara Street, Coimbatore",

    "feedback_type": "3-user qualitative validation",

    "users": feedback,

    "summary": {
        "average_usefulness": average_usefulness,
        "average_understanding": average_understanding,
        "average_confidence": average_confidence
    }
}


# ------------------------------------------------------------
# Save feedback
# ------------------------------------------------------------

os.makedirs("results", exist_ok=True)

with open(OUTPUT_FILE, "w") as file:
    json.dump(
        feedback_results,
        file,
        indent=4
    )


# ------------------------------------------------------------
# Display summary
# ------------------------------------------------------------

print("\n========================================")
print("FEEDBACK SUMMARY")
print("========================================")

print(
    f"Average Usefulness     : "
    f"{average_usefulness}/5"
)

print(
    f"Average Understanding  : "
    f"{average_understanding}/5"
)

print(
    f"Average Confidence     : "
    f"{average_confidence}/5"
)

print("\n========================================")
print("QUALITATIVE VALIDATION COMPLETED")
print("========================================")

print(f"Results saved to: {OUTPUT_FILE}")