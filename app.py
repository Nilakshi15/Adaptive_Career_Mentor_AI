"""
═══════════════════════════════════════════════════════════════════════════════
  Adaptive AI Mentor System for Career Intelligence
  & Personalized Pathway Generation
═══════════════════════════════════════════════════════════════════════════════

System Architecture — Research-Backed Hybrid Assessment Platform:

  ┌────────────────────────────────────────────────────────────────────────┐
  │  Module Stack                                                        │
  │  ─────────                                                           │
  │  1. DualEntryRouter       — Stage selection + Guided/Discovery mode  │
  │  2. RIASECProfiler        — Holland's 6-type interest mapping        │
  │  3. BigFiveProfiler       — O/C/E/A/N personality trait scoring      │
  │  4. TextAnalyzer          — Rule-based keyword/pattern NLP           │
  │  5. AptitudeAssessor      — Logical, Creative, Verbal assessment     │
  │  6. BehavioralTracker     — Consistency & confidence scoring         │
  │  7. CareerMatcher (CSS)   — Multi-factor suitability formula         │
  │  8. RoadmapGenerator      — Stage-adapted pathway builder            │
  │  9. LocationIntelligence  — Pune/Maharashtra institution mapping     │
  │  10. CommunityInsights    — Anonymized aggregate analytics           │
  └────────────────────────────────────────────────────────────────────────┘

Scoring Formula:
  CSS = 0.30·interest_match + 0.25·aptitude_match + 0.25·traits_match
      + 0.10·behavioral + 0.10·stage_fit
  Score range: 0–100.  Threshold ≥70 = strong fit.

Psychometric Models:
  - Holland's RIASEC (Strong Interest Inventory analog)
  - Big Five / OCEAN personality dimensions
  - Multi-dimensional aptitude battery (logical, creative, verbal)

═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json, os, math, re, uuid
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "adaptive-mentor-psychometric-2024")

# ═══════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
COMMUNITY_FILE = os.path.join(DATA_DIR, "community_insights.json")


def load_careers():
    with open(os.path.join(DATA_DIR, "careers.json"), "r") as f:
        return json.load(f)


def load_locations():
    with open(os.path.join(DATA_DIR, "locations.json"), "r") as f:
        return json.load(f)


def load_community():
    if os.path.exists(COMMUNITY_FILE):
        with open(COMMUNITY_FILE, "r") as f:
            return json.load(f)
    return {"total_users": 0, "career_counts": {}, "avg_riasec": {}, "stage_dist": {}}


def save_community(data):
    with open(COMMUNITY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ═══════════════════════════════════════════════════════════
# 1. ADAPTIVE QUESTION BANK
#    Dual-mode: Discovery (full RIASEC) and Guided (domain-specific)
#    60% scenario/open-text, 40% MCQ as specified.
# ═══════════════════════════════════════════════════════════

QUESTION_BANK = {
    # ── Phase 0: Onboarding ──────────────────────────────────
    "stage_select": {
        "id": "stage_select", "phase": "onboarding", "phase_label": "Getting Started",
        "step": 1, "total_steps": 18,
        "text": "Welcome! Let's start by understanding where you are in your journey.",
        "subtext": "Your educational stage helps us tailor the assessment depth and career recommendations",
        "type": "single_choice",
        "options": [
            {"value": "after_10th",       "label": "After 10th standard", "icon": "📘"},
            {"value": "after_12th_sci",   "label": "After 12th — Science stream"},
            {"value": "after_12th_com",   "label": "After 12th — Commerce stream"},
            {"value": "after_12th_arts",  "label": "After 12th — Arts / Humanities"},
            {"value": "in_college",       "label": "Currently in college", "icon": "🎓"},
            {"value": "graduate",         "label": "Graduate / Career switcher"},
        ],
        "next": "domain_select",
    },

    "domain_select": {
        "id": "domain_select", "phase": "onboarding", "phase_label": "Getting Started",
        "step": 2, "total_steps": 18,
        "text": "Do you have a specific domain interest, or would you prefer a complete exploration?",
        "subtext": "Guided mode dives deep into your chosen area; Discovery mode maps your full interest profile",
        "type": "single_choice",
        "options": [
            {"value": "it_software",   "label": "IT & Software Development", "mode": "guided"},
            {"value": "healthcare",    "label": "Healthcare & Life Sciences", "mode": "guided"},
            {"value": "business",      "label": "Business & Finance", "mode": "guided"},
            {"value": "creative",      "label": "Design & Creative Arts", "mode": "guided"},
            {"value": "engineering",   "label": "Engineering & Manufacturing", "mode": "guided"},
            {"value": "discover",      "label": "I'm not sure — help me explore", "mode": "discovery"},
        ],
        "next": "riasec_1",
    },

    # ── Phase 1: RIASEC Interest Mapping (5 Qs) ─────────────
    "riasec_1": {
        "id": "riasec_1", "phase": "interest", "phase_label": "Interest Discovery (RIASEC)",
        "step": 3, "total_steps": 18,
        "text": "Which statement resonates more with you?",
        "subtext": "Holland's Interest Mapping — Realistic vs Social dimension",
        "type": "single_choice",
        "options": [
            {"value": "realistic",  "label": "I enjoy working with tools, machines, or building physical/digital things"},
            {"value": "social",     "label": "I prefer helping people, mentoring, or resolving personal problems"},
            {"value": "both",       "label": "I connect with both — depends on context"},
        ],
        "riasec_scores": {
            "realistic": {"R": 8, "S": 2},
            "social":    {"R": 2, "S": 8},
            "both":      {"R": 5, "S": 5},
        },
        "next": "riasec_2",
    },
    "riasec_2": {
        "id": "riasec_2", "phase": "interest", "phase_label": "Interest Discovery (RIASEC)",
        "step": 4, "total_steps": 18,
        "text": "Which excites you more?",
        "subtext": "Investigative vs Enterprising dimension",
        "type": "single_choice",
        "options": [
            {"value": "investigative", "label": "Investigating how things work through research and analysis"},
            {"value": "enterprising",  "label": "Persuading others, leading teams, or selling ideas"},
            {"value": "both",          "label": "I enjoy both depending on the situation"},
        ],
        "riasec_scores": {
            "investigative": {"I": 8, "E": 2},
            "enterprising":  {"I": 2, "E": 8},
            "both":          {"I": 5, "E": 5},
        },
        "next": "riasec_3",
    },
    "riasec_3": {
        "id": "riasec_3", "phase": "interest", "phase_label": "Interest Discovery (RIASEC)",
        "step": 5, "total_steps": 18,
        "text": "Which activity appeals to you more?",
        "subtext": "Artistic vs Conventional dimension",
        "type": "single_choice",
        "options": [
            {"value": "artistic",     "label": "Creative expression — art, writing, music, or design"},
            {"value": "conventional", "label": "Organizing data, maintaining records, following systems"},
            {"value": "both",         "label": "I appreciate both structure and creativity"},
        ],
        "riasec_scores": {
            "artistic":     {"A": 8, "C": 2},
            "conventional": {"A": 2, "C": 8},
            "both":         {"A": 5, "C": 5},
        },
        "next": "riasec_4",
    },
    "riasec_4": {
        "id": "riasec_4", "phase": "interest", "phase_label": "Interest Discovery (RIASEC)",
        "step": 6, "total_steps": 18,
        "text": "Imagine you're organizing a community event in Pune. Which role would you volunteer for?",
        "subtext": "Scenario-based RIASEC holistic assessment",
        "type": "single_choice",
        "options": [
            {"value": "tech_setup",   "label": "Setting up equipment, AV, and technical infrastructure"},
            {"value": "research",     "label": "Researching the best approach and creating a strategic plan"},
            {"value": "design",       "label": "Designing promotional materials, stage decor, and branding"},
            {"value": "coordinate",   "label": "Coordinating volunteers, managing attendees, emceeing"},
            {"value": "sponsors",     "label": "Handling sponsorships, partnerships, and the budget"},
            {"value": "logistics",    "label": "Managing registration, schedules, and logistics operations"},
        ],
        "riasec_scores": {
            "tech_setup":  {"R": 7, "I": 2, "A": 1, "S": 1, "E": 1, "C": 2},
            "research":    {"R": 1, "I": 7, "A": 2, "S": 1, "E": 1, "C": 2},
            "design":      {"R": 1, "I": 1, "A": 7, "S": 2, "E": 1, "C": 1},
            "coordinate":  {"R": 1, "I": 1, "A": 1, "S": 7, "E": 3, "C": 1},
            "sponsors":    {"R": 1, "I": 2, "A": 1, "S": 2, "E": 7, "C": 2},
            "logistics":   {"R": 2, "I": 1, "A": 1, "S": 1, "E": 2, "C": 7},
        },
        "next": "riasec_5",
    },
    "riasec_5": {
        "id": "riasec_5", "phase": "interest", "phase_label": "Interest Discovery (RIASEC)",
        "step": 7, "total_steps": 18,
        "text": "On a free weekend, which activity would you most enjoy?",
        "subtext": "Leisure preferences often reveal core interest types",
        "type": "single_choice",
        "options": [
            {"value": "build",    "label": "Building something — a shelf, circuit, or coding project"},
            {"value": "read",     "label": "Reading a deep-dive article or documentary about science"},
            {"value": "create",   "label": "Painting, writing, playing music, or designing something"},
            {"value": "social",   "label": "Volunteering, teaching, or hanging out with friends"},
            {"value": "plan",     "label": "Planning something ambitious — event, business idea, trip"},
            {"value": "organize", "label": "Organizing my space, finances, or planning next week"},
        ],
        "riasec_scores": {
            "build":    {"R": 6, "I": 2, "A": 1, "S": 0, "E": 1, "C": 1},
            "read":     {"R": 0, "I": 6, "A": 2, "S": 0, "E": 1, "C": 1},
            "create":   {"R": 0, "I": 1, "A": 6, "S": 1, "E": 0, "C": 0},
            "social":   {"R": 0, "I": 0, "A": 1, "S": 6, "E": 2, "C": 0},
            "plan":     {"R": 1, "I": 1, "A": 1, "S": 1, "E": 6, "C": 1},
            "organize": {"R": 1, "I": 0, "A": 0, "S": 0, "E": 1, "C": 6},
        },
        "next": "big5_openness",
    },

    # ── Phase 2: Big Five Personality (5 Scenarios) ──────────
    "big5_openness": {
        "id": "big5_openness", "phase": "personality", "phase_label": "Personality Profile (Big Five)",
        "step": 8, "total_steps": 18,
        "text": "You discover a completely new technology that could change your field. How do you respond?",
        "subtext": "Scenario: Openness to Experience",
        "type": "single_choice",
        "options": [
            {"value": "high",   "label": "Immediately dive in and experiment — I love novelty and change"},
            {"value": "medium", "label": "Research it carefully, then gradually adopt it if it proves valuable"},
            {"value": "low",    "label": "Stick with proven tools — I prefer stability over speculation"},
        ],
        "big5_scores": {"high": {"O": 9}, "medium": {"O": 6}, "low": {"O": 3}},
        "next": "big5_conscientiousness",
    },
    "big5_conscientiousness": {
        "id": "big5_conscientiousness", "phase": "personality", "phase_label": "Personality Profile (Big Five)",
        "step": 9, "total_steps": 18,
        "text": "Your project deadline is in one week. What best describes your approach?",
        "subtext": "Scenario: Conscientiousness",
        "type": "single_choice",
        "options": [
            {"value": "high",   "label": "I have a detailed schedule with milestones and daily targets"},
            {"value": "medium", "label": "I have a general plan but stay flexible on execution specifics"},
            {"value": "low",    "label": "I work best under pressure — I'll knock it out in the final stretch"},
        ],
        "big5_scores": {"high": {"C": 9}, "medium": {"C": 6}, "low": {"C": 3}},
        "next": "big5_extraversion",
    },
    "big5_extraversion": {
        "id": "big5_extraversion", "phase": "personality", "phase_label": "Personality Profile (Big Five)",
        "step": 10, "total_steps": 18,
        "text": "After a long, intense workday, you recharge by:",
        "subtext": "Scenario: Extraversion",
        "type": "single_choice",
        "options": [
            {"value": "high",   "label": "Going out with friends or colleagues — social energy fuels me"},
            {"value": "medium", "label": "Balanced — sometimes social, sometimes quiet alone time"},
            {"value": "low",    "label": "Quiet time alone — reading, gaming, or introspective thinking"},
        ],
        "big5_scores": {"high": {"E": 9}, "medium": {"E": 6}, "low": {"E": 3}},
        "next": "big5_agreeableness",
    },
    "big5_agreeableness": {
        "id": "big5_agreeableness", "phase": "personality", "phase_label": "Personality Profile (Big Five)",
        "step": 11, "total_steps": 18,
        "text": "A team member consistently disagrees with your technical approach. How do you handle it?",
        "subtext": "Scenario: Agreeableness",
        "type": "single_choice",
        "options": [
            {"value": "high",   "label": "Actively try to understand their view and find common ground"},
            {"value": "medium", "label": "Present my reasoning clearly but remain open to genuine compromise"},
            {"value": "low",    "label": "Stand firm — my analysis shows my approach is objectively correct"},
        ],
        "big5_scores": {"high": {"A": 9}, "medium": {"A": 6}, "low": {"A": 3}},
        "next": "big5_neuroticism",
    },
    "big5_neuroticism": {
        "id": "big5_neuroticism", "phase": "personality", "phase_label": "Personality Profile (Big Five)",
        "step": 12, "total_steps": 18,
        "text": "Before a major presentation or interview, you typically feel:",
        "subtext": "Scenario: Emotional Stability (inverse Neuroticism)",
        "type": "single_choice",
        "options": [
            {"value": "low",    "label": "Calm and confident — preparation is my armor"},
            {"value": "medium", "label": "Slightly nervous but I manage it effectively through routine"},
            {"value": "high",   "label": "Quite anxious — I replay scenarios and worry about many outcomes"},
        ],
        "big5_scores": {"low": {"N": 3}, "medium": {"N": 6}, "high": {"N": 9}},
        "next": "opentext_problem",
    },

    # ── Phase 3: Open-Text Responses (2 Qs) ─────────────────
    "opentext_problem": {
        "id": "opentext_problem", "phase": "opentext", "phase_label": "In Your Own Words",
        "step": 13, "total_steps": 18,
        "text": "Describe a challenging problem you solved recently. What was your approach?",
        "subtext": "Write freely (3-5 sentences). We analyze your thinking style, not spelling or grammar.",
        "type": "open_text",
        "placeholder": "e.g., In my college project, I had to debug a complex issue where...",
        "next": "opentext_energize",
    },
    "opentext_energize": {
        "id": "opentext_energize", "phase": "opentext", "phase_label": "In Your Own Words",
        "step": 14, "total_steps": 18,
        "text": "What kind of work environment makes you feel most alive and productive?",
        "subtext": "Describe your ideal setting, pace, and collaboration style.",
        "type": "open_text",
        "placeholder": "e.g., I thrive in fast-paced teams where I can brainstorm ideas and...",
        "next": "aptitude_logical1",
    },

    # ── Phase 4: Aptitude Battery (4 Qs) ─────────────────────
    "aptitude_logical1": {
        "id": "aptitude_logical1", "phase": "aptitude", "phase_label": "Aptitude Assessment",
        "step": 15, "total_steps": 18,
        "text": "What comes next in this sequence?  2, 6, 18, 54, ___",
        "subtext": "Logical reasoning — Pattern recognition",
        "type": "single_choice",
        "options": [
            {"value": "108",  "label": "108", "icon": "🔢"},
            {"value": "162",  "label": "162", "icon": "🔢"},
            {"value": "148",  "label": "148", "icon": "🔢"},
            {"value": "172",  "label": "172", "icon": "🔢"},
        ],
        "correct": "162",
        "aptitude_dim": "logical",
        "next": "aptitude_logical2",
    },
    "aptitude_logical2": {
        "id": "aptitude_logical2", "phase": "aptitude", "phase_label": "Aptitude Assessment",
        "step": 16, "total_steps": 18,
        "text": "If all roses are flowers, and some flowers fade quickly, which statement MUST be true?",
        "subtext": "Logical reasoning — Deductive inference",
        "type": "single_choice",
        "options": [
            {"value": "all_roses",  "label": "All roses fade quickly", "icon": "🌹"},
            {"value": "some_roses", "label": "Some roses fade quickly", "icon": "🥀"},
            {"value": "cannot",     "label": "None of these can be concluded with certainty", "icon": "❓"},
            {"value": "no_roses",   "label": "No roses fade quickly", "icon": "🚫"},
        ],
        "correct": "cannot",
        "aptitude_dim": "logical",
        "next": "aptitude_creative",
    },
    "aptitude_creative": {
        "id": "aptitude_creative", "phase": "aptitude", "phase_label": "Aptitude Assessment",
        "step": 17, "total_steps": 18,
        "text": "Pune faces severe traffic congestion during peak hours. Propose one innovative, unconventional solution.",
        "subtext": "Creative aptitude — We evaluate originality, feasibility, and detail of your idea.",
        "type": "open_text",
        "placeholder": "e.g., A neighborhood ride-matching app using AI that groups commuters by destination...",
        "aptitude_dim": "creative",
        "next": "aptitude_verbal",
    },
    "aptitude_verbal": {
        "id": "aptitude_verbal", "phase": "aptitude", "phase_label": "Aptitude Assessment",
        "step": 18, "total_steps": 18,
        "text": "Which word is most similar in meaning to 'Pragmatic'?",
        "subtext": "Verbal reasoning — Vocabulary and comprehension",
        "type": "single_choice",
        "options": [
            {"value": "idealistic",   "label": "Idealistic", "icon": "💭"},
            {"value": "practical",    "label": "Practical", "icon": "🎯"},
            {"value": "theoretical",  "label": "Theoretical", "icon": "📐"},
            {"value": "emotional",    "label": "Emotional", "icon": "💗"},
        ],
        "correct": "practical",
        "aptitude_dim": "verbal",
        "next": "behavioral_risk",
    },

    # ── Phase 5: Behavioral ──────────────────────────────────
    "behavioral_risk": {
        "id": "behavioral_risk", "phase": "behavioral", "phase_label": "Career Preferences",
        "step": 18, "total_steps": 18,
        "text": "How would you describe your ideal career trajectory?",
        "subtext": "Final question! This helps us calibrate risk tolerance and growth preferences.",
        "type": "single_choice",
        "options": [
            {"value": "stable",    "label": "Steady growth in a stable, established organization", "icon": "🏔️"},
            {"value": "dynamic",   "label": "Rapid advancement in a dynamic, fast-growing industry", "icon": "📈"},
            {"value": "venture",   "label": "Building my own venture, freelancing, or consulting", "icon": "🚀"},
            {"value": "research",  "label": "Contributing to research, knowledge, and discovery", "icon": "🔬"},
        ],
        "behavioral_scores": {
            "stable":  {"risk": 2, "E_mod": -1, "C_mod": 2},
            "dynamic": {"risk": 5, "E_mod": 2,  "C_mod": 0},
            "venture": {"risk": 8, "E_mod": 3,  "C_mod": -1},
            "research":{"risk": 3, "E_mod": -2, "C_mod": 1},
        },
        "next": None,
    },
}


# ═══════════════════════════════════════════════════════════
# 2. RIASEC PROFILER
#    Maps responses to Holland's 6-type interest vector.
# ═══════════════════════════════════════════════════════════

class RIASECProfiler:
    """Compute Holland's RIASEC scores from assessment responses."""

    def __init__(self):
        self.scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        self.response_count = 0

    def process_responses(self, responses):
        for resp in responses:
            q = QUESTION_BANK.get(resp.get("question_id"))
            if not q or "riasec_scores" not in q:
                continue
            answer = resp.get("answer", "")
            score_map = q["riasec_scores"].get(answer, {})
            for dim, val in score_map.items():
                self.scores[dim] += val
            self.response_count += 1

    def get_normalized(self):
        """Normalize RIASEC scores to 0–10 scale."""
        max_val = max(self.scores.values(), default=1) or 1
        return {k: round((v / max_val) * 10, 1) for k, v in self.scores.items()}

    def get_top_types(self, n=3):
        normed = self.get_normalized()
        sorted_types = sorted(normed.items(), key=lambda x: x[1], reverse=True)
        return sorted_types[:n]


# ═══════════════════════════════════════════════════════════
# 3. BIG FIVE PROFILER
#    Maps scenario responses to O/C/E/A/N personality scores.
# ═══════════════════════════════════════════════════════════

class BigFiveProfiler:
    """Compute Big Five personality scores from scenarios and text analysis."""

    def __init__(self):
        self.scores = {"O": 5, "C": 5, "E": 5, "A": 5, "N": 5}  # Neutral baseline

    def process_responses(self, responses):
        for resp in responses:
            q = QUESTION_BANK.get(resp.get("question_id"))
            if not q:
                continue
            answer = resp.get("answer", "")

            # Big Five scenario questions
            if "big5_scores" in q:
                score_map = q["big5_scores"].get(answer, {})
                for dim, val in score_map.items():
                    self.scores[dim] = val  # Replace with scenario answer

            # Behavioral modifiers
            if "behavioral_scores" in q:
                bdata = q["behavioral_scores"].get(answer, {})
                if "E_mod" in bdata:
                    self.scores["E"] = max(1, min(10, self.scores["E"] + bdata["E_mod"]))
                if "C_mod" in bdata:
                    self.scores["C"] = max(1, min(10, self.scores["C"] + bdata["C_mod"]))

    def apply_text_modifiers(self, text_analysis):
        """Adjust Big Five based on text analysis (weight 1.5x as specified)."""
        mods = text_analysis.get("big5_modifiers", {})
        for dim, mod in mods.items():
            self.scores[dim] = max(1, min(10, self.scores[dim] + round(mod * 1.5)))

    def get_scores(self):
        return {k: round(v, 1) for k, v in self.scores.items()}


# ═══════════════════════════════════════════════════════════
# 4. TEXT ANALYZER
#    Rule-based keyword/pattern analysis for open-text inputs.
#    Extracts traits, maps to personality & aptitude signals.
# ═══════════════════════════════════════════════════════════

class TextAnalyzer:
    """
    Rule-based NLP for open-text responses.
    Analyzes: keywords → personality traits, sentence patterns → confidence,
    contradictions → consistency.
    """

    # Keyword → Trait mappings
    KEYWORD_MAPS = {
        # Conscientiousness signals
        "plan": ("C", 1), "schedule": ("C", 1), "step": ("C", 1), "organize": ("C", 1),
        "systematic": ("C", 2), "method": ("C", 1), "careful": ("C", 1), "detail": ("C", 1),
        "deadline": ("C", 1), "milestone": ("C", 1), "routine": ("C", 1), "checklist": ("C", 1),

        # Openness signals
        "idea": ("O", 1), "brainstorm": ("O", 2), "creative": ("O", 2), "innovate": ("O", 2),
        "experiment": ("O", 1), "explore": ("O", 1), "curious": ("O", 2), "novel": ("O", 1),
        "imagine": ("O", 1), "vision": ("O", 1), "different": ("O", 1), "unconventional": ("O", 2),

        # Extraversion signals
        "team": ("E", 1), "collaborate": ("E", 2), "discuss": ("E", 1), "present": ("E", 1),
        "network": ("E", 1), "lead": ("E", 1), "group": ("E", 1), "social": ("E", 1),
        "outgoing": ("E", 2), "energetic": ("E", 1),

        # Agreeableness signals
        "help": ("A", 1), "support": ("A", 1), "empathy": ("A", 2), "understand": ("A", 1),
        "cooperative": ("A", 2), "kind": ("A", 1), "compassion": ("A", 2), "listen": ("A", 1),
        "harmony": ("A", 1), "consensus": ("A", 1),

        # Introversion / Low N signals
        "independent": ("E", -1), "solo": ("E", -1), "quiet": ("E", -1), "alone": ("E", -1),
        "focus": ("N", -1), "calm": ("N", -1), "confident": ("N", -1), "steady": ("N", -1),

        # Risk / startup keywords → Enterprising
        "startup": ("E", 1), "venture": ("E", 1), "risk": ("E", 1), "ambitious": ("E", 1),
    }

    # Creative aptitude keywords
    CREATIVE_KEYWORDS = [
        "invent", "design", "prototype", "imagine", "novel", "unconventional",
        "new approach", "outside the box", "fresh", "original", "rethink",
    ]

    def analyze(self, texts):
        """
        Analyze list of open-text responses.
        Returns: {big5_modifiers, confidence, consistency, creativity_score, analysis_notes}
        """
        combined = " ".join(texts).lower()
        words = re.findall(r'\b[a-z]+\b', combined)
        sentences = [s.strip() for s in re.split(r'[.!?]', combined) if s.strip()]

        big5_mods = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
        matched_keywords = []

        # — Keyword extraction —
        for word in words:
            for keyword, (dim, weight) in self.KEYWORD_MAPS.items():
                if keyword in word:
                    big5_mods[dim] += weight
                    matched_keywords.append(f"{word}→{dim}({'+' if weight > 0 else ''}{weight})")

        # — Sentence-level analysis —
        avg_sentence_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        confidence = min(10, max(1, round(avg_sentence_len / 3)))  # Longer = more confident

        # — Creativity score for creative aptitude questions —
        creativity_score = 0
        for kw in self.CREATIVE_KEYWORDS:
            if kw in combined:
                creativity_score += 2

        # Detail/length bonus
        if len(words) > 40:
            creativity_score += 2
        if len(words) > 80:
            creativity_score += 1
        creativity_score = min(10, max(1, creativity_score))

        # — Contradiction detection —
        contradictions = []
        social_signals = sum(1 for w in words if w in ("team", "collaborate", "group", "social"))
        solo_signals = sum(1 for w in words if w in ("independent", "solo", "alone", "quiet"))
        if social_signals > 2 and solo_signals > 2:
            contradictions.append("Mixed social/independent signals")

        consistency = 10 if not contradictions else 6

        return {
            "big5_modifiers": {k: max(-3, min(3, v)) for k, v in big5_mods.items()},
            "confidence": confidence,
            "consistency_penalty": len(contradictions),
            "creativity_score": creativity_score,
            "matched_keywords": matched_keywords[:15],
            "contradictions": contradictions,
            "word_count": len(words),
            "avg_sentence_length": round(avg_sentence_len, 1),
        }


# ═══════════════════════════════════════════════════════════
# 5. APTITUDE ASSESSOR
#    Logical, Creative, Verbal scoring from assessment Qs.
# ═══════════════════════════════════════════════════════════

class AptitudeAssessor:
    """Score logical, creative, and verbal aptitudes."""

    def __init__(self):
        self.scores = {"logical": 5, "creative": 5, "verbal": 5}
        self.raw = {"logical": [], "creative": [], "verbal": []}

    def process_responses(self, responses, text_analysis=None):
        for resp in responses:
            q = QUESTION_BANK.get(resp.get("question_id"))
            if not q or "aptitude_dim" not in q:
                continue

            dim = q["aptitude_dim"]
            answer = resp.get("answer", "")

            if q["type"] == "single_choice" and "correct" in q:
                # Objective question — binary correct/incorrect
                is_correct = (answer == q["correct"])
                score = 9 if is_correct else 3
                self.raw[dim].append(score)
            elif q["type"] == "open_text":
                # Creative aptitude from text analysis
                if text_analysis:
                    self.raw[dim].append(text_analysis.get("creativity_score", 5))

        # Aggregate
        for dim in self.scores:
            if self.raw[dim]:
                self.scores[dim] = round(sum(self.raw[dim]) / len(self.raw[dim]), 1)

    def get_scores(self):
        return self.scores


# ═══════════════════════════════════════════════════════════
# 6. BEHAVIORAL TRACKER
#    Consistency & confidence scoring from response patterns.
# ═══════════════════════════════════════════════════════════

class BehavioralTracker:
    """Track response consistency and confidence signals."""

    def __init__(self):
        self.consistency_score = 8    # Start optimistic, reduce on flags
        self.confidence_level = 5
        self.risk_tolerance = 5
        self.flags = []

    def process(self, responses, riasec_scores, big5_scores, text_analysis):
        # — Consistency: check RIASEC-Big5 alignment —
        # Social RIASEC should correlate with Extraversion+Agreeableness
        s_score = riasec_scores.get("S", 0)
        e_big5 = big5_scores.get("E", 5)
        a_big5 = big5_scores.get("A", 5)

        if s_score > 7 and e_big5 < 4:
            self.consistency_score -= 2
            self.flags.append("Social interests but low extraversion — internal conflict")
        if s_score > 7 and a_big5 < 4:
            self.consistency_score -= 1
            self.flags.append("Social interests but low agreeableness — possible misalignment")

        # Investigative RIASEC should correlate with Openness
        i_score = riasec_scores.get("I", 0)
        o_big5 = big5_scores.get("O", 5)
        if i_score > 7 and o_big5 < 4:
            self.consistency_score -= 1
            self.flags.append("Investigative interests but low openness — unusual combination")

        # Text analysis consistency
        if text_analysis:
            self.consistency_score -= text_analysis.get("consistency_penalty", 0)
            self.confidence_level = text_analysis.get("confidence", 5)

        # Behavioral question - risk
        for resp in responses:
            q = QUESTION_BANK.get(resp.get("question_id"))
            if q and "behavioral_scores" in q:
                bdata = q["behavioral_scores"].get(resp.get("answer"), {})
                self.risk_tolerance = bdata.get("risk", 5)

        self.consistency_score = max(1, min(10, self.consistency_score))

    def get_behavioral(self):
        is_consistent = self.consistency_score >= 7
        return {
            "consistency_score": self.consistency_score,
            "confidence_level": self.confidence_level,
            "risk_tolerance": self.risk_tolerance,
            "alignment_status": "High alignment" if is_consistent else "Some misalignment detected",
            "flags": self.flags,
        }


# ═══════════════════════════════════════════════════════════
# 7. CAREER MATCHER (CSS Engine)
#    CSS = 0.30·interest + 0.25·aptitude + 0.25·traits
#        + 0.10·behavioral + 0.10·stage_fit
# ═══════════════════════════════════════════════════════════

def cosine_similarity(vec_a, vec_b, keys):
    """Compute cosine similarity between two vectors over given keys."""
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(vec_a.get(k, 0) ** 2 for k in keys)) or 1
    mag_b = math.sqrt(sum(vec_b.get(k, 0) ** 2 for k in keys)) or 1
    return dot / (mag_a * mag_b)


def compute_css(user_profile, career, stage):
    """
    Career Suitability Score (0–100).
    CSS = 0.30·interest_match + 0.25·aptitude_match + 0.25·traits_match
        + 0.10·behavioral + 0.10·stage_fit
    """
    # 1. Interest match: RIASEC cosine similarity
    riasec_keys = ["R", "I", "A", "S", "E", "C"]
    interest_match = cosine_similarity(
        user_profile["riasec"], career["riasec_req"], riasec_keys
    )

    # 2. Aptitude match: weighted average of dimension matches
    apt_total, apt_count = 0, 0
    for dim in ["logical", "creative", "verbal"]:
        user_val = user_profile["aptitudes"].get(dim, 5)
        req_val = career["aptitude_req"].get(dim, 5)
        match_ratio = min(user_val / max(req_val, 1), 1.0)
        apt_total += match_ratio
        apt_count += 1
    aptitude_match = apt_total / max(apt_count, 1)

    # 3. Traits match: Big Five cosine similarity
    big5_keys = ["O", "C", "E", "A", "N"]
    traits_match = cosine_similarity(
        user_profile["big5"], career["big5_req"], big5_keys
    )

    # 4. Behavioral: normalized consistency + confidence
    behavioral = user_profile["behavioral"]
    behavioral_score = (
        (behavioral["consistency_score"] / 10) * 0.6 +
        (behavioral["confidence_level"] / 10) * 0.4
    )

    # 5. Stage fit
    stage_val = career.get("stage_fit", {}).get(stage, 5)
    stage_fit = stage_val / 10.0

    # Composite
    css = (
        0.30 * interest_match +
        0.25 * aptitude_match +
        0.25 * traits_match +
        0.10 * behavioral_score +
        0.10 * stage_fit
    ) * 100

    return {
        "css": round(css, 1),
        "breakdown": {
            "interest_match": round(interest_match * 100, 1),
            "aptitude_match": round(aptitude_match * 100, 1),
            "traits_match": round(traits_match * 100, 1),
            "behavioral": round(behavioral_score * 100, 1),
            "stage_fit": round(stage_fit * 100, 1),
        },
    }


def rank_careers(user_profile, careers, stage, top_n=5):
    """Rank all careers by CSS and return top N."""
    results = []
    for career in careers:
        css_data = compute_css(user_profile, career, stage)
        results.append({"career": career, **css_data})
    results.sort(key=lambda x: x["css"], reverse=True)
    return results[:top_n], results


# ═══════════════════════════════════════════════════════════
# 8. EXPLAINABLE RECOMMENDATION ENGINE
#    Rule-based justifications tied to specific profile inputs.
# ═══════════════════════════════════════════════════════════

def generate_explanations(user_profile, career, css_data):
    """Generate structured, rule-based explanations for a career match."""
    explanations = []
    bd = css_data["breakdown"]
    riasec_labels = {"R": "Realistic", "I": "Investigative", "A": "Artistic",
                     "S": "Social", "E": "Enterprising", "C": "Conventional"}
    big5_labels = {"O": "Openness", "C": "Conscientiousness", "E": "Extraversion",
                   "A": "Agreeableness", "N": "Emotional Stability"}

    # — RIASEC alignment —
    user_top = sorted(user_profile["riasec"].items(), key=lambda x: x[1], reverse=True)[:2]
    career_top = sorted(career["riasec_req"].items(), key=lambda x: x[1], reverse=True)[:2]

    overlap = set(t[0] for t in user_top) & set(t[0] for t in career_top)
    if len(overlap) >= 2:
        types_str = " + ".join(riasec_labels[t] for t in overlap)
        explanations.append({"type": "strength", "cat": "Interest", "text": f"Strong alignment: your top RIASEC types ({types_str}) match this career's requirements"})
    elif len(overlap) == 1:
        t = list(overlap)[0]
        explanations.append({"type": "strength", "cat": "Interest", "text": f"Partial alignment: your {riasec_labels[t]} interest type matches this role"})
    else:
        explanations.append({"type": "gap", "cat": "Interest", "text": f"Interest profile differs from typical practitioners — consider exploration projects to validate fit"})

    # — Big Five insights —
    for dim in ["O", "C", "E", "A"]:
        user_val = user_profile["big5"].get(dim, 5)
        req_val = career["big5_req"].get(dim, 5)
        diff = user_val - req_val
        if diff >= 2:
            explanations.append({"type": "strength", "cat": "Personality",
                "text": f"Your high {big5_labels[dim]} ({user_val}/10) exceeds this role's needs — a strong asset"})
        elif diff <= -3:
            explanations.append({"type": "gap", "cat": "Personality",
                "text": f"This role typically requires higher {big5_labels[dim]} (needs {req_val}, you scored {user_val}) — growth area"})

    # — Aptitude —
    for dim in ["logical", "creative", "verbal"]:
        user_val = user_profile["aptitudes"].get(dim, 5)
        req_val = career["aptitude_req"].get(dim, 5)
        if user_val >= req_val:
            explanations.append({"type": "strength", "cat": "Aptitude",
                "text": f"Your {dim} aptitude ({user_val}/10) meets the requirement ({req_val}/10)"})
        elif req_val - user_val >= 3:
            explanations.append({"type": "gap", "cat": "Aptitude",
                "text": f"Significant {dim} aptitude gap: you scored {user_val}/10 vs required {req_val}/10"})

    # — Behavioral —
    beh = user_profile["behavioral"]
    if beh["consistency_score"] >= 8:
        explanations.append({"type": "insight", "cat": "Behavioral",
            "text": "High consistency across your responses indicates clear self-awareness"})
    elif beh["consistency_score"] < 6:
        explanations.append({"type": "flag", "cat": "Behavioral",
            "text": "Some inconsistencies detected — recommendation confidence is slightly reduced"})
    for flag in beh.get("flags", [])[:2]:
        explanations.append({"type": "flag", "cat": "Behavioral", "text": flag})

    # — Overall verdict —
    css = css_data["css"]
    if css >= 80:
        explanations.append({"type": "verdict", "cat": "Overall",
            "text": f"Highly recommended — strong multi-dimensional alignment (CSS: {css}/100)"})
    elif css >= 70:
        explanations.append({"type": "verdict", "cat": "Overall",
            "text": f"Strong fit with targeted development opportunities (CSS: {css}/100)"})
    elif css >= 55:
        explanations.append({"type": "verdict", "cat": "Overall",
            "text": f"Good potential — invest in identified growth areas (CSS: {css}/100)"})
    else:
        explanations.append({"type": "verdict", "cat": "Overall",
            "text": f"Exploratory option — significant development needed (CSS: {css}/100)"})

    return explanations


# ═══════════════════════════════════════════════════════════
# 9. SKILL GAP ANALYSIS
# ═══════════════════════════════════════════════════════════

def analyze_gaps(user_profile, career):
    """Quantitative skill gap: user aptitudes vs career requirements."""
    gaps = []
    for dim in ["logical", "creative", "verbal"]:
        user_val = user_profile["aptitudes"].get(dim, 5)
        req_val = career["aptitude_req"].get(dim, 5)
        gap = req_val - user_val
        gaps.append({
            "skill": dim.title(),
            "user_level": user_val,
            "required": req_val,
            "gap": round(max(0, gap), 1),
            "surplus": round(max(0, -gap), 1),
            "status": "surplus" if gap < -0.5 else ("adequate" if abs(gap) <= 0.5 else "gap"),
        })
    return gaps


# ═══════════════════════════════════════════════════════════
# 10. ROADMAP GENERATOR
#     Stage-adapted pathway with skills/tools/projects.
# ═══════════════════════════════════════════════════════════

STAGE_TO_LEVEL = {
    "after_10th": "beginner",
    "after_12th_sci": "beginner",
    "after_12th_com": "beginner",
    "after_12th_arts": "beginner",
    "in_college": "intermediate",
    "graduate": "advanced",
}


def generate_roadmap(career, stage):
    """Build stage-adapted career pathway."""
    start_level = STAGE_TO_LEVEL.get(stage, "beginner")
    roadmap_data = career.get("roadmap", {})

    levels = ["beginner", "intermediate", "advanced"]
    start_idx = levels.index(start_level)

    pathway = []
    for lvl in levels[start_idx:]:
        if lvl in roadmap_data:
            entry = roadmap_data[lvl].copy()
            entry["level"] = lvl.title()
            entry["is_starting"] = (lvl == start_level)
            pathway.append(entry)

    return {
        "starting_level": start_level.title(),
        "total_duration": _sum_durations(pathway),
        "stages": pathway,
    }


def _sum_durations(stages):
    """Rough total duration estimate."""
    total_low, total_high = 0, 0
    for s in stages:
        dur = s.get("duration", "1–3 months")
        parts = re.findall(r'(\d+)', dur)
        if len(parts) >= 2:
            total_low += int(parts[0])
            total_high += int(parts[1])
        elif parts:
            total_low += int(parts[0])
            total_high += int(parts[0])
    return f"{total_low}–{total_high} months"


# ═══════════════════════════════════════════════════════════
# 11. LOCATION INTELLIGENCE
#     Pune/Maharashtra-specific institution & opportunity data.
# ═══════════════════════════════════════════════════════════

def get_location_data(career_id):
    """Retrieve Pune-specific institutions and job data for a career."""
    locations = load_locations()
    career_loc = locations.get("career_locations", {}).get(career_id, {})
    category_map = {
        "software_engineer": "technology", "data_scientist": "technology",
        "ml_engineer": "technology", "cybersecurity_analyst": "technology",
        "cloud_architect": "technology", "ux_designer": "creative",
        "game_developer": "creative", "content_strategist": "creative",
        "product_manager": "business", "business_analyst": "business",
        "digital_marketing": "business", "management_consultant": "business",
        "research_scientist": "science", "biotech_researcher": "science",
        "nurse_healthcare": "healthcare", "civil_engineer": "engineering",
        "arvr_developer": "creative_technology", "creative_technologist": "creative_technology",
    }
    cat = category_map.get(career_id, "technology")
    institutions = locations.get("institutions", {}).get(cat, [])

    return {
        "city": locations.get("city", "Pune"),
        "institutions": institutions[:5],
        "career_data": career_loc,
        "market_summary": locations.get("market_summary", ""),
    }


# ═══════════════════════════════════════════════════════════
# 12. COMMUNITY INSIGHTS (Simulated Aggregate)
# ═══════════════════════════════════════════════════════════

def update_community(top_results, user_profile, stage):
    community = load_community()
    community["total_users"] = community.get("total_users", 0) + 1

    cc = community.get("career_counts", {})
    for r in top_results[:5]:
        cid = r["career"]["id"]
        cc[cid] = cc.get(cid, 0) + 1
    community["career_counts"] = cc

    sd = community.get("stage_dist", {})
    sd[stage] = sd.get(stage, 0) + 1
    community["stage_dist"] = sd

    # Running avg RIASEC
    n = community["total_users"]
    avg_r = community.get("avg_riasec", {})
    for dim in ["R", "I", "A", "S", "E", "C"]:
        old = avg_r.get(dim, 0)
        avg_r[dim] = round(((old * (n - 1)) + user_profile["riasec"].get(dim, 0)) / n, 2)
    community["avg_riasec"] = avg_r

    save_community(community)
    return community


# ═══════════════════════════════════════════════════════════
# FLASK ROUTES — Page Rendering
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/auth", methods=["POST"])
def api_auth():
    """Simulated Google OAuth — stores user profile in session."""
    data = request.get_json(force=True)
    session["user"] = {
        "name": data.get("name", "User"),
        "email": data.get("email", "user@example.com"),
        "uid": str(uuid.uuid4())[:8],
        "location": data.get("location", "Pune, Maharashtra"),
        "created_at": datetime.now().isoformat(),
    }
    return jsonify({"status": "ok", "user": session["user"]})

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/result")
def result():
    return render_template("result.html")


# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.route("/api/question", methods=["POST"])
def api_question():
    """
    Adaptive question flow. Returns next question based on
    the full response history. Handles conditional branching
    and mode-aware routing (Guided vs Discovery).
    """
    data = request.get_json(force=True)
    responses = data.get("responses", [])

    if not responses:
        return jsonify({"status": "question", "question": QUESTION_BANK["stage_select"]})

    last = responses[-1]
    last_q = QUESTION_BANK.get(last.get("question_id"))
    if not last_q:
        return jsonify({"status": "error", "message": "Unknown question ID"})

    next_id = last_q.get("next")
    if next_id is None:
        return jsonify({"status": "complete"})

    # Conditional branching (dict-based routing)
    if isinstance(next_id, dict):
        answer = last.get("answer", "")
        next_id = next_id.get(answer, list(next_id.values())[0])

    next_q = QUESTION_BANK.get(next_id)
    if not next_q:
        return jsonify({"status": "complete"})

    return jsonify({"status": "question", "question": next_q})


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Core analysis pipeline:
      1. Extract stage & mode from onboarding responses
      2. Build RIASEC profile
      3. Build Big Five profile
      4. Analyze open-text responses
      5. Score aptitudes
      6. Track behavioral flags
      7. Compute CSS for all careers
      8. Generate explanations, gaps, roadmaps, locations
      9. Update community data
    """
    data = request.get_json(force=True)
    responses = data.get("responses", [])
    if not responses:
        return jsonify({"status": "error", "message": "No responses"}), 400

    # ── Extract onboarding data ──────────────
    stage = "graduate"
    mode = "discovery"
    domain = None
    for r in responses:
        if r["question_id"] == "stage_select":
            stage = r["answer"]
        if r["question_id"] == "domain_select":
            domain = r["answer"]
            mode = "guided" if r["answer"] != "discover" else "discovery"

    # ── 1. RIASEC Profiling ──────────────────
    riasec = RIASECProfiler()
    riasec.process_responses(responses)
    riasec_scores = riasec.get_normalized()

    # ── 2. Text Analysis ─────────────────────
    open_texts = [r["answer"] for r in responses
                  if QUESTION_BANK.get(r["question_id"], {}).get("type") == "open_text"
                  and isinstance(r.get("answer"), str)]
    text_analyzer = TextAnalyzer()
    text_analysis = text_analyzer.analyze(open_texts) if open_texts else {
        "big5_modifiers": {}, "confidence": 5, "consistency_penalty": 0,
        "creativity_score": 5, "matched_keywords": [], "contradictions": [],
        "word_count": 0, "avg_sentence_length": 0,
    }

    # ── 3. Big Five Profiling ────────────────
    big5 = BigFiveProfiler()
    big5.process_responses(responses)
    big5.apply_text_modifiers(text_analysis)
    big5_scores = big5.get_scores()

    # ── 4. Aptitude Assessment ───────────────
    aptitude = AptitudeAssessor()
    aptitude.process_responses(responses, text_analysis)
    apt_scores = aptitude.get_scores()

    # ── 5. Behavioral Tracking ───────────────
    behavioral = BehavioralTracker()
    behavioral.process(responses, riasec_scores, big5_scores, text_analysis)
    beh_data = behavioral.get_behavioral()

    # ── Build user profile vector ────────────
    user_profile = {
        "riasec": riasec_scores,
        "big5": big5_scores,
        "aptitudes": apt_scores,
        "behavioral": beh_data,
        "stage": stage,
        "mode": mode,
        "domain": domain,
    }

    # ── 6. Career Matching ───────────────────
    career_data = load_careers()
    careers = career_data["careers"]

    # In guided mode, filter careers by domain
    if mode == "guided" and domain:
        domain_map = {
            "it_software": ["software_engineer", "data_scientist", "ml_engineer",
                           "cybersecurity_analyst", "cloud_architect"],
            "healthcare": ["nurse_healthcare", "biotech_researcher", "research_scientist"],
            "business": ["product_manager", "business_analyst", "management_consultant",
                        "digital_marketing"],
            "creative": ["ux_designer", "game_developer", "content_strategist"],
            "engineering": ["civil_engineer", "software_engineer", "cloud_architect"],
        }
        allowed = domain_map.get(domain, [c["id"] for c in careers])
        filtered = [c for c in careers if c["id"] in allowed]
        top_results, all_results = rank_careers(user_profile, filtered, stage, top_n=5)
    else:
        top_results, all_results = rank_careers(user_profile, careers, stage, top_n=5)

    # ── 7. Generate full results ─────────────
    result_cards = []
    for entry in top_results:
        career = entry["career"]
        explanations = generate_explanations(user_profile, career, entry)
        gaps = analyze_gaps(user_profile, career)
        roadmap = generate_roadmap(career, stage)
        loc_data = get_location_data(career["id"])

        result_cards.append({
            "career_id": career["id"],
            "title": career["title"],
            "description": career["description"],
            "icon": career["icon"],
            "category": career["category"],
            "css": entry["css"],
            "breakdown": entry["breakdown"],
            "explanations": explanations,
            "skill_gaps": gaps,
            "roadmap": roadmap,
            "location": loc_data,
            "salary_range": career["salary_range"],
            "growth_outlook": career["growth_outlook"],
        })

    # ── 8. Community update ──────────────────
    community = update_community(top_results, user_profile, stage)

    # ── Return structured response ───────────
    return jsonify({
        "status": "success",
        "profile": {
            "riasec": riasec_scores,
            "riasec_top": riasec.get_top_types(3),
            "big5": big5_scores,
            "aptitudes": apt_scores,
            "behavioral": beh_data,
            "text_analysis": {
                "matched_keywords": text_analysis["matched_keywords"],
                "word_count": text_analysis["word_count"],
                "creativity_score": text_analysis["creativity_score"],
            },
            "stage": stage,
            "mode": mode,
        },
        "results": result_cards,
        "all_scores": [
            {"title": r["career"]["title"], "css": r["css"], "id": r["career"]["id"]}
            for r in all_results
        ],
        "community": {
            "total_users": community.get("total_users", 0),
            "top_careers": sorted(community.get("career_counts", {}).items(),
                                  key=lambda x: x[1], reverse=True)[:5],
            "avg_riasec": community.get("avg_riasec", {}),
            "stage_distribution": community.get("stage_dist", {}),
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "model_version": "2.0.0",
            "scoring_formula": "CSS = 0.30·interest + 0.25·aptitude + 0.25·traits + 0.10·behavioral + 0.10·stage_fit",
            "psychometric_models": ["Holland RIASEC", "Big Five (OCEAN)", "Multi-aptitude battery"],
        },
    })


@app.route("/api/careers", methods=["GET"])
def api_careers():
    data = load_careers()
    return jsonify({"careers": data["careers"], "count": len(data["careers"])})


@app.route("/api/community", methods=["GET"])
def api_community():
    c = load_community()
    data = load_careers()
    name_map = {cr["id"]: cr["title"] for cr in data["careers"]}
    top = [{"id": k, "title": name_map.get(k, k), "count": v}
           for k, v in sorted(c.get("career_counts", {}).items(), key=lambda x: x[1], reverse=True)[:5]]
    return jsonify({
        "total_users": c.get("total_users", 0),
        "top_careers": top,
        "avg_riasec": c.get("avg_riasec", {}),
        "stage_distribution": c.get("stage_dist", {}),
    })


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  Adaptive AI Mentor System v2.0")
    print("  Career Intelligence & Personalized Pathway Generation")
    print("  ─────────────────────────────────────────────────────")
    print("  Models: Holland RIASEC │ Big Five │ Multi-Aptitude")
    print("  Scoring: CSS = 0.30·I + 0.25·A + 0.25·T + 0.10·B + 0.10·S")
    print("=" * 65)
    print("  → http://127.0.0.1:5000")
    print("=" * 65 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
