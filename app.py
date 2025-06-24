"""
Fully Dynamic AI Leadership Assessment Engine
Production-ready system with 100% AI-generated content
7 Yes/No/Maybe + 7 MCQ + 1 Writing Scenario
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
import google.generativeai as genai
from typing import Dict, List, Optional
import re
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Dynamic AI Leadership Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bilingual content structure
CONTENT = {
    'en': {
        'title': "🧠 Dynamic AI Leadership Assessment",
        'subtitle': "Comprehensive Leadership Evaluation - 7+7+1 Format",
        'language_label': "Language / اللغة",
        'welcome_title': "Welcome to Dynamic AI Leadership Assessment",
        'welcome_desc': "7 Yes/No/Maybe + 7 Multiple Choice + 1 Writing Scenario",
        'begin_assessment': "🚀 Begin Assessment",
        'profile_title': "👤 Personal & Professional Profile",
        'profile_desc': "Your information shapes every aspect of your assessment",
        'assessment_progress': "Assessment Progress",
        'yes': "Yes",
        'no': "No", 
        'maybe': "Maybe",
        'next_question': "Next Question ➡️",
        'previous_question': "⬅️ Previous Question",
        'complete_assessment': "🎯 Complete Assessment",
        'generating_report': "📊 Generating your personalized report...",
        'report_title': "📊 Your Personalized Leadership Assessment Report",
        'overall_score': "Overall Score",
        'download_report': "📄 Download Report",
        'new_assessment': "🔄 New Assessment",
        'api_error': "API Configuration Error",
        'api_missing': "Gemini API key not found. Please check your .env file.",
        'pillars': [
            "Strategic Thinking",
            "Leading Change & Adaptability", 
            "Effective Communication & Influence",
            "Empowerment & Motivation",
            "Responsibility & Accountability",
            "Innovation & Continuous Improvement"
        ]
    },
    'ar': {
        'title': "🧠 مقياس القيادة الذكي الديناميكي",
        'subtitle': "تقييم قيادي شامل - نموذج 7+7+1",
        'language_label': "اللغة / Language",
        'welcome_title': "مرحباً بك في مقياس القيادة الذكي الديناميكي",
        'welcome_desc': "7 نعم/لا/ربما + 7 متعدد الخيارات + 1 سيناريو كتابي",
        'begin_assessment': "🚀 بدء التقييم",
        'profile_title': "👤 الملف الشخصي والمهني",
        'profile_desc': "معلوماتك تشكل كل جانب من جوانب تقييمك",
        'assessment_progress': "تقدم التقييم",
        'yes': "نعم",
        'no': "لا",
        'maybe': "ربما",
        'next_question': "السؤال التالي ➡️",
        'previous_question': "⬅️ السؤال السابق",
        'complete_assessment': "🎯 إكمال التقييم",
        'generating_report': "📊 جاري إنشاء تقريرك الشخصي...",
        'report_title': "📊 تقرير تقييم القيادة الشخصي",
        'overall_score': "النتيجة الإجمالية",
        'download_report': "📄 تحميل التقرير",
        'new_assessment': "🔄 تقييم جديد",
        'api_error': "خطأ في إعدادات API",
        'api_missing': "لم يتم العثور على مفتاح Gemini API",
        'pillars': [
            "التفكير الاستراتيجي",
            "قيادة التغيير والتكيف",
            "التأثير والتواصل الفعّال",
            "التمكين وتحفيز الآخرين",
            "تحمل المسؤولية والمساءلة",
            "الابتكار والتحسين المستمر"
        ]
    }
}

class DynamicLeadershipAssessment:
    """Production-ready dynamic AI assessment engine with 7+7+1 format."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test API connection
        self._test_connection()
        logger.info("Dynamic Assessment Engine initialized successfully")
    
    def _test_connection(self):
        """Test API connection with retry mechanism."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                test_response = self.model.generate_content("Respond with: API_TEST_SUCCESS")
                if test_response and "API_TEST_SUCCESS" in test_response.text:
                    return True
                else:
                    raise Exception("API test response invalid")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API connection failed after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)
    
    def _make_api_call_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Make API call with retry mechanism and validation."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if not response or not response.text:
                    raise Exception("Empty response from API")
                
                logger.info(f"API call successful on attempt {attempt + 1}")
                return response.text.strip()
                
            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"API call failed after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)
    
    def _clean_and_parse_json(self, text: str) -> Dict:
        """Clean and parse JSON response with validation."""
        # Remove markdown formatting
        text = re.sub(r'```json\n?', '', text)
        text = re.sub(r'```\n?', '', text)
        text = re.sub(r'```', '', text)
        text = text.strip()
        
        try:
            parsed_data = json.loads(text)
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.error(f"Raw text: {text[:500]}...")
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    
    def generate_comprehensive_yes_no_questions(self, language: str, user_profile: Dict) -> List[Dict]:
        """Generate 7 comprehensive Yes/No/Maybe questions covering all leadership pillars."""
        
        lang_instruction = "in Arabic language only" if language == 'ar' else "in English language only"
        
        prompt = f"""
        You are an expert leadership psychologist creating a comprehensive assessment. Generate exactly 7 unique Yes/No/Maybe questions {lang_instruction} that cover all leadership competencies.

        PERSONALIZATION CONTEXT:
        - Name: {user_profile.get('name')}
        - Position: {user_profile.get('current_position')}
        - Industry: {user_profile.get('industry')}
        - Experience: {user_profile.get('experience_years')} years
        - Leadership Experience: {user_profile.get('leadership_experience')} years
        - Team Size: {user_profile.get('team_size')}
        - Company Size: {user_profile.get('company_size')}
        - Country: {user_profile.get('country')}

        LEADERSHIP PILLARS TO COVER:
        1. Strategic Thinking
        2. Leading Change & Adaptability
        3. Effective Communication & Influence
        4. Empowerment & Motivation
        5. Responsibility & Accountability
        6. Innovation & Continuous Improvement
        7. Overall Leadership Effectiveness

        REQUIREMENTS:
        1. Each question must be HIGHLY SPECIFIC to their role, industry, and experience level
        2. Questions should test different leadership competencies
        3. Reference their actual work context and challenges
        4. Use industry-specific terminology and situations
        5. Consider cultural context from their country
        6. Questions should feel personally relevant and challenging

        Return ONLY valid JSON in this exact format:
        [
            {{"question": "Highly personalized question 1", "pillar": "Strategic Thinking"}},
            {{"question": "Highly personalized question 2", "pillar": "Leading Change & Adaptability"}},
            {{"question": "Highly personalized question 3", "pillar": "Effective Communication & Influence"}},
            {{"question": "Highly personalized question 4", "pillar": "Empowerment & Motivation"}},
            {{"question": "Highly personalized question 5", "pillar": "Responsibility & Accountability"}},
            {{"question": "Highly personalized question 6", "pillar": "Innovation & Continuous Improvement"}},
            {{"question": "Highly personalized question 7", "pillar": "Overall Leadership Effectiveness"}}
        ]

        CRITICAL: All content must be {lang_instruction}. No explanations, just the JSON.
        """
        
        response_text = self._make_api_call_with_retry(prompt)
        questions = self._clean_and_parse_json(response_text)
        
        # Validate response
        if not isinstance(questions, list) or len(questions) != 7:
            raise Exception("Invalid question format - must be exactly 7 questions")
        
        for q in questions:
            if not isinstance(q, dict) or 'question' not in q or 'pillar' not in q:
                raise Exception("Invalid question structure")
        
        logger.info(f"Generated 7 comprehensive Yes/No/Maybe questions")
        return questions
    
    def generate_comprehensive_mcq_questions(self, language: str, user_profile: Dict) -> List[Dict]:
        """Generate 7 comprehensive MCQ questions covering all leadership scenarios."""
        
        lang_instruction = "in Arabic language only" if language == 'ar' else "in English language only"
        
        prompt = f"""
        Create exactly 7 multiple choice questions for comprehensive leadership assessment {lang_instruction}, completely personalized for this professional.

        PERSONALIZATION CONTEXT:
        - Name: {user_profile.get('name')}
        - Position: {user_profile.get('current_position')}
        - Industry: {user_profile.get('industry')}
        - Experience: {user_profile.get('experience_years')} years
        - Leadership Experience: {user_profile.get('leadership_experience')} years
        - Team Size: {user_profile.get('team_size')}
        - Company Size: {user_profile.get('company_size')}

        REQUIREMENTS:
        1. Each question must present a realistic scenario they would actually face in their role
        2. Options must reflect real choices they would consider
        3. Questions should test different leadership competencies comprehensively
        4. Use industry-specific language and contexts
        5. Difficulty appropriate for their experience level
        6. Cover various leadership situations: crisis, growth, team conflicts, strategic decisions, etc.

        Return ONLY valid JSON:
        [
            {{
                "question": "Personalized scenario question 1",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }},
            {{
                "question": "Personalized scenario question 2",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }},
            {{
                "question": "Personalized scenario question 3",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }},
            {{
                "question": "Personalized scenario question 4",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }},
            {{
                "question": "Personalized scenario question 5",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }},
            {{
                "question": "Personalized scenario question 6",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }},
            {{
                "question": "Personalized scenario question 7",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "pillar": "Leadership competency being tested"
            }}
        ]

        CRITICAL: All content must be {lang_instruction}.
        """
        
        response_text = self._make_api_call_with_retry(prompt)
        questions = self._clean_and_parse_json(response_text)
        
        # Validate response
        if not isinstance(questions, list) or len(questions) != 7:
            raise Exception("Invalid MCQ format - must be exactly 7 questions")
        
        for q in questions:
            required_keys = ['question', 'options', 'pillar']
            if not all(key in q for key in required_keys):
                raise Exception("Invalid MCQ structure")
            if len(q['options']) != 4:
                raise Exception("MCQ must have exactly 4 options")
        
        logger.info(f"Generated 7 comprehensive MCQ questions")
        return questions
    
    def generate_personalized_scenario(self, language: str, user_profile: Dict) -> str:
        """Generate a comprehensive personalized writing scenario."""
        
        lang_instruction = "in Arabic language only" if language == 'ar' else "in English language only"
        
        prompt = f"""
        Create one highly comprehensive, complex leadership scenario {lang_instruction} for this specific professional that requires detailed written analysis.

        PERSONALIZATION CONTEXT:
        - Name: {user_profile.get('name')}
        - Position: {user_profile.get('current_position')}
        - Industry: {user_profile.get('industry')}
        - Experience: {user_profile.get('experience_years')} years
        - Leadership Experience: {user_profile.get('leadership_experience')} years
        - Team Size: {user_profile.get('team_size')}
        - Company Size: {user_profile.get('company_size')}
        - Country: {user_profile.get('country')}

        REQUIREMENTS:
        1. Scenario must be HIGHLY SPECIFIC to their actual role and industry
        2. Include multiple realistic stakeholders, constraints, and competing priorities
        3. Test ALL leadership competencies simultaneously
        4. Reflect current industry trends and challenges
        5. Consider cultural and regional business context
        6. Require 200-300 word response to address properly
        7. Include specific metrics, timelines, budget constraints, and business outcomes
        8. Present a complex situation with no obvious "right" answer
        9. Require strategic thinking, change management, communication, team leadership, accountability, and innovation

        Return ONLY the comprehensive scenario text {lang_instruction}. No formatting, explanations, or additional text.
        """
        
        scenario = self._make_api_call_with_retry(prompt)
        
        # Validate scenario length and content
        if len(scenario) < 150:
            raise Exception("Generated scenario too short")
        
        logger.info("Generated comprehensive personalized scenario question")
        return scenario
    
    def analyze_responses_dynamically(self, responses: Dict, language: str, user_profile: Dict) -> Dict:
        """Perform comprehensive analysis based on 7+7+1 responses."""
        
        lang_instruction = "in Arabic language only" if language == 'ar' else "in English language only"
        
        # Prepare detailed response analysis
        response_analysis = ""
        for key, value in responses.items():
            response_analysis += f"\n{key}: {json.dumps(value, ensure_ascii=False)}"
        
        prompt = f"""
        Perform a comprehensive, personalized leadership analysis {lang_instruction} based on this individual's specific responses to 7 Yes/No/Maybe questions, 7 MCQ questions, and 1 writing scenario.

        INDIVIDUAL PROFILE:
        - Name: {user_profile.get('name')}
        - Position: {user_profile.get('current_position')}
        - Industry: {user_profile.get('industry')}
        - Experience: {user_profile.get('experience_years')} years
        - Leadership Experience: {user_profile.get('leadership_experience')} years
        - Team Size: {user_profile.get('team_size')}
        - Company Size: {user_profile.get('company_size')}
        - Country: {user_profile.get('country')}

        ACTUAL RESPONSES TO ANALYZE:
        {response_analysis}

        ANALYSIS REQUIREMENTS:
        1. Analyze ACTUAL response patterns across all 15 questions
        2. Scores must reflect their specific answers and demonstrate clear reasoning
        3. Identify specific behavioral patterns from their Yes/No, MCQ, and writing responses
        4. Provide insights relevant to their role and industry
        5. Consider their experience level in scoring and recommendations
        6. Reference specific responses in your analysis
        7. Weight the writing scenario more heavily in final scoring
        8. Provide evidence-based assessment with examples from their responses

        Return ONLY valid JSON {lang_instruction}:
        {{
            "overall_score": [calculated from actual responses with clear reasoning],
            "pillar_scores": {{
                "Strategic Thinking": [score based on responses with evidence],
                "Leading Change & Adaptability": [score based on responses with evidence],
                "Effective Communication & Influence": [score based on responses with evidence],
                "Empowerment & Motivation": [score based on responses with evidence],
                "Responsibility & Accountability": [score based on responses with evidence],
                "Innovation & Continuous Improvement": [score based on responses with evidence]
            }},
            "leadership_level": "[based on scores and experience]",
            "strengths": ["specific strengths from actual responses with examples"],
            "development_areas": ["specific areas from actual responses with examples"],
            "detailed_analysis": "comprehensive analysis referencing actual responses and patterns",
            "personalized_recommendations": ["specific recommendations based on their responses and role"],
            "development_plan": {{
                "30_day_goals": ["specific 30-day actions based on their responses"],
                "90_day_goals": ["specific 90-day actions based on their responses"],
                "6_month_goals": ["specific 6-month actions based on their responses"]
            }},
            "response_insights": {{
                "yes_no_patterns": "analysis of their Yes/No/Maybe response patterns",
                "mcq_patterns": "analysis of their MCQ choice patterns",
                "writing_quality": "analysis of their writing scenario response quality and depth"
            }}
        }}

        CRITICAL: Base everything on their ACTUAL responses with specific examples. All content must be {lang_instruction}.
        """
        
        response_text = self._make_api_call_with_retry(prompt)
        analysis = self._clean_and_parse_json(response_text)
        
        # Validate analysis structure
        required_keys = ['overall_score', 'pillar_scores', 'leadership_level', 'strengths', 
                        'development_areas', 'detailed_analysis', 'personalized_recommendations', 
                        'development_plan', 'response_insights']
        if not all(key in analysis for key in required_keys):
            raise Exception("Invalid analysis structure")
        
        # Validate scores
        if not (1.0 <= analysis['overall_score'] <= 10.0):
            raise Exception("Invalid overall score")
        
        for pillar, score in analysis['pillar_scores'].items():
            if not (1.0 <= score <= 10.0):
                raise Exception(f"Invalid score for {pillar}")
        
        logger.info("Generated comprehensive personalized analysis based on 7+7+1 responses")
        return analysis

# Session state management
def initialize_session_state():
    """Initialize session state for production use."""
    defaults = {
        'language': 'en',
        'assessment_phase': 'setup',
        'user_profile': {},
        'yes_no_questions': [],
        'mcq_questions': [],
        'scenario_question': "",
        'responses': {},
        'final_analysis': {},
        'assessment_engine': None,
        'start_time': None,
        'current_question_index': 0
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def check_api_connection():
    """Check and initialize API connection."""
    try:
        if st.session_state.assessment_engine is None:
            with st.spinner("Initializing AI Assessment Engine..."):
                st.session_state.assessment_engine = DynamicLeadershipAssessment()
        return True
    except Exception as e:
        st.error(f"Failed to initialize assessment engine: {str(e)}")
        logger.error(f"API initialization failed: {str(e)}")
        return False

def display_language_selector():
    """Display language selector."""
    with st.sidebar:
        language = st.selectbox(
            CONTENT[st.session_state.language]['language_label'],
            ['English', 'العربية'],
            index=0 if st.session_state.language == 'en' else 1
        )
        
        if language == 'العربية' and st.session_state.language != 'ar':
            st.session_state.language = 'ar'
            st.rerun()
        elif language == 'English' and st.session_state.language != 'en':
            st.session_state.language = 'en'
            st.rerun()

def display_welcome():
    """Display welcome screen."""
    lang = st.session_state.language
    content = CONTENT[lang]
    
    st.title(content['title'])
    st.subheader(content['subtitle'])
    
    if lang == 'ar':
        st.markdown("""
        ### 🚀 نظام تقييم قيادي ديناميكي شامل
        
        **هيكل التقييم:**
        - **7 أسئلة نعم/لا/ربما**: تغطي جميع أركان القيادة
        - **7 أسئلة متعددة الخيارات**: سيناريوهات قيادية متنوعة
        - **1 سيناريو كتابي**: تحليل قيادي شامل ومعمق
        
        **المميزات:**
        - لا توجد أسئلة محددة مسبقاً
        - تحليل شخصي مبني على إجاباتك الفعلية
        - خطة تطوير مخصصة لدورك ومجالك
        - رؤى عميقة لأنماط قيادتك
        
        ✅ **محرك الذكاء الاصطناعي جاهز للتقييم الشامل**
        """)
    else:
        st.markdown("""
        ### 🚀 Comprehensive Dynamic Leadership Assessment System
        
        **Assessment Structure:**
        - **7 Yes/No/Maybe Questions**: Covering all leadership pillars
        - **7 Multiple Choice Questions**: Diverse leadership scenarios
        - **1 Writing Scenario**: Comprehensive leadership analysis
        
        **Features:**
        - No Predefined Questions
        - Personalized Analysis based on actual responses
        - Custom Development Plan for your role and industry
        - Deep Insights into your leadership patterns
        
        ✅ **AI Engine Ready for Comprehensive Assessment**
        """)
    
    st.success("🤖 Dynamic AI Assessment (7+7+1): Ready" if lang == 'en' else "🤖 التقييم الذكي الديناميكي (7+7+1): جاهز")
    
    if st.button(content['begin_assessment'], type="primary", use_container_width=True):
        st.session_state.assessment_phase = 'profile'
        st.session_state.start_time = datetime.now()
        st.rerun()

def display_user_profile():
    """Display comprehensive user profile form."""
    lang = st.session_state.language
    content = CONTENT[lang]
    
    st.title(content['profile_title'])
    st.markdown(content['profile_desc'])
    
    with st.form("dynamic_profile_form"):
        col1, col2 = st.columns(2)
        
        # Dynamic industry options
        industry_options = {
            'en': ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", 
                   "Retail", "Consulting", "Government", "Non-profit", "Energy", 
                   "Telecommunications", "Media", "Real Estate", "Other"],
            'ar': ["التكنولوجيا", "الرعاية الصحية", "المالية", "التعليم", "التصنيع",
                   "التجارة", "الاستشارات", "الحكومة", "غير ربحي", "الطاقة",
                   "الاتصالات", "الإعلام", "العقارات", "أخرى"]
        }
        
        with col1:
            name = st.text_input("Full Name *" if lang == 'en' else "الاسم الكامل *")
            age = st.number_input("Age *" if lang == 'en' else "العمر *", min_value=18, max_value=80, value=30)
            experience_years = st.number_input("Years of Experience *" if lang == 'en' else "سنوات الخبرة *", min_value=0, max_value=50, value=5)
            current_position = st.text_input("Current Position *" if lang == 'en' else "المنصب الحالي *")
            industry = st.selectbox("Industry *" if lang == 'en' else "الصناعة *", industry_options[lang])
            
        with col2:
            country = st.text_input("Country *" if lang == 'en' else "البلد *")
            team_size = st.selectbox(
                "Team Size" if lang == 'en' else "حجم الفريق",
                ["No direct reports", "1-5", "6-15", "16-50", "50+"] if lang == 'en' else 
                ["لا يوجد مرؤوسين", "1-5", "6-15", "16-50", "أكثر من 50"]
            )
            leadership_experience = st.number_input("Leadership Experience (years)" if lang == 'en' else "الخبرة القيادية (سنوات)", min_value=0, max_value=40, value=2)
            company_size = st.selectbox(
                "Company Size" if lang == 'en' else "حجم الشركة",
                ["Startup (1-50)", "Small (51-200)", "Medium (201-1000)", "Large (1001-5000)", "Enterprise (5000+)"] if lang == 'en' else
                ["ناشئة (1-50)", "صغيرة (51-200)", "متوسطة (201-1000)", "كبيرة (1001-5000)", "مؤسسة (5000+)"]
            )
            education = st.selectbox(
                "Education Level" if lang == 'en' else "المستوى التعليمي",
                ["High School", "Bachelor's", "Master's", "PhD", "Professional Cert"] if lang == 'en' else
                ["ثانوية", "بكالوريوس", "ماجستير", "دكتوراه", "شهادة مهنية"]
            )
        
        # Additional context for personalization
        st.markdown("### " + ("Additional Context" if lang == 'en' else "سياق إضافي"))
        current_challenges = st.text_area(
            "Current leadership challenges you face:" if lang == 'en' else "التحديات القيادية الحالية التي تواجهها:",
            placeholder="Describe specific challenges in your role..." if lang == 'en' else "صف التحديات المحددة في دورك..."
        )
        
        submitted = st.form_submit_button(
            "Generate 7+7+1 Assessment" if lang == 'en' else "إنشاء التقييم 7+7+1",
            type="primary", use_container_width=True
        )
        
        if submitted:
            required_fields = [name, current_position, industry, country]
            if not all(required_fields):
                st.error("Please fill all required fields" if lang == 'en' else "يرجى ملء جميع الحقول المطلوبة")
            else:
                st.session_state.user_profile = {
                    "name": name, "age": age, "experience_years": experience_years,
                    "current_position": current_position, "industry": industry, "country": country,
                    "team_size": team_size, "leadership_experience": leadership_experience,
                    "company_size": company_size, "education": education,
                    "current_challenges": current_challenges
                }
                st.session_state.assessment_phase = 'yes_no'
                st.success("Profile saved! Generating 7 personalized Yes/No questions..." if lang == 'en' else "تم حفظ الملف الشخصي! جاري إنشاء 7 أسئلة نعم/لا شخصية...")
                st.rerun()

def display_yes_no_assessment():
    """Display 7 Yes/No/Maybe questions."""
    lang = st.session_state.language
    content = CONTENT[lang]
    
    st.header("📋 Part 1: Yes/No/Maybe Questions (7 Questions)" if lang == 'en' else "📋 الجزء الأول: أسئلة نعم/لا/ربما (7 أسئلة)")
    st.info("Comprehensive questions covering all leadership competencies" if lang == 'en' else "أسئلة شاملة تغطي جميع الكفاءات القيادية")
    
    # Generate 7 comprehensive questions
    if not st.session_state.yes_no_questions:
        with st.spinner("🤖 AI is creating 7 personalized Yes/No questions..." if lang == 'en' else "🤖 الذكاء الاصطناعي ينشئ 7 أسئلة نعم/لا شخصية..."):
            try:
                questions = st.session_state.assessment_engine.generate_comprehensive_yes_no_questions(
                    lang, st.session_state.user_profile
                )
                st.session_state.yes_no_questions = questions
                st.success("✨ 7 personalized questions generated!" if lang == 'en' else "✨ تم إنشاء 7 أسئلة شخصية!")
            except Exception as e:
                st.error(f"Failed to generate questions: {str(e)}")
                return
    
    # Display all 7 questions
    yes_no_responses = st.session_state.responses.get('yes_no', {})
    
    for i, q in enumerate(st.session_state.yes_no_questions):
        st.markdown(f"**{i+1}. {q['question']}**")
        st.caption(f"Testing: {q['pillar']}")
        
        response = st.radio(
            "Your answer:" if lang == 'en' else "إجابتك:",
            [content['yes'], content['no'], content['maybe']],
            key=f"yn_{i}",
            index=0 if f'q{i}' not in yes_no_responses else [content['yes'], content['no'], content['maybe']].index(yes_no_responses[f'q{i}'])
        )
        yes_no_responses[f'q{i}'] = response
        st.markdown("---")
    
    st.session_state.responses['yes_no'] = yes_no_responses
    
    # Progress indicator
    st.progress(1/3, text="Progress: Part 1 of 3 completed" if lang == 'en' else "التقدم: الجزء 1 من 3 مكتمل")
    
    # Navigation
    if st.button("Continue to Multiple Choice Questions (7 Questions)" if lang == 'en' else "المتابعة للأسئلة متعددة الخيارات (7 أسئلة)", type="primary", use_container_width=True):
        st.session_state.assessment_phase = 'mcq'
        st.rerun()

def display_mcq_assessment():
    """Display 7 MCQ questions."""
    lang = st.session_state.language
    
    st.header("📋 Part 2: Multiple Choice Questions (7 Questions)" if lang == 'en' else "📋 الجزء الثاني: أسئلة متعددة الخيارات (7 أسئلة)")
    st.info("Complex scenarios tailored to your role and industry" if lang == 'en' else "سيناريوهات معقدة مصممة لدورك ومجالك")
    
    # Generate 7 comprehensive MCQ questions
    if not st.session_state.mcq_questions:
        with st.spinner("🤖 Creating 7 personalized scenario questions..." if lang == 'en' else "🤖 إنشاء 7 أسئلة سيناريو شخصية..."):
            try:
                mcq_questions = st.session_state.assessment_engine.generate_comprehensive_mcq_questions(
                    lang, st.session_state.user_profile
                )
                st.session_state.mcq_questions = mcq_questions
                st.success("✨ 7 personalized scenarios ready!" if lang == 'en' else "✨ 7 سيناريوهات شخصية جاهزة!")
            except Exception as e:
                st.error(f"Failed to generate MCQ questions: {str(e)}")
                return
    
    # Display all 7 MCQ questions
    mcq_responses = st.session_state.responses.get('mcq', {})
    
    for i, q in enumerate(st.session_state.mcq_questions):
        st.markdown(f"**{i+1}. {q['question']}**")
        st.caption(f"Testing: {q['pillar']}")
        
        response = st.radio(
            "Select your approach:" if lang == 'en' else "اختر نهجك:",
            q['options'],
            key=f"mcq_{i}",
            index=0 if f'q{i}' not in mcq_responses else q['options'].index(mcq_responses[f'q{i}'])
        )
        mcq_responses[f'q{i}'] = response
        st.markdown("---")
    
    st.session_state.responses['mcq'] = mcq_responses
    
    # Progress indicator
    st.progress(2/3, text="Progress: Part 2 of 3 completed" if lang == 'en' else "التقدم: الجزء 2 من 3 مكتمل")
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Yes/No Questions" if lang == 'en' else "⬅️ العودة لأسئلة نعم/لا", use_container_width=True):
            st.session_state.assessment_phase = 'yes_no'
            st.rerun()
    
    with col2:
        if st.button("Continue to Writing Scenario (1 Question)" if lang == 'en' else "المتابعة لسيناريو الكتابة (سؤال واحد)", type="primary", use_container_width=True):
            st.session_state.assessment_phase = 'scenario'
            st.rerun()

def display_scenario_assessment():
    """Display 1 comprehensive writing scenario."""
    lang = st.session_state.language
    
    st.header("📝 Part 3: Leadership Writing Scenario (1 Question)" if lang == 'en' else "📝 الجزء الثالث: سيناريو القيادة الكتابي (سؤال واحد)")
    st.info("A comprehensive scenario requiring detailed leadership analysis" if lang == 'en' else "سيناريو شامل يتطلب تحليل قيادي مفصل")
    
    # Generate comprehensive scenario
    if not st.session_state.scenario_question:
        with st.spinner("🤖 Creating your comprehensive leadership scenario..." if lang == 'en' else "🤖 إنشاء سيناريو القيادة الشامل..."):
            try:
                scenario = st.session_state.assessment_engine.generate_personalized_scenario(
                    lang, st.session_state.user_profile
                )
                st.session_state.scenario_question = scenario
                st.success("✨ Your comprehensive scenario is ready!" if lang == 'en' else "✨ سيناريوك الشامل جاهز!")
            except Exception as e:
                st.error(f"Failed to generate scenario: {str(e)}")
                return
    
    # Display scenario
    st.markdown("### Your Leadership Challenge:" if lang == 'en' else "### تحديك القيادي:")
    st.info(st.session_state.scenario_question)
    
    # Response input
    response = st.text_area(
        "Your comprehensive response (200-300 words recommended):" if lang == 'en' else "إجابتك الشاملة (يُنصح بـ 200-300 كلمة):",
        value=st.session_state.responses.get('scenario', ''),
        height=300,
        placeholder="Provide a detailed leadership analysis including: your approach, specific actions, stakeholder management, risk mitigation, timeline, and expected outcomes..." if lang == 'en' else "قدم تحليل قيادي مفصل يشمل: نهجك، الإجراءات المحددة، إدارة أصحاب المصلحة، تخفيف المخاطر، الجدول الزمني، والنتائج المتوقعة..."
    )
    
    st.session_state.responses['scenario'] = response
    
    # Word count and guidance
    word_count = len(response.split()) if response else 0
    if word_count < 100:
        st.warning(f"Word count: {word_count}. Add more detail for comprehensive analysis." if lang == 'en' else f"عدد الكلمات: {word_count}. أضف المزيد من التفاصيل للتحليل الشامل.")
    elif word_count < 200:
        st.info(f"Word count: {word_count}. Good progress - consider adding more depth." if lang == 'en' else f"عدد الكلمات: {word_count}. تقدم جيد - فكر في إضافة المزيد من العمق.")
    else:
        st.success(f"Word count: {word_count} ✓ Excellent comprehensive response!" if lang == 'en' else f"عدد الكلمات: {word_count} ✓ إجابة شاملة ممتازة!")
    
    # Progress indicator
    st.progress(3/3, text="Progress: All 3 parts ready for analysis" if lang == 'en' else "التقدم: جميع الأجزاء الثلاثة جاهزة للتحليل")
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Multiple Choice" if lang == 'en' else "⬅️ العودة للأسئلة متعددة الخيارات", use_container_width=True):
            st.session_state.assessment_phase = 'mcq'
            st.rerun()
    
    with col2:
        if st.button("🎯 Generate Comprehensive Analysis" if lang == 'en' else "🎯 إنشاء التحليل الشامل", type="primary", use_container_width=True):
            if len(response.strip()) < 100:
                st.error("Please provide a more comprehensive response (at least 100 words)." if lang == 'en' else "يرجى تقديم إجابة أكثر شمولية (100 كلمة على الأقل).")
            else:
                # Generate comprehensive analysis
                with st.spinner("🧠 AI is analyzing all 15 responses (7+7+1) and creating your comprehensive report..." if lang == 'en' else "🧠 الذكاء الاصطناعي يحلل جميع الإجابات الـ15 (7+7+1) وينشئ تقريرك الشامل..."):
                    try:
                        analysis = st.session_state.assessment_engine.analyze_responses_dynamically(
                            st.session_state.responses, lang, st.session_state.user_profile
                        )
                        st.session_state.final_analysis = analysis
                        st.session_state.assessment_phase = 'complete'
                        st.success("🎉 Your comprehensive analysis is complete!" if lang == 'en' else "🎉 تحليلك الشامل مكتمل!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate analysis: {str(e)}")

def display_comprehensive_report():
    """Display the comprehensive 7+7+1 analysis report."""
    lang = st.session_state.language
    content = CONTENT[lang]
    analysis = st.session_state.final_analysis
    
    st.title(content['report_title'])
    
    # Report header with comprehensive details
    completion_time = datetime.now()
    duration = completion_time - st.session_state.start_time if st.session_state.start_time else None
    
    st.markdown(f"""
    **{st.session_state.user_profile['name']}** | **{st.session_state.user_profile['current_position']}**  
    **{st.session_state.user_profile['industry']}** | **{st.session_state.user_profile['country']}**  
    **Assessment Format:** 7 Yes/No/Maybe + 7 MCQ + 1 Writing Scenario  
    **Generated:** {completion_time.strftime('%B %d, %Y at %I:%M %p')}  
    **Duration:** {duration.seconds // 60} minutes  
    **Language:** {'Arabic' if lang == 'ar' else 'English'}
    
    ---
    """)
    
    # Comprehensive metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(content['overall_score'], f"{analysis['overall_score']:.1f}/10")
    with col2:
        st.metric("Leadership Level" if lang == 'en' else "مستوى القيادة", analysis['leadership_level'])
    with col3:
        st.metric("Total Questions" if lang == 'en' else "إجمالي الأسئلة", "15 (7+7+1)")
    with col4:
        scenario_words = len(st.session_state.responses.get('scenario', '').split())
        st.metric("Writing Response" if lang == 'en' else "الإجابة الكتابية", f"{scenario_words} words" if lang == 'en' else f"{scenario_words} كلمة")
    
    # Comprehensive radar chart
    st.subheader("🎯 Your Leadership Profile" if lang == 'en' else "🎯 ملفك القيادي")
    
    pillar_scores = [analysis['pillar_scores'].get(pillar, 5.0) for pillar in content['pillars']]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=pillar_scores,
        theta=content['pillars'],
        fill='toself',
        name=f"{st.session_state.user_profile['name']}'s Profile",
        line_color='rgb(0, 123, 255)',
        fillcolor='rgba(0, 123, 255, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                tickmode='array'
            )
        ),
        showlegend=True,
        title=f"Comprehensive Leadership Assessment (7+7+1) - {st.session_state.user_profile['name']}",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analysis sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌟 Your Strengths" if lang == 'en' else "🌟 نقاط قوتك")
        for strength in analysis['strengths']:
            st.success(f"-  {strength}")
    
    with col2:
        st.subheader("📈 Development Opportunities" if lang == 'en' else "📈 فرص التطوير")
        for area in analysis['development_areas']:
            st.warning(f"-  {area}")
    
    # Comprehensive analysis
    st.subheader("🔍 Comprehensive Analysis" if lang == 'en' else "🔍 التحليل الشامل")
    st.write(analysis['detailed_analysis'])
    
    # Response pattern insights
    if 'response_insights' in analysis:
        st.subheader("📊 Response Pattern Analysis" if lang == 'en' else "📊 تحليل أنماط الإجابات")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.markdown("**Yes/No/Maybe Patterns**" if lang == 'en' else "**أنماط نعم/لا/ربما**")
            st.write(analysis['response_insights']['yes_no_patterns'])
        
        with insight_col2:
            st.markdown("**MCQ Choice Patterns**" if lang == 'en' else "**أنماط الاختيارات متعددة الخيارات**")
            st.write(analysis['response_insights']['mcq_patterns'])
        
        with insight_col3:
            st.markdown("**Writing Quality Analysis**" if lang == 'en' else "**تحليل جودة الكتابة**")
            st.write(analysis['response_insights']['writing_quality'])
    
    # Personalized recommendations
    st.subheader("💡 Your Personalized Recommendations" if lang == 'en' else "💡 توصياتك الشخصية")
    for i, rec in enumerate(analysis['personalized_recommendations'], 1):
        st.markdown(f"**{i}.** {rec}")
    
    # Comprehensive development plan
    st.subheader("📅 Your Personal Development Plan" if lang == 'en' else "📅 خطة التطوير الشخصية")
    
    plan_col1, plan_col2, plan_col3 = st.columns(3)
    
    with plan_col1:
        st.markdown("**30-Day Goals**" if lang == 'en' else "**أهداف 30 يوم**")
        for goal in analysis['development_plan']['30_day_goals']:
            st.write(f"-  {goal}")
    
    with plan_col2:
        st.markdown("**90-Day Goals**" if lang == 'en' else "**أهداف 90 يوم**")
        for goal in analysis['development_plan']['90_day_goals']:
            st.write(f"-  {goal}")
    
    with plan_col3:
        st.markdown("**6-Month Goals**" if lang == 'en' else "**أهداف 6 أشهر**")
        for goal in analysis['development_plan']['6_month_goals']:
            st.write(f"-  {goal}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(content['download_report'], use_container_width=True):
            report_content = f"""
# Comprehensive Leadership Assessment Report (7+7+1)
## {st.session_state.user_profile['name']}

**Position:** {st.session_state.user_profile['current_position']}
**Industry:** {st.session_state.user_profile['industry']}
**Assessment Format:** 7 Yes/No/Maybe + 7 MCQ + 1 Writing Scenario
**Generated:** {completion_time.strftime('%B %d, %Y at %I:%M %p')}

## Comprehensive Analysis Results
{json.dumps(analysis, indent=2, ensure_ascii=False)}

## User Profile
{json.dumps(st.session_state.user_profile, indent=2, ensure_ascii=False)}

## Complete Responses (15 Questions)
{json.dumps(st.session_state.responses, indent=2, ensure_ascii=False)}
            """
            st.download_button(
                label="Download Complete Report" if lang == 'en' else "تحميل التقرير الكامل",
                data=report_content,
                file_name=f"comprehensive_leadership_assessment_{st.session_state.user_profile['name'].replace(' ', '_')}_{completion_time.strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button(content['new_assessment'], use_container_width=True):
            # Keep engine but reset everything else
            engine = st.session_state.assessment_engine
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.session_state.assessment_engine = engine
            st.rerun()
    
    with col3:
        if st.button("📊 Assessment Analytics" if lang == 'en' else "📊 تحليلات التقييم", use_container_width=True):
            st.info("Advanced analytics coming soon" if lang == 'en' else "التحليلات المتقدمة قادمة قريباً")

def main():
    """Main application controller for comprehensive 7+7+1 assessment."""
    initialize_session_state()
    display_language_selector()
    
    # Check API connection
    if not check_api_connection():
        st.error("Failed to initialize AI Assessment Engine. Please check your API configuration.")
        return
    
    # Main application flow
    try:
        if st.session_state.assessment_phase == 'setup':
            display_welcome()
        elif st.session_state.assessment_phase == 'profile':
            display_user_profile()
        elif st.session_state.assessment_phase == 'yes_no':
            display_yes_no_assessment()
        elif st.session_state.assessment_phase == 'mcq':
            display_mcq_assessment()
        elif st.session_state.assessment_phase == 'scenario':
            display_scenario_assessment()
        elif st.session_state.assessment_phase == 'complete':
            display_comprehensive_report()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == '__main__':
    main()
