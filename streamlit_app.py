import streamlit as st
import joblib
import pandas as pd

MODEL_PATH = 'emotion_model.pkl'
LABEL_ENCODER_PATH = 'label_encoder.pkl'

st.set_page_config(page_title="Emotional State Assessor", layout="centered")

@st.cache_resource
def load_resources():
    try:
        model = joblib.load(MODEL_PATH)
        le = joblib.load(LABEL_ENCODER_PATH)
        return model, le
    except FileNotFoundError:
        st.error(f"Error: Model or LabelEncoder file not found. Make sure '{MODEL_PATH}' and '{LABEL_ENCODER_PATH}' are in the same directory.")
        st.stop()

model, le = load_resources()

MOOD_MAPPING = {
    'Extreme sadness': 0, 'Very sad': 1, 'Somewhat sad': 2,
    'Irritability': 3, 'Fluctuating': 4, 'Neutral': 5,
    'Slightly anxious': 6, 'Somewhat anxious': 7, 'Mildly anxious': 8,
    'Slightly happy': 9, 'Happiness': 10, 'Very happy': 11
}

ANXIOUS_SOCIAL_MAPPING = {
    'Not at all anxious': 0, 'Rarely anxious': 1, 'Slightly anxious': 2,
    'Somewhat anxious': 3, 'Often anxious': 4, 'Very anxious': 5, 'Extremely anxious': 6
}

SLEEP_QUALITY_MAPPING = {
    'Difficulty staying asleep': 0, 'Early morning waking': 1, 'Interrupted': 2,
    'Restless': 3, 'Normal': 4, 'Restful': 5, 'Excellent': 6
}

APPETITE_CHANGE_MAPPING = {
    'Loss of appetite': 0, 'Decreased': 1, 'Fluctuates daily': 2,
    'No significant change': 3, 'Increased cravings': 4, 'Increased': 5
}

LACK_OF_INTEREST_MAPPING = {
    'Never': 0, 'Rarely': 1, 'Occasionally': 2, 'Frequently': 3, 'Always': 4
}

ENJOYABLE_ACTIVITIES_MAPPING = {
    'Never': 0, 'Rarely': 1, 'Once a week': 2, 'A few times a week': 3,
    'Daily': 4, 'Always': 5
}

PHYSICAL_ANXIETY_MAPPING = {
    'No': 0, 'Rarely': 1, 'Yes, occasionally': 2, 'Yes, frequently': 3, 'Always': 4
}

CONCENTRATION_DIFFICULTY_MAPPING = {
    'Never': 0, 'Rarely': 1, 'Occasionally': 2, 'Frequently': 3, 'Constantly': 4
}

questions_data = [
    {'id': 'mood', 'text': '1. How would you describe your mood over the past two weeks?', 'type': 'radio', 'options': list(MOOD_MAPPING.keys())},
    {'id': 'anxious_social_scale', 'text': '2. On a scale of 0-6, how often have you felt anxious in social situations recently?', 'type': 'radio', 'options': list(ANXIOUS_SOCIAL_MAPPING.keys())},
    {'id': 'anxiety_triggers', 'text': '3. Have you experienced any of the following anxiety triggers in the past month?', 'type': 'multiselect', 'options': ['Family issues', 'Work-related stress', 'Financial concerns', 'Health concerns', 'Social situations', 'None of the above']},
    {'id': 'sleep_quality', 'text': '4. How would you rate the quality of your sleep over the past week?', 'type': 'radio', 'options': list(SLEEP_QUALITY_MAPPING.keys())},
    {'id': 'appetite_change', 'text': '5. Have you noticed any significant changes in your appetite?', 'type': 'radio', 'options': list(APPETITE_CHANGE_MAPPING.keys())},
    {'id': 'lack_of_interest', 'text': '6. How often have you felt a lack of interest or pleasure in daily activities?', 'type': 'radio', 'options': list(LACK_OF_INTEREST_MAPPING.keys())},
    {'id': 'enjoyable_activities', 'text': '7. How often do you engage in activities you enjoy or that help you relax?', 'type': 'radio', 'options': list(ENJOYABLE_ACTIVITIES_MAPPING.keys())},
    {'id': 'physical_anxiety_symptoms', 'text': '8. Have you had any physical symptoms of anxiety (e.g., heart palpitations, sweating, shortness of breath)?', 'type': 'radio', 'options': list(PHYSICAL_ANXIETY_MAPPING.keys())},
    {'id': 'concentration_difficulty', 'text': '9. How often do you find it difficult to concentrate on tasks?', 'type': 'radio', 'options': list(CONCENTRATION_DIFFICULTY_MAPPING.keys())},
    {'id': 'coping_strategies', 'text': '10. What coping strategies have you used when feeling stressed or anxious?', 'type': 'multiselect', 'options': ['Physical activity', 'Journaling or writing', 'Meditation/Mindfulness', 'Socializing', 'Seeking professional help', 'No coping strategies']},
]
NUM_QUESTIONS = len(questions_data)

# --- 4. Streamlit UI Layout ---
st.title("💡 Emotional State Assessor")
st.markdown("Answer these 10 questions to get an assessment of your emotional state.")

# Initialize session state
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
    st.session_state.user_responses = {}
    st.session_state.assessment_submitted = False

# Display current question
if not st.session_state.assessment_submitted:
    current_q_data = questions_data[st.session_state.current_question_idx]
    q_id = current_q_data['id']
    q_text = current_q_data['text']
    q_type = current_q_data['type']
    q_options = current_q_data['options']

    st.header(f"Question {st.session_state.current_question_idx + 1} of {NUM_QUESTIONS}")

    with st.form(key=f"question_form_{st.session_state.current_question_idx}"):
        if q_type == 'radio':
            current_value = st.session_state.user_responses.get(q_id, q_options[0])
            default_index = q_options.index(current_value) if current_value in q_options else 0
            user_answer = st.radio(q_text, q_options, key=q_id, index=default_index)
        elif q_type == 'multiselect':
            default_values = st.session_state.user_responses.get(q_id, [])
            user_answer = st.multiselect(q_text, q_options, key=q_id, default=default_values)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.session_state.current_question_idx > 0:
                if st.form_submit_button("Previous"):
                    st.session_state.user_responses[q_id] = user_answer
                    st.session_state.current_question_idx -= 1
                    st.rerun()

        with col2:
            if st.session_state.current_question_idx < NUM_QUESTIONS - 1:
                if st.form_submit_button("Next"):
                    if user_answer is None or (isinstance(user_answer, list) and not user_answer):
                        st.warning("Please select an option to proceed.")
                    else:
                        st.session_state.user_responses[q_id] = user_answer
                        st.session_state.current_question_idx += 1
                        st.rerun()
            else:
                if st.form_submit_button("Assess My Emotion"):
                    if user_answer is None or (isinstance(user_answer, list) and not user_answer):
                        st.warning("Please select an option to proceed.")
                    else:
                        st.session_state.user_responses[q_id] = user_answer
                        st.session_state.assessment_submitted = True
                        st.rerun()

# --- 5. Process User Inputs and Make Prediction ---
if st.session_state.assessment_submitted:
    if len(st.session_state.user_responses) != NUM_QUESTIONS:
        st.error("It looks like some questions were not answered. Please restart the assessment.")
        if st.button("Start New Assessment"):
            st.session_state.current_question_idx = 0
            st.session_state.user_responses = {}
            st.session_state.assessment_submitted = False
            st.rerun()
    else:
        st.markdown("---")
        st.subheader("Processing your answers...")

        # Use model's expected feature names
        expected_feature_columns = model.feature_names_in_.tolist()

        # Initialize processed input
        processed_input = {}
        all_possible_trigger_col_names = [
            'trigger_Family issues',
            'trigger_Work-related stress',
            'trigger_Financial concerns',
            'trigger_Health concerns',
            'trigger_Social situations',
            'trigger_None of the above'
        ]
        for col_name in all_possible_trigger_col_names:
            processed_input[col_name] = 0

        processed_input['has_coping_strategies'] = 0

        user_inputs = st.session_state.user_responses

        processed_input['mood_encoded'] = MOOD_MAPPING.get(user_inputs['mood'], MOOD_MAPPING['Neutral'])
        processed_input['anxious_social_scale_encoded'] = ANXIOUS_SOCIAL_MAPPING.get(user_inputs['anxious_social_scale'], ANXIOUS_SOCIAL_MAPPING['Somewhat anxious'])

        # Handle anxiety triggers with spaces
        for trigger_option_display in user_inputs['anxiety_triggers']:
            col_name = f"trigger_{trigger_option_display}"
            if col_name in all_possible_trigger_col_names:
                processed_input[col_name] = 1

        if 'None of the above' in user_inputs['anxiety_triggers'] and len(user_inputs['anxiety_triggers']) > 1:
            st.warning("You selected 'None of the above' along with other triggers. This might lead to an invalid prediction.")

        processed_input['sleep_quality_encoded'] = SLEEP_QUALITY_MAPPING.get(user_inputs['sleep_quality'], SLEEP_QUALITY_MAPPING['Normal'])
        processed_input['appetite_change_encoded'] = APPETITE_CHANGE_MAPPING.get(user_inputs['appetite_change'], APPETITE_CHANGE_MAPPING['No significant change'])
        processed_input['lack_of_interest_encoded'] = LACK_OF_INTEREST_MAPPING.get(user_inputs['lack_of_interest'], LACK_OF_INTEREST_MAPPING['Occasionally'])
        processed_input['enjoyable_activities_encoded'] = ENJOYABLE_ACTIVITIES_MAPPING.get(user_inputs['enjoyable_activities'], ENJOYABLE_ACTIVITIES_MAPPING['Once a week'])
        processed_input['physical_anxiety_symptoms_encoded'] = PHYSICAL_ANXIETY_MAPPING.get(user_inputs['physical_anxiety_symptoms'], PHYSICAL_ANXIETY_MAPPING['No'])
        processed_input['concentration_difficulty_encoded'] = CONCENTRATION_DIFFICULTY_MAPPING.get(user_inputs['concentration_difficulty'], CONCENTRATION_DIFFICULTY_MAPPING['Occasionally'])
        processed_input['has_coping_strategies'] = 0 if 'No coping strategies' in user_inputs['coping_strategies'] else 1

        input_df = pd.DataFrame([processed_input]).reindex(columns=expected_feature_columns, fill_value=0)

        try:
            prediction_encoded = model.predict(input_df)[0]
            predicted_emotion = le.inverse_transform([prediction_encoded])[0]

            st.markdown("---")
            st.subheader("Your Emotional State Assessment:")

            if predicted_emotion == 'Happy':
                st.success(f"🎉 Based on your answers, you seem to be feeling: **{predicted_emotion}!**")
                st.balloons()
            elif predicted_emotion == 'Normal':
                st.info(f"😊 Based on your answers, you seem to be feeling: **{predicted_emotion}.**")
            elif predicted_emotion == 'Sad':
                st.warning(f"😔 Based on your answers, you seem to be feeling: **{predicted_emotion}.**")
                st.write("If you're feeling down, remember it's okay to seek support. Consider talking to a trusted friend, family member, or a professional.")
            else:
                st.write(f"Your assessed emotional state is: **{predicted_emotion}**")

            st.markdown("---")
            st.caption("Disclaimer: This tool provides a basic assessment based on a machine learning model and is not a substitute for professional medical or psychological advice. If you have concerns about your mental health, please consult a qualified healthcare provider.")
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")

        if st.button("Start New Assessment"):
            st.session_state.current_question_idx = 0
            st.session_state.user_responses = {}
            st.session_state.assessment_submitted = False
            st.rerun()