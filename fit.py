from flask import Flask, render_template, request, jsonify
import google.generativeai as ai
import sqlite3
import time

app = Flask(__name__)

API_KEY = 'AIzaSyCIgHspeOtytvBf0_ohZZdt43DUqNJBf2Q'
ai.configure(api_key=API_KEY)

model = ai.GenerativeModel("gemini-pro")
chat = model.start_chat()

predefined_responses = {
    "who are you": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "who are you?": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "what is your name": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "what is your name?": "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊",
    "hello": "Hi! How can I assist you today? 👋",
    "bye": "Goodbye! Have a great day! 👋",
    "❤️": "Love is in the air! 😊",
    
    "calculate bmi": "Please provide your weight (kg) and height (cm) to calculate BMI. Formula: BMI = weight / (height * height) in meters.",
    
    "calculate bmr (male)": "BMR Formula for men: BMR = 88.36 + (13.4 × weight in kg) + (4.8 × height in cm) − (5.7 × age in years).",
    
    "calculate bmr (female)": "BMR Formula for women: BMR = 447.6 + (9.2 × weight in kg) + (3.1 × height in cm) − (4.3 × age in years).",
    
    "calculate tdee": "TDEE Formula: TDEE = BMR × Activity Factor. Sedentary: 1.2, Light: 1.375, Moderate: 1.55, Active: 1.725, Intense: 1.9.",
    
    "calculate calorie deficit for weight loss": "Calorie Deficit Formula: Deficit = TDEE - 500 (for ~0.5 kg/week weight loss).",
    
    "calculate calorie surplus for muscle gain": "Calorie Surplus Formula: Surplus = TDEE + 300 to 500 (for lean muscle gain).",
    
    "calculate ideal protein intake": "Protein Intake Formula: 1.6 to 2.2g per kg of body weight for muscle building. Example: 70kg person needs 112g - 154g protein daily.",
    
    "calculate water intake": "Daily Water Intake Formula: Weight (kg) × 0.033 = Liters per day. Example: 70kg × 0.033 = 2.3L daily.",
    
    "calculate fat percentage (YMCA method)": "Body Fat Formula: Males: (1.20 × BMI) + (0.23 × Age) - 16.2. Females: (1.20 × BMI) + (0.23 × Age) - 5.4.",
    
    "calculate one-rep max (1RM)": "One-Rep Max Formula: 1RM = weight × (1 + (0.033 × reps)). Example: 50kg × (1 + 0.033 × 5) = 58.25kg.",
    
    "calculate target heart rate (THR)": "THR Formula: [(220 - age) × % intensity]. Example: 25-year-old at 70% intensity: (220 - 25) × 0.7 = 136.5 BPM.",
    
    "calculate VO2 max": "VO2 Max Formula: 15 × (HRmax / RestingHR). Higher VO2 max means better cardiovascular fitness.",
    
    "calculate waist-to-hip ratio": "WHR Formula: Waist circumference ÷ Hip circumference. Ideal: <0.90 (men), <0.85 (women).",
    
    "calculate lean body mass (LBM)": "LBM Formula: LBM = Total Body Weight - (Body Fat % × Total Body Weight). Example: 80kg, 20% fat → 80 - (0.2 × 80) = 64kg.",
    
    "calculate body fat percentage (US Navy)": "Body Fat % (Men): 86.01 × log10(Waist - Neck) - 70.041 × log10(Height) + 36.76. Women: 163.205 × log10(Waist + Hip - Neck) - 97.684 × log10(Height) - 78.387.",
    
    "calculate calories burned during workout": "Calories Burned Formula: MET × Weight (kg) × Duration (hours). Example: Running at 8 METs, 70kg person for 1 hour = 8 × 70 × 1 = 560 kcal.",
    
    "calculate workout volume": "Workout Volume Formula: Volume = Sets × Reps × Weight. Example: 4 sets × 10 reps × 50kg = 2000kg volume.",
    
    "calculate macronutrient split": "Macronutrient Split Formula: Protein (30-40%), Carbs (40-50%), Fats (20-30%) based on goal (cutting/bulking/maintenance).",
    
    "calculate step-to-calorie conversion": "Steps to Calories Formula: 20 steps ≈ 1 kcal. Example: 10,000 steps ≈ 500 kcal burned.",
    
    "calculate sleep requirement": "Sleep Formula: Ideal = 7-9 hours. Athletes may need 8-10 hours for muscle recovery.",

    "who created you?": "I was created by denQueue.",
    "who developed you?": "I was developed by denQueue.",
    "give me a fitness tip": "Remember to stay hydrated and warm up before your workout! 💪",
    "motivate me": "You're doing amazing! Keep pushing your limits! 💪🔥",
    "who made you": "I was made by denQueue.",
    "calculate bmi": "Please provide your weight (kg) and height (cm) to calculate BMI.",
    #MEDICAL 
    
    "calculate ideal body weight (IBW) (males)": "IBW Formula for Males: 50 + (2.3 × (Height in inches - 60)).",
    
    "calculate ideal body weight (IBW) (females)": "IBW Formula for Females: 45.5 + (2.3 × (Height in inches - 60)).",
    
    "calculate body surface area (BSA)": "BSA Formula: √(Height(cm) × Weight(kg) / 3600). Example: 170cm, 70kg → BSA = 1.84 m².",
    
    "calculate mean arterial pressure (MAP)": "MAP Formula: MAP = (SBP + 2 × DBP) / 3. Normal: 70-100 mmHg.",
    
    "calculate resting metabolic rate (RMR)": "RMR Formula: RMR = BMR × 1.1 (for basic activity level).",
    
    "calculate max oxygen uptake (VO2 max)": "VO2 max Formula: 15 × (HRmax / Resting HR). Higher VO2 max = Better endurance.",
    
    "calculate adjusted body weight (ABW)": "ABW Formula: ABW = IBW + 0.4 × (Actual Weight - IBW).",
    
    "calculate creatinine clearance (CrCl)": "CrCl Formula (Cockcroft-Gault): [(140 - Age) × Weight (kg)] / (72 × Serum Creatinine). For females: multiply by 0.85.",
    
    "calculate LDL cholesterol": "LDL Formula: LDL = Total Cholesterol - HDL - (Triglycerides / 5).",
    
    "calculate cardiac output": "Cardiac Output Formula: CO = Stroke Volume × Heart Rate. Normal: 4-8 L/min.",
    
    "calculate ejection fraction": "Ejection Fraction Formula: (Stroke Volume / End-Diastolic Volume) × 100%. Normal: 55-70%.",
    
    "calculate pregnancy due date (Naegle’s rule)": "Due Date Formula: LMP + 7 days - 3 months + 1 year.",
    
    "calculate respiratory rate ratio": "Normal Respiratory Rate: 12-20 breaths/min for adults.",
    
    "calculate insulin dosage": "Insulin Dosage: Total Daily Dose (TDD) = 0.5 × Weight (kg). 50% basal, 50% bolus.",
    
    "calculate estimated blood volume (EBV)": "EBV Formula: Males: 70mL/kg × Weight (kg). Females: 65mL/kg × Weight (kg).",
    
    "calculate anion gap": "Anion Gap Formula: AG = Na - (Cl + HCO3). Normal: 8-16 mEq/L.",
    
    "calculate corrected sodium": "Corrected Na Formula: Measured Na + [0.016 × (Glucose - 100)].",
    
    "calculate QTc interval": "QTc Formula: QT / √(RR interval in seconds). Normal: <440 ms.",
    
    "calculate GFR (glomerular filtration rate)": "GFR Formula: GFR = [(140 - Age) × Weight (kg)] / (72 × Serum Creatinine). For females, multiply by 0.85.",
    #Sports 
    
    "calculate sprint speed": "Speed Formula: Speed = Distance / Time. Example: 100m in 10s → Speed = 10 m/s.",
    
    "calculate batting average": "Batting Average Formula: Hits / At-Bats.",
    
    "calculate field goal percentage": "FG% Formula: (Field Goals Made / Field Goals Attempted) × 100.",
    
    "calculate pitching ERA (earned run average)": "ERA Formula: (Earned Runs × 9) / Innings Pitched.",
    
    "calculate shooting percentage in basketball": "Shooting % Formula: (Made Shots / Attempted Shots) × 100.",
    
    "calculate soccer shot accuracy": "Shot Accuracy Formula: (Shots on Target / Total Shots) × 100.",
    
    "calculate baseball slugging percentage": "Slugging % Formula: (Total Bases / At-Bats).",
    
    "calculate swimming lap speed": "Lap Speed Formula: Distance / Time per Lap.",
    
    "calculate force in weightlifting": "Force Formula: Mass × Acceleration (F = ma).",
    
    "calculate kinetic energy of a moving ball": "Kinetic Energy Formula: KE = 0.5 × Mass × Velocity².",
    
    "calculate reaction time": "Reaction Time Formula: √(2 × Distance / Acceleration due to Gravity).",
    
    "calculate vertical jump height": "Jump Height Formula: H = (Velocity²) / (2 × Gravity).",
    
    "calculate cycling power output": "Power Formula: Force × Velocity. Example: 300N × 5m/s = 1500W.",
    
    "calculate rowing stroke rate": "Stroke Rate Formula: Strokes per minute.",
    
    "calculate marathons pace": "Pace Formula: Time / Distance. Example: 3h 30min for 42.195km → 5 min/km.",
    
    "calculate VO2 max for runners": "VO2 max Formula (Cooper Test): (Distance run in 12 min - 504) / 45.",
    
    "calculate agility test score": "Agility Score Formula: (Time Taken to Complete Test) / (Number of Direction Changes).",
    
    "calculate stamina endurance time": "Endurance Time Formula: Energy Available / Energy Used per Unit Time.",
    #Credits 
    "who developed you?": "I was developed by denQueue.",
    "who created you?": "I was created by the innovative minds at denQueue.",
    "who built this AI?": "This AI was built by denQueue, a team dedicated to revolutionizing fitness technology.",
    "who is behind this AI?": "denQueue is the team behind Fitness Tech-AI, bringing AI-powered fitness solutions to life.",
    "who owns you?": "I am a product of denQueue, designed to enhance your fitness journey.",
    "who made this app?": "denQueue developed this app with a passion for fitness and AI-driven coaching.",
    "what is denQueue?": "denQueue is a tech-driven company focused on AI innovations in fitness and sports training.",
    "tell me about denQueue": "denQueue is a pioneering team committed to merging AI and fitness to create next-generation training solutions.",
    "is this app AI-powered?": "Yes! Fitness Tech-AI, developed by denQueue, leverages AI to provide smart fitness insights.",
    "who manages this app?": "This app is managed and continuously improved by the experts at denQueue.",
    "what does denQueue specialize in?": "denQueue specializes in AI-powered fitness coaching, real-time form correction, and performance enhancement tools.",
    "is denQueue a fitness company?": "denQueue is a tech-driven company focused on AI solutions for fitness and sports training.",
    "how does denQueue use AI?": "denQueue harnesses AI for real-time posture monitoring, personalized coaching, and injury prevention.",
    "does denQueue provide personal training?": "Through AI-driven insights, denQueue offers virtual personal training and performance analysis.",
    "who are the developers of Fitness Tech-AI?": "Fitness Tech-AI was developed by denQueue, an expert team passionate about AI and fitness.",
    "what makes denQueue unique?": "denQueue combines advanced AI with fitness expertise to create smart training solutions.",
    "how does denQueue improve workouts?": "denQueue's AI-powered technology enhances workouts through real-time monitoring and personalized feedback.",
    "why was Fitness Tech-AI created?": "Fitness Tech-AI was created by denQueue to provide expert-level coaching to everyone using AI.",
    "what is the vision of denQueue?": "denQueue aims to revolutionize fitness training with AI, making expert coaching accessible to all.",
    
    "what is the purpose of Fitness Tech-AI?": "Fitness Tech-AI was created to enhance workouts, prevent injuries, and provide expert-level training using AI.",
    "why was this AI developed?": "Fitness Tech-AI was developed by denQueue to bring smart, AI-powered fitness assistance to everyone.",
    "what makes Fitness Tech-AI unique?": "Fitness Tech-AI offers real-time posture correction, personalized training, and AI-driven performance analysis.",
    "how does Fitness Tech-AI help users?": "This AI provides instant feedback on your form, tracks your progress, and optimizes your workouts.",
    "why should I use Fitness Tech-AI?": "Fitness Tech-AI ensures safer workouts, reduces injury risk, and maximizes your fitness results with AI insights.",
    "who benefits from this AI?": "Fitness enthusiasts, athletes, beginners, and professionals can all benefit from Fitness Tech-AI’s smart coaching.",
    "how does AI improve workouts?": "AI analyzes movement, detects form errors, and provides real-time feedback for effective training.",
    "does this AI work for beginners?": "Absolutely! Fitness Tech-AI adapts to all levels, from beginners to advanced athletes.",
    "is this AI useful for professional athletes?": "Yes! Fitness Tech-AI provides detailed performance analytics to help athletes improve their game.",
    "can this AI track my fitness progress?": "Yes! It continuously tracks your performance, helping you set and achieve fitness goals.",
    "does this AI prevent injuries?": "Yes! By monitoring form and providing corrections, Fitness Tech-AI helps reduce injury risks.",
    "can this AI be used in gyms?": "Yes! Gyms can integrate Fitness Tech-AI to offer smart training assistance and injury prevention.",
    "is this AI suitable for home workouts?": "Yes! Whether at home or the gym, Fitness Tech-AI provides virtual coaching anywhere.",
    "does Fitness Tech-AI support weight training?": "Yes! It monitors your posture and form during weightlifting to ensure safe training.",
    "how does this AI support cardio training?": "It tracks running posture, heart rate zones, and endurance levels for optimized cardio workouts.",
    "does this AI assist with yoga?": "Yes! Fitness Tech-AI helps with posture correction and breathing guidance for better yoga practice.",
    "is this AI useful for rehabilitation?": "Yes! It helps in post-injury recovery by ensuring safe movements and proper form.",
    "how does this AI help bodybuilders?": "It monitors muscle activation, rep quality, and form for effective muscle growth.",
    "is this AI useful for weight loss?": "Yes! It tracks calories burned, optimizes workout routines, and provides motivation for weight loss goals.",
    "can I get a personalized workout plan?": "Yes! Fitness Tech-AI generates customized workout plans based on your fitness level and goals.",
    "does this AI provide nutrition advice?": "Yes! It gives basic nutrition insights to support your fitness journey.",
    "how does this AI help runners?": "It monitors stride length, cadence, and running posture to improve performance and prevent injuries.",
    "can this AI work for sports training?": "Yes! Fitness Tech-AI helps with agility, endurance, and skill-specific training in various sports.",
    "does this AI track heart rate?": "If connected to a heart rate monitor, it can analyze your heart rate data for optimal performance.",
    "how does this AI support HIIT workouts?": "It tracks intensity, form, and recovery times to optimize HIIT training.",
    "is this AI useful for strength training?": "Yes! It analyzes movement patterns to ensure correct form during strength training exercises.",
    "can this AI work with wearable devices?": "Yes! It can integrate with wearables for more accurate tracking and insights.",
    "does this AI support calisthenics?": "Yes! It helps track bodyweight exercises and ensures proper execution.",
    "is Fitness Tech-AI good for seniors?": "Yes! It provides safe and effective training guidance for older adults.",
    "can this AI help with flexibility training?": "Yes! It suggests stretching routines and monitors flexibility progress.",
    "how does this AI support rehabilitation?": "It helps in tracking recovery exercises and ensures correct movement execution.",
    "does this AI analyze workout intensity?": "Yes! It evaluates workout intensity and suggests improvements.",
    "can this AI assist personal trainers?": "Yes! Trainers can use Fitness Tech-AI to enhance coaching and monitor client progress.",
    "is Fitness Tech-AI useful for teams?": "Yes! Sports teams can use it for performance analysis and injury prevention.",
    "does this AI work for martial arts training?": "Yes! It helps with movement analysis and form correction for combat sports.",
    "can this AI be used for CrossFit training?": "Yes! It tracks performance and ensures safe execution of high-intensity movements.",
    "does this AI support functional fitness?": "Yes! It helps improve balance, coordination, and movement efficiency.",
    "what AI technology powers this app?": "Fitness Tech-AI uses advanced computer vision and machine learning for real-time analysis.",
    "how is AI used in fitness tracking?": "AI processes movement data to detect posture, technique, and workout effectiveness.",
    "does Fitness Tech-AI use deep learning?": "Yes! It applies deep learning models to analyze motion and provide accurate feedback.",
    "who maintains Fitness Tech-AI?": "The expert team at denQueue continuously updates and improves the AI for better performance.",
    "is Fitness Tech-AI a virtual trainer?": "Yes! It acts as a virtual personal trainer, guiding you through exercises and improving your technique.",
    "does this AI integrate with fitness apps?": "Yes! It can sync with popular fitness apps for better tracking and analysis.",
    "is Fitness Tech-AI available worldwide?": "Yes! Fitness Tech-AI can be accessed and used globally for fitness improvement.",
    "is this AI free to use?": "Fitness Tech-AI offers both free and premium features for users.",
    "how does AI help in sports performance?": "It tracks movement efficiency, provides corrective feedback, and optimizes training techniques.",
    "does AI help in preventing sports injuries?": "Yes! AI detects movement imbalances and suggests corrections to prevent injuries.",
    "who leads the Fitness Tech-AI team?": "denQueue’s team of AI engineers and fitness experts lead the development of Fitness Tech-AI.",
    "who are the developers behind this app?": "The skilled professionals at denQueue developed this AI to transform fitness training.",
    "what is the mission of denQueue?": "denQueue aims to revolutionize fitness with AI-powered coaching and injury prevention.",
    "how does denQueue innovate in fitness?": "denQueue integrates AI with fitness science to create next-level training solutions.",
    "what impact does Fitness Tech-AI have?": "Fitness Tech-AI helps users train smarter, reduce injuries, and improve overall performance.",
    "can AI replace personal trainers?": "AI enhances personal training but works best alongside human coaches for optimal results.",
    "what future developments are planned?": "denQueue is continuously working on adding more sports-specific AI features.",
    "is AI the future of fitness?": "AI is transforming fitness by making expert training accessible and improving performance tracking.",
    "what role does AI play in rehabilitation?": "AI helps track recovery progress and ensures safe rehabilitation exercises.",
    "how does AI support mental fitness?": "Fitness Tech-AI provides motivation, stress-reducing workouts, and guided relaxation exercises.",
    "how can AI improve my motivation?": "AI tracks your progress, sets achievable goals, and provides instant encouragement.",
    "what industries use AI in fitness?": "Gyms, sports teams, personal trainers, and healthcare professionals use AI-powered fitness technology.",
    "how does AI enhance gym workouts?": "It provides form correction, progress tracking, and workout optimization for gym users.",
    "does AI support remote coaching?": "Yes! Fitness Tech-AI allows remote training by providing AI-driven feedback from anywhere.",


    #OTHER MATHEMATICAL STUFFS
    
    "calculate hydration needs": "Hydration Formula: Weight (kg) × 0.033 = Liters per day.",
    
    "calculate basal temperature increase during fever": "Normal body temperature: 36.1 - 37.2°C. Fever: >38°C.",
    
    "calculate optimal stride length for running": "Stride Length Formula: Height × 0.41 for men, Height × 0.38 for women.",
    
    "calculate maximum power output in sprinting": "Power Output = (Force × Distance) / Time.",
    
    "calculate tennis ball impact force": "Impact Force Formula: (Mass × Change in Velocity) / Time of Impact.",
    
    "calculate body hydration deficit": "Hydration Deficit Formula: (Weight Loss in kg) × 1.5 = Liters needed.",
    
    "calculate maximum lifting capacity": "Strength Formula: Force = Mass × Acceleration.",
    
    "calculate fatigue rate": "Fatigue Rate = Power Output / Time until Exhaustion.",
    
    "calculate heart rate recovery": "HR Recovery: HRmax - HR after 1 min of rest.",
    
    "calculate sweat rate during exercise": "Sweat Rate Formula: (Pre-exercise Weight - Post-exercise Weight + Fluid Intake) / Exercise Time.",


  "who developed you?": "I was developed by DenQueue.",
    "who made you?": "I was made by DenQueue.",
    "what is Fitness Tech-AI?": "Fitness Tech-AI is an AI-powered fitness assistant by DenQueue, offering real-time workout guidance and personalized training plans.",
    "what do you do?": "I provide AI-driven fitness guidance, workout tracking, injury prevention tips, and performance analysis.",
    "give me a fitness tip": "Remember to stay hydrated and warm up before your workout! 💪",
    "motivate me": "You're doing amazing! Keep pushing your limits! 💪🔥",
    "calculate bmi": "Please provide your weight (kg) and height (cm) to calculate BMI.",
    "how to stay consistent with workouts?": "Set a realistic schedule, track your progress, and make fitness a habit! 💯",
    "what is the best time to exercise?": "It depends on your goals! Mornings boost metabolism, while evenings improve performance.",
    "how much water should I drink daily?": "Drink at least 2-3 liters of water daily to stay hydrated! 🚰",
    "how to lose weight fast?": "Focus on a calorie deficit, strength training, and consistent cardio workouts.",
    "how to gain muscle?": "Lift weights, consume enough protein, and get sufficient rest for muscle growth.",
    "should I do cardio every day?": "It depends on your goal! For fat loss, 3-5 times a week is ideal.",
    "how to prevent injuries while working out?": "Always warm up, maintain proper form, and avoid overtraining.",
    "how important is sleep for fitness?": "Very important! Aim for 7-9 hours of sleep for muscle recovery and performance.",
    "what is HIIT?": "HIIT (High-Intensity Interval Training) is a fast-paced workout that burns fat efficiently! 🔥",
    "how often should I work out?": "Train at least 3-5 times per week for optimal results.",
    "what foods help in muscle recovery?": "Protein-rich foods like eggs, chicken, fish, and nuts help muscle recovery. 🥩",
    "how long should a workout session be?": "30-60 minutes is sufficient, depending on the intensity and workout type.",
    "is stretching necessary?": "Yes! Stretching improves flexibility, prevents injuries, and enhances recovery. 🏋️",
    "what is the best post-workout meal?": "A meal with protein and carbs like grilled chicken with rice is ideal.",
    "should I work out if I'm sore?": "Light movement and stretching can help reduce soreness, but avoid overexertion.",
    "how to boost stamina?": "Cardio exercises like running, cycling, and jump rope improve stamina. 🚴",
    "how to increase strength?": "Progressive overload in weight training helps build strength over time.",
    "what is a balanced diet?": "A diet with protein, carbs, healthy fats, vitamins, and minerals.",
    "can AI replace a personal trainer?": "AI provides real-time feedback and personalized guidance, but human trainers add motivation and customization.",
    "does Fitness Tech-AI track progress?": "Yes! I can help track your workouts and suggest improvements over time.",
    "how does AI help in fitness?": "AI provides real-time posture correction, injury prevention tips, and personalized training plans.",
    "why is rest important in fitness?": "Rest allows muscle recovery, prevents burnout, and improves overall performance.",
    "what are good pre-workout snacks?": "Bananas, oats, and peanut butter give a good energy boost!",
    "what is the difference between bulking and cutting?": "Bulking focuses on muscle gain, while cutting focuses on fat loss.",
    "how can I track calories?": "Use calorie-tracking apps or consult AI-based nutrition tracking tools.",
    "how to train for endurance?": "Increase workout duration gradually and focus on stamina-building exercises.",
    "how to train for strength?": "Lift heavier weights with lower reps and focus on compound exercises.",
    "does lifting weights make you bulky?": "No, it depends on diet and training. Strength training helps tone muscles.",
    "can I work out on an empty stomach?": "Fasted workouts can burn fat, but it’s best to have a light meal before intense training.",
    "how do I improve flexibility?": "Regular stretching, yoga, and mobility drills help improve flexibility.",
    "how does Fitness Tech-AI provide workout plans?": "It analyzes your fitness level and goals to create a personalized plan.",
    "what is the importance of core strength?": "A strong core improves stability, posture, and overall performance.",
    "does Fitness Tech-AI support sports training?": "Yes! It provides real-time feedback for sports-specific training.",
    "how to stay injury-free?": "Warm up properly, use correct form, and allow adequate recovery.",
    "how to fix bad posture?": "Practice exercises that strengthen your back and core muscles.",
    "what is overtraining?": "Overtraining occurs when you don’t allow your body enough time to recover, leading to fatigue.",
    "should I take protein supplements?": "Whole foods are best, but protein supplements can help meet protein requirements.",
    "how do I stay motivated?": "Set small goals, track progress, and remind yourself why you started!",
    "how does real-time posture correction work?": "AI analyzes your form during workouts and provides instant feedback.",
    "what is the best way to burn belly fat?": "A mix of cardio, strength training, and a healthy diet works best.",
    "how to improve running speed?": "Sprint drills, strength training, and endurance workouts help improve speed.",
    "how to fix muscle imbalances?": "Focus on unilateral exercises and strengthen weaker muscles individually.",
    "why is warming up important?": "It prepares your body for exercise and reduces the risk of injuries.",
    "what is the best way to track fitness progress?": "Monitor workout performance, take progress photos, and track strength gains.",
    "should I eat before or after a workout?": "Both! A pre-workout snack gives energy, and post-workout meals aid recovery.",
    "how to make workouts more effective?": "Increase intensity, focus on form, and stay consistent!",
    "how do I know if I'm training too hard?": "Persistent fatigue, soreness, and lack of motivation are signs of overtraining.",
    "how does AI help in injury prevention?": "AI detects incorrect movements and provides instant posture correction feedback."

}

def get_db_connection():
    conn = sqlite3.connect('interactions.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            response_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

create_table()

def handle_message(message):
    normalized_message = message.strip().lower()
    if normalized_message in predefined_responses:
        return predefined_responses[normalized_message]
    return None

@app.route('/')
def home():
    return render_template('good.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_message = request.form['message']
    predefined_response = handle_message(user_message)
    if predefined_response:
        response_text = predefined_response
    elif user_message.lower().startswith('bmi '):
        try:
            weight, height = map(float, user_message[4:].split())
            bmi = weight / (height / 100) ** 2
            response_text = f"Your BMI is {bmi:.2f}. A healthy BMI is typically between 18.5 and 24.9."
        except ValueError:
            response_text = "Please provide your weight (kg) and height (cm) separated by a space. Example: 'BMI 70 175'"
    else:
        response_text = send_message_with_retry(chat, user_message)

    response_chunks = [response_text[i:i+500] for i in range(0, len(response_text), 500)]
    save_interaction(user_message, response_text)
    return jsonify(response=response_text)

def save_interaction(user_message, response_text):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO interactions (user_message, response_text)
        VALUES (?, ?)
    ''', (user_message, response_text))
    conn.commit()
    conn.close()

def send_message_with_retry(chat, user_message, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = chat.send_message(user_message)
            if any(word in response.text.lower() for word in ["gemini", "google"]):
                response.text = "I am Fitness Tech-AI, your personal fitness assistant, developed by denQueue 😊"
            return response.text
        except ai.errors.ApiError as api_err:
            app.logger.error(f"API Error on attempt {attempt + 1}: {api_err}")
            time.sleep(delay)
        except Exception as e:
            app.logger.error(f"General Error on attempt {attempt + 1}: {e}")
            time.sleep(delay)
    return "Sorry, something went wrong. Please try again."

@app.route('/chat-history')
def chat_history():
    conn = get_db_connection()
    interactions = conn.execute('SELECT id, user_message, timestamp FROM interactions ORDER BY timestamp DESC').fetchall()
    conn.close()
    history = [{"id": row["id"], "title": row["user_message"][:30], "timestamp": row["timestamp"]} for row in interactions]
    return jsonify(history=history)

@app.route('/chat/<int:chat_id>')
def get_chat(chat_id):
    conn = get_db_connection()
    interaction = conn.execute('SELECT user_message, response_text FROM interactions WHERE id = ?', (chat_id,)).fetchall()
    conn.close()
    messages = [{"text": row["user_message"], "sender": "user"} for row in interaction]
    messages += [{"text": row["response_text"], "sender": "bot"} for row in interaction]
    return jsonify(messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
