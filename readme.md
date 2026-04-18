# 🎯 Adaptive Career Mentor AI

<div align="center">
**An AI-powered career guidance chatbot that provides personalized career recommendations, skill roadmaps, and location-based academic suggestions — built for students seeking structured and personalized career guidance.**

🌐 **Live Demo:** https://adaptive-career-mentor-ai.onrender.com
</div>

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Installation](#️-installation)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Survey & Validation](#-survey--validation)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)

---

## 🧠 About the Project

**Adaptive Career Mentor AI** is an intelligent web-based chatbot designed to help students and young professionals make informed career decisions. The system analyzes user interests, skills, and aptitude test results to generate personalized career recommendations, structured learning roadmaps, and location-specific academic suggestions.

> Traditional career counseling is expensive, inaccessible, and generic. This project solves that — making expert-level guidance available to everyone, anytime.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Chatbot Interface** | Conversational flow that collects user data naturally |
| 🔐 **User Authentication** | Secure login and registration system |
| 📝 **Aptitude Testing** | Evaluates logical reasoning and analytical thinking |
| 🎯 **Career Recommendations** | Personalized career paths based on user profile |
| 🗺️ **Skill Roadmaps** | Step-by-step learning paths with tools & resources |
| 📍 **Location-Based Suggestions** | Nearby colleges and academies for selected careers |
| 📊 **Results Dashboard** | Visual breakdown of career match scores |
| 📱 **Responsive Design** | Fully functional on desktop and mobile |

---

## 📁 Project Structure

```
Adaptive_Career_Mentor_AI/
│
├── 📂 data/
│   ├── careers.json              # Career data and metadata
│   ├── community_insights.json   # Community-based career insights
│   └── locations.json            # Location-based college data
│
├── 📂 static/
│   ├── script.js                 # Frontend JavaScript logic
│   └── style.css                 # Global styles and animations
│
├── 📂 templates/
│   ├── index.html                # Landing page
│   ├── login.html                # Authentication page
│   ├── chat.html                 # Chatbot interface
│   └── result.html               # Career results dashboard
│
├── app.py                        # Flask backend & routing
├── revert.py                     # Utility script
└── README.md
```

---

## 🛠️ Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Custom animations and glassmorphism UI design
- Responsive layout with CSS Grid & Flexbox

**Backend:**
- Python 3.10+
- Flask (Web Framework)
- JSON-based data storage

**AI & Logic:**
- Rule-based recommendation engine
- Aptitude scoring algorithm
- Weighted career matching system

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Nilakshi15/adaptive-career-mentor-ai.git

# 2. Navigate into the project folder
cd Adaptive_Career_Mentor_AI

# 3. Create a virtual environment (recommended)
python -m venv venv

# 4. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 5. Install dependencies
pip install flask

# 6. Run the application
python app.py
```

### Then open your browser and visit:
```
http://127.0.0.1:5000
```

## 🔄 How It Works

```
User Registers / Logs In
        ↓
Chatbot Collects Interests & Skills
        ↓
Aptitude Test is Conducted
        ↓
AI Engine Analyzes User Profile
        ↓
Career Recommendations Generated (with match scores)
        ↓
Skill Roadmap + Location Suggestions Displayed
```

1. **User Authentication** — Users create an account and log in securely.
2. **Chatbot Interaction** — The chatbot walks users through a series of questions about their interests, skills, and goals.
3. **Aptitude Test** — A built-in test evaluates logical and analytical abilities.
4. **Recommendation Engine** — Combines all inputs to suggest the most suitable career paths.
5. **Results Dashboard** — Displays career match scores, skill gaps, roadmaps, and nearby learning institutions.

---

## 📸 Screenshots

![Home Page](Images/home_page.png)
![Chatbot Interface](Images/chatbot_interface.png)
![Result dashboard](Images/result_dashboard.png)
![Career Pathways](Images/career_pathways.png)

---

## 📊 Survey & Validation

A Google Forms survey was conducted to validate the need for this system and evaluate user experience.

🔗 **Survey Link:** [View Survey](https://docs.google.com/forms/d/1_hOiO9U6p2SFe9UnbmuwqqZTy0WrxTLg2AnwuErtGXw/edit?chromeless=1)


**Key Findings:**
- ✅ Majority of users reported confusion when selecting a career path
- ✅ High demand for personalized and structured career guidance
- ✅ Users preferred interactive chatbot format over static tools
- ✅ Location-based suggestions were rated as highly practical

---

## 🚀 Future Enhancements

- [ ] Integration with real AI/LLM APIs (OpenAI, Gemini)
- [ ] User profile saving and progress tracking
- [ ] PDF export of career roadmaps
- [ ] Multilingual support
- [ ] Admin dashboard for data management
- [ ] Mobile app version (Flutter/React Native)
- [ ] Real-time job market data integration

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/AmazingFeature

# 3. Commit your changes
git commit -m "Add AmazingFeature"

# 4. Push to the branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

---

## 👨‍💻 Author

**Nilakshi Patil**
- GitHub: [@Nilakshi15](https://github.com/Nilakshi15)

---

<div align="center">

⭐ **If you found this project helpful, please give it a star!** ⭐

Made with ❤️ for students everywhere

</div>