"""
Fully Dynamic AI Leadership Assessment Engine
Production-ready system with 100% AI-generated content
7 Yes/No/Maybe + 7 MCQ + 1 Writing Scenario
Enhanced with Multiple Arabic PDF Solutions
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
import io
import base64

# PDF generation imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        'download_report': "📄 Download PDF Report",
        'view_printable': "📄 View Printable Report",
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
        'subtitle': "تقييم قيادي شخصي بالكامل - نموذج 7+7+1",
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
        'download_report': "📄 تحميل تقرير PDF",
        'view_printable': "📄 عرض التقرير للطباعة",
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

class ArabicFontPDFGenerator:
    """Enhanced PDF generator with Arabic font support."""
    
    def __init__(self, language='en'):
        self.language = language
        self.story = []
        self.styles = getSampleStyleSheet()
        self.arabic_font = self._register_arabic_font()
        self._setup_styles()
    
    def _register_arabic_font(self):
        """Register Arabic-compatible fonts."""
        try:
            # Try to register system fonts that support Arabic
            font_paths = [
                'C:/Windows/Fonts/arial.ttf',  # Windows
                'C:/Windows/Fonts/calibri.ttf',
                'C:/Windows/Fonts/tahoma.ttf',
                '/System/Library/Fonts/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                '/usr/share/fonts/TTF/arial.ttf'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                        return 'ArabicFont'
                    except:
                        continue
        except Exception as e:
            logger.warning(f"Font registration failed: {e}")
        
        return 'Helvetica'  # Fallback
    
    def _setup_styles(self):
        """Setup styles with Arabic font support."""
        if self.language == 'ar':
            self.title_style = ParagraphStyle(
                'ArabicTitle',
                parent=self.styles['Title'],
                fontSize=18,
                alignment=TA_CENTER,
                fontName=self.arabic_font,
                spaceAfter=20,
                textColor=colors.darkblue
            )
            
            self.heading_style = ParagraphStyle(
                'ArabicHeading',
                parent=self.styles['Heading1'],
                fontSize=14,
                alignment=TA_RIGHT,
                fontName=self.arabic_font,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            self.normal_style = ParagraphStyle(
                'ArabicNormal',
                parent=self.styles['Normal'],
                fontSize=11,
                alignment=TA_RIGHT,
                fontName=self.arabic_font,
                spaceAfter=8
            )
        else:
            self.title_style = self.styles['Title']
            self.heading_style = self.styles['Heading1']
            self.normal_style = self.styles['Normal']
    
    def clean_arabic_text(self, text):
        """Clean Arabic text for PDF rendering."""
        if not text:
            return ""
        
        text = str(text)
        # Remove black squares and problematic characters
        text = text.replace('■', '').replace('□', '').replace('▪', '')
        
        # For Arabic text, try to preserve as much as possible
        if self.language == 'ar':
            try:
                # Try to process Arabic text
                import arabic_reshaper
                from bidi.algorithm import get_display
                
                reshaped_text = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped_text)
                return bidi_text
            except:
                # If processing fails, return cleaned text
                return text
        
        return text
    
    def add_title(self, title):
        """Add title with proper Arabic support."""
        clean_title = self.clean_arabic_text(title)
        title_para = Paragraph(clean_title, self.title_style)
        self.story.append(title_para)
        self.story.append(Spacer(1, 20))
    
    def add_section(self, heading, content):
        """Add section with Arabic support."""
        clean_heading = self.clean_arabic_text(heading)
        heading_para = Paragraph(clean_heading, self.heading_style)
        self.story.append(heading_para)
        
        if isinstance(content, list):
            for item in content:
                clean_item = self.clean_arabic_text(item)
                para = Paragraph(f"• {clean_item}", self.normal_style)
                self.story.append(para)
        else:
            clean_content = self.clean_arabic_text(content)
            para = Paragraph(clean_content, self.normal_style)
            self.story.append(para)
        
        self.story.append(Spacer(1, 15))
    
    def generate_pdf(self):
        """Generate PDF with Arabic support."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50)
        doc.build(self.story)
        buffer.seek(0)
        return buffer.getvalue()

class HTMLReportGenerator:
    """Generate HTML reports for browser-based PDF printing."""
    
    def __init__(self, language='en'):
        self.language = language
    
    def generate_html_report(self, report_data: Dict, user_profile: Dict) -> str:
        """Generate complete HTML report for printing."""
        
        if self.language == 'ar':
            html_content = f'''
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>تقرير تقييم القيادة الشخصي</title>
                <style>
                    @page {{
                        size: A4;
                        margin: 2cm;
                        @bottom-center {{
                            content: "صفحة " counter(page);
                            font-size: 10px;
                        }}
                    }}
                    
                    body {{
                        font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
                        font-size: 12px;
                        line-height: 1.8;
                        color: #333;
                        direction: rtl;
                        text-align: right;
                        margin: 0;
                        padding: 20px;
                    }}
                    
                    .header {{
                        text-align: center;
                        border-bottom: 3px solid #2c5aa0;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }}
                    
                    .title {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c5aa0;
                        margin-bottom: 10px;
                    }}
                    
                    .user-info {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 25px;
                        border-right: 4px solid #2c5aa0;
                    }}
                    
                    .section-title {{
                        font-size: 18px;
                        font-weight: bold;
                        color: #2c5aa0;
                        border-bottom: 2px solid #2c5aa0;
                        padding-bottom: 8px;
                        margin-top: 30px;
                        margin-bottom: 15px;
                    }}
                    
                    .pillar-section {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-radius: 5px;
                        border-right: 4px solid #2c5aa0;
                    }}
                    
                    .pillar-title {{
                        font-size: 16px;
                        font-weight: bold;
                        color: #2c5aa0;
                        margin-bottom: 10px;
                    }}
                    
                    .score {{
                        background-color: #2c5aa0;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 15px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 5px 0;
                    }}
                    
                    .recommendation {{
                        background-color: #e7f3ff;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        border-right: 3px solid #2c5aa0;
                    }}
                    
                    .goal-section {{
                        margin-bottom: 20px;
                    }}
                    
                    .goal-title {{
                        font-size: 14px;
                        font-weight: bold;
                        color: #2c5aa0;
                        margin-bottom: 10px;
                    }}
                    
                    .no-print {{
                        display: block;
                    }}
                    
                    @media print {{
                        .no-print {{
                            display: none !important;
                        }}
                        body {{
                            margin: 0;
                            padding: 0;
                        }}
                    }}
                    
                    .print-button {{
                        background-color: #2c5aa0;
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 5px;
                        font-size: 16px;
                        cursor: pointer;
                        margin: 20px 0;
                        display: block;
                        margin-right: auto;
                        margin-left: auto;
                    }}
                    
                    .print-button:hover {{
                        background-color: #1e3a6f;
                    }}
                    
                    ul {{
                        padding-right: 20px;
                    }}
                    
                    li {{
                        margin-bottom: 8px;
                    }}
                </style>
            </head>
            <body>
                <div class="no-print">
                    <button class="print-button" onclick="window.print()">🖨️ طباعة التقرير كـ PDF</button>
                    <p style="text-align: center; color: #666;">استخدم Ctrl+P أو اضغط على الزر أعلاه لطباعة التقرير</p>
                </div>
                
                <div class="header">
                    <div class="title">تقرير تقييم القيادة الشخصي</div>
                    <p>تقييم شامل للمهارات القيادية باستخدام الذكاء الاصطناعي</p>
                </div>
                
                <div class="user-info">
                    <h3>معلومات المتقدم</h3>
                    <p><strong>الاسم:</strong> {user_profile.get('name', 'غير متوفر')}</p>
                    <p><strong>المنصب:</strong> {user_profile.get('current_position', 'غير متوفر')}</p>
                    <p><strong>الصناعة:</strong> {user_profile.get('industry', 'غير متوفر')}</p>
                    <p><strong>سنوات الخبرة:</strong> {user_profile.get('experience_years', 'غير متوفر')} سنة</p>
                    <p><strong>تاريخ الإنشاء:</strong> {datetime.now().strftime('%Y/%m/%d')}</p>
                </div>
                
                <div class="section-title">الملخص التنفيذي</div>
                <p>{report_data.get('executive_summary', 'الملخص التنفيذي غير متوفر.')}</p>
                
                <div class="section-title">النتيجة الإجمالية للقيادة</div>
                <p><span class="score">{report_data.get('overall_leadership_score', {}).get('score', 0):.1f}/10</span></p>
                <p>{report_data.get('overall_leadership_score', {}).get('justification', 'المبرر غير متوفر.')}</p>
                
                <div class="section-title">تفصيل الملف القيادي</div>
            '''
            
            # Add pillar sections
            profile_breakdown = report_data.get('leadership_profile_breakdown', {})
            arabic_pillars = [
                "التفكير الاستراتيجي",
                "قيادة التغيير والتكيف",
                "التأثير والتواصل الفعّال",
                "التمكين وتحفيز الآخرين",
                "تحمل المسؤولية والمساءلة",
                "الابتكار والتحسين المستمر"
            ]
            
            for pillar in arabic_pillars:
                pillar_data = profile_breakdown.get(pillar, {})
                if pillar_data:
                    score = pillar_data.get('score', 0)
                    analysis = pillar_data.get('analysis', 'التحليل غير متوفر.')
                    html_content += f'''
                    <div class="pillar-section">
                        <div class="pillar-title">{pillar} <span class="score">{score}/10</span></div>
                        <p>{analysis}</p>
                    </div>
                    '''
            
            # Add other sections
            html_content += f'''
                <div class="section-title">نقاط القوة</div>
                <p>{report_data.get('overall_strengths', 'تحليل نقاط القوة غير متوفر.')}</p>
                
                <div class="section-title">مجالات التطوير</div>
                <p>{report_data.get('overall_development_areas', 'تحليل مجالات التطوير غير متوفر.')}</p>
                
                <div class="section-title">التوصيات الشخصية</div>
            '''
            
            # Add recommendations
            recommendations = report_data.get('personalized_recommendations', [])
            for i, rec in enumerate(recommendations, 1):
                html_content += f'<div class="recommendation">{i}. {rec}</div>'
            
            html_content += '''
                <div class="section-title">خطة التطوير الشخصية</div>
            '''
            
            # Add development plan
            dev_plan = report_data.get('personal_development_plan', {})
            if dev_plan:
                html_content += '''
                <div class="goal-section">
                    <div class="goal-title">أهداف 30 يوم</div>
                    <ul>
                '''
                for goal in dev_plan.get('30_day_goals', []):
                    html_content += f'<li>{goal}</li>'
                html_content += '</ul></div>'
                
                html_content += '''
                <div class="goal-section">
                    <div class="goal-title">أهداف 90 يوم</div>
                    <ul>
                '''
                for goal in dev_plan.get('90_day_goals', []):
                    html_content += f'<li>{goal}</li>'
                html_content += '</ul></div>'
                
                html_content += '''
                <div class="goal-section">
                    <div class="goal-title">أهداف 6 أشهر</div>
                    <ul>
                '''
                for goal in dev_plan.get('6_month_goals', []):
                    html_content += f'<li>{goal}</li>'
                html_content += '</ul></div>'
            
            # Add closing remarks
            closing = report_data.get('closing_remarks')
            if closing:
                html_content += f'''
                <div class="section-title">ملاحظات ختامية</div>
                <p>{closing}</p>
                '''
            
            html_content += '''
                <div class="no-print">
                    <button class="print-button" onclick="window.print()">🖨️ طباعة التقرير كـ PDF</button>
                </div>
            </body>
            </html>
            '''
            
        else:
            # English HTML template (similar structure but left-aligned)
            html_content = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Leadership Assessment Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .title {{ font-size: 24px; font-weight: bold; text-align: center; color: #2c5aa0; }}
                    .section {{ margin: 20px 0; }}
                    .print-button {{ background: #2c5aa0; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
                    @media print {{ .no-print {{ display: none; }} }}
                </style>
            </head>
            <body>
                <div class="no-print">
                    <button class="print-button" onclick="window.print()">🖨️ Print as PDF</button>
                </div>
                <div class="title">Personal Leadership Assessment Report</div>
                <div class="section">
                    <h3>User Information</h3>
                    <p><strong>Name:</strong> {user_profile.get('name', 'N/A')}</p>
                    <p><strong>Position:</strong> {user_profile.get('current_position', 'N/A')}</p>
                    <!-- Add other English content -->
                </div>
            </body>
            </html>
            '''
        
        return html_content

class DynamicLeadershipAssessment:
    """Production-ready dynamic AI assessment engine with multiple Arabic PDF solutions."""
    
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
        text = re.sub(r'json\n?', '', text)
        text = re.sub(r'```\n?', '', text)
        text = re.sub(r'', '', text)
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
    
    def generate_comprehensive_detailed_report(self, responses: Dict, language: str, user_profile: Dict) -> Dict:
        """Generate comprehensive detailed report based on all responses using the enhanced prompt."""
        
        lang_instruction = "English" if language == 'en' else "Arabic"
        
        # Prepare detailed response analysis
        response_analysis = ""
        for key, value in responses.items():
            response_analysis += f"\n{key}: {json.dumps(value, ensure_ascii=False)}"
        
        prompt = f"""
        Role: You are a highly experienced and meticulous Senior Leadership Consultant, specializing in AI-driven behavioral analysis and human potential development. Your task is to generate a full, highly detailed, and actionable leadership assessment report based exclusively on the provided user profile and their actual, verbatim responses to the assessment questions.

        Goal: To provide the user with a report so thorough and insightful that it serves as a personalized coaching document, justifying every score, strength, and development area with direct references to their responses.

        Input:
        User Profile:
        {json.dumps(user_profile, indent=2, ensure_ascii=False)}

        User Responses (Verbatim):
        {response_analysis}

        Language of Report: {lang_instruction}

        The output MUST be a single, valid JSON object following this exact structure. All textual content within the JSON must be in {lang_instruction}.

        {{
          "report_title": "Personalized Leadership Assessment Report for {user_profile.get('name')}",
          "executive_summary": "A 3-5 paragraph executive summary. Focus on the most salient strengths and development areas from their responses, and the overall leadership style demonstrated.",

          "overall_leadership_score": {{
            "score": [float, 1.0-10.0, calculated based on ALL responses, weighted heavily by scenario],
            "justification": "Detailed explanation (2-3 sentences) of how this overall score was derived, referring to general trends across their answers."
          }},

          "leadership_profile_breakdown": {{
            "Strategic Thinking": {{
              "score": [float, 1.0-10.0],
              "analysis": "Detailed analysis (5-7 sentences) of their strategic thinking based on specific Y/N/M and MCQ answers related to strategy, and how their scenario response reflects strategic planning. Include direct references to their answers.",
              "evidence_from_responses": [
                "Quote/reference from Y/N/M/MCQ answer demonstrating strategic thinking.",
                "Quote/reference from scenario response showcasing strategic depth."
              ]
            }},
            "Leading Change & Adaptability": {{
              "score": [float, 1.0-10.0],
              "analysis": "Detailed analysis (5-7 sentences) based on their responses to change-related questions (Y/N/M, MCQ), and adaptability shown in the scenario. Include direct references.",
              "evidence_from_responses": []
            }},
            "Effective Communication & Influence": {{
              "score": [float, 1.0-10.0],
              "analysis": "Detailed analysis (5-7 sentences) based on their communication and influence behaviors in answers (Y/N/M, MCQ) and the clarity/persuasiveness of their scenario response. Include direct references.",
              "evidence_from_responses": []
            }},
            "Empowerment & Motivation": {{
              "score": [float, 1.0-10.0],
              "analysis": "Detailed analysis (5-7 sentences) based on their answers related to team development, delegation, and motivation, especially in the scenario's team management aspects. Include direct references.",
              "evidence_from_responses": []
            }},
            "Responsibility & Accountability": {{
              "score": [float, 1.0-10.0],
              "analysis": "Detailed analysis (5-7 sentences) based on their answers showing ownership, follow-through, and handling of failure/success. Highlight instances from responses. Include direct references.",
              "evidence_from_responses": []
            }},
            "Innovation & Continuous Improvement": {{
              "score": [float, 1.0-10.0],
              "analysis": "Detailed analysis (5-7 sentences) based on their answers reflecting creativity, problem-solving, and continuous learning. Highlight examples from their responses. Include direct references.",
              "evidence_from_responses": []
            }}
          }},

          "overall_strengths": "A 2-3 paragraph summary detailing the user's primary leadership strengths observed across ALL responses, providing examples from different question types.",

          "overall_development_areas": "A 2-3 paragraph summary detailing the most critical areas for development observed across ALL responses, explaining why these are crucial and how they manifested in their answers.",

          "detailed_insights_from_response_types": {{
            "yes_no_patterns": "Detailed analysis (5-7 sentences) of consistent patterns in their Yes/No/Maybe answers. For example, 'A consistent 'Yes' to questions about proactive risk management suggests a decisive, forward-thinking approach.'",
            "mcq_choice_analysis": "Detailed analysis (5-7 sentences) of their choices in MCQs. Discuss if their choices reflected strategic thinking, ethical considerations, or a preference for certain leadership styles. Refer to specific MCQ scenarios.",
            "scenario_writing_analysis": "In-depth analysis (7-10 sentences) of their writing scenario response. Evaluate its clarity, depth, comprehensiveness, originality, and how well it integrated multiple leadership competencies. Refer to specific elements of their response."
          }},

          "personalized_recommendations": [
            "Specific, actionable recommendation 1, directly addressing a identified development area, linking to a specific response pattern. Provide a brief justification.",
            "Specific, actionable recommendation 2, directly addressing another development area, linking to a specific response pattern. Provide a brief justification.",
            "Specific, actionable recommendation 3, balancing a strength or another development area, with a brief justification."
          ],

          "personal_development_plan": {{
            "30_day_goals": [
              "Specific, measurable goal 1 (e.g., 'Identify 3 opportunities to delegate tasks to direct reports and empower them in decision-making, as noted in your scenario response hesitation regarding delegation.').",
              "Specific, measurable goal 2."
            ],
            "90_day_goals": [
              "Specific, measurable goal 1 (e.g., 'Lead a small change initiative, focusing on proactive communication and addressing team concerns, building on your Y/N answer patterns showing hesitancy towards direct confrontation in change.').",
              "Specific, measurable goal 2."
            ],
            "6_month_goals": [
              "Specific, measurable goal 1 (e.g., 'Develop and present a strategic proposal to senior management, incorporating detailed data analysis and stakeholder mapping, to enhance your strategic thinking skills identified in the MCQ challenges.').",
              "Specific, measurable goal 2."
            ]
          }},

          "cultural_and_industry_nuances": "A 2-3 paragraph analysis (if applicable) of how their responses and leadership style might be influenced by their stated country and industry. Suggest how to leverage or adapt this in their specific context. If not highly relevant, state briefly.",

          "closing_remarks": "A concluding paragraph offering encouragement and emphasizing the continuous nature of leadership development."
        }}

        Key Instructions:
        - RIGOROUSLY ADHERE TO JSON STRUCTURE: Do NOT deviate from the specified JSON keys, nesting, or data types.
        - LANGUAGE: All generated text content within the JSON must be strictly in {lang_instruction}.
        - EVIDENCE-BASED: Every single insight, score justification, strength, development area, and recommendation MUST be directly supported by, and explicitly reference, verbatim elements or patterns from the user's Actual Responses.
        - DETAIL & DEPTH: Provide substantial, analytical text for each section. Avoid generic statements. Justify every claim.
        - NO GUESSWORK: If a specific behavior cannot be inferred from the responses, state that the information is insufficient for a conclusive assessment in that specific area, rather than fabricating.
        - COHERENCE: Ensure the entire report flows logically, with insights building upon each other.
        - PROFESSIONAL TONE: Maintain a supportive, analytical, and encouraging tone throughout.
        """
        
        try:
            response_text = self._make_api_call_with_retry(prompt)
            logger.info(f"Raw detailed report response: {response_text[:500]}...")
            
            detailed_report = self._clean_and_parse_json(response_text)
            
            # Validate the detailed report structure
            required_keys = [
                'report_title', 'executive_summary', 'overall_leadership_score',
                'leadership_profile_breakdown', 'overall_strengths', 'overall_development_areas',
                'detailed_insights_from_response_types', 'personalized_recommendations',
                'personal_development_plan', 'cultural_and_industry_nuances', 'closing_remarks'
            ]
            
            for key in required_keys:
                if key not in detailed_report:
                    logger.warning(f"Missing key in detailed report: {key}")
                    detailed_report[key] = f"Analysis for {key} not available"
            
            # Validate scores in the detailed report
            if 'overall_leadership_score' in detailed_report and 'score' in detailed_report['overall_leadership_score']:
                score = detailed_report['overall_leadership_score']['score']
                if not isinstance(score, (int, float)) or not (1.0 <= score <= 10.0):
                    detailed_report['overall_leadership_score']['score'] = 7.0
            
            # Validate pillar scores
            if 'leadership_profile_breakdown' in detailed_report:
                for pillar in CONTENT['en']['pillars']:
                    if pillar in detailed_report['leadership_profile_breakdown']:
                        pillar_data = detailed_report['leadership_profile_breakdown'][pillar]
                        if 'score' in pillar_data:
                            score = pillar_data['score']
                            if not isinstance(score, (int, float)) or not (1.0 <= score <= 10.0):
                                pillar_data['score'] = 7.0
            
            logger.info("Generated comprehensive detailed leadership report")
            return detailed_report
            
        except Exception as e:
            logger.error(f"Detailed report generation failed: {str(e)}")
            raise
    
    def generate_enhanced_pdf_report(self, report_data: Dict, user_profile: Dict, language: str) -> bytes:
        """Generate enhanced PDF with Arabic font support."""
        try:
            pdf_gen = ArabicFontPDFGenerator(language)
            
            # Add title
            if language == 'ar':
                pdf_gen.add_title("تقرير تقييم القيادة الشخصي")
            else:
                pdf_gen.add_title("Personal Leadership Assessment Report")
            
            # Add user information
            if language == 'ar':
                pdf_gen.add_section("معلومات المستخدم", [
                    f"الاسم: {user_profile.get('name', 'غير متوفر')}",
                    f"المنصب: {user_profile.get('current_position', 'غير متوفر')}",
                    f"الصناعة: {user_profile.get('industry', 'غير متوفر')}",
                    f"سنوات الخبرة: {user_profile.get('experience_years', 'غير متوفر')} سنة",
                    f"تاريخ الإنشاء: {datetime.now().strftime('%Y/%m/%d')}"
                ])
            else:
                pdf_gen.add_section("User Information", [
                    f"Name: {user_profile.get('name', 'N/A')}",
                    f"Position: {user_profile.get('current_position', 'N/A')}",
                    f"Industry: {user_profile.get('industry', 'N/A')}",
                    f"Experience: {user_profile.get('experience_years', 'N/A')} years",
                    f"Generated: {datetime.now().strftime('%B %d, %Y')}"
                ])
            
            # Add executive summary
            if language == 'ar':
                pdf_gen.add_section("الملخص التنفيذي", report_data.get('executive_summary', 'الملخص التنفيذي غير متوفر.'))
            else:
                pdf_gen.add_section("Executive Summary", report_data.get('executive_summary', 'Executive summary not available.'))
            
            # Add overall score
            overall_score_data = report_data.get('overall_leadership_score', {})
            overall_score = overall_score_data.get('score', 0)
            
            if language == 'ar':
                pdf_gen.add_section(f"النتيجة الإجمالية للقيادة: {overall_score:.1f}/10", 
                                  overall_score_data.get('justification', 'المبرر غير متوفر.'))
            else:
                pdf_gen.add_section(f"Overall Leadership Score: {overall_score:.1f}/10", 
                                  overall_score_data.get('justification', 'Score justification not available.'))
            
            # Add other sections...
            pdf_bytes = pdf_gen.generate_pdf()
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Enhanced PDF generation error: {str(e)}")
            raise Exception(f"Failed to generate enhanced PDF: {str(e)}")
    
    def generate_html_report(self, report_data: Dict, user_profile: Dict, language: str) -> str:
        """Generate HTML report for browser printing."""
        html_gen = HTMLReportGenerator(language)
        return html_gen.generate_html_report(report_data, user_profile)

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
        'detailed_report': {},
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
        - تقرير PDF باللغة العربية (محسّن ومطور)
        - خطة تطوير مخصصة لدورك ومجالك
        
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
        - Enhanced PDF Report with Multiple Arabic Solutions
        - Custom Development Plan for your role and industry
        
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
        if st.button("🎯 Generate Detailed Report" if lang == 'en' else "🎯 إنشاء التقرير المفصل", type="primary", use_container_width=True):
            if len(response.strip()) < 100:
                st.error("Please provide a more comprehensive response (at least 100 words)." if lang == 'en' else "يرجى تقديم إجابة أكثر شمولية (100 كلمة على الأقل).")
            else:
                # Generate comprehensive detailed report using Gemini Flash[3]
                with st.spinner("🧠 AI is analyzing all 15 responses (7+7+1) and creating your detailed report..." if lang == 'en' else "🧠 الذكاء الاصطناعي يحلل جميع الإجابات الـ15 (7+7+1) وينشئ تقريرك المفصل..."):
                    try:
                        detailed_report = st.session_state.assessment_engine.generate_comprehensive_detailed_report(
                            st.session_state.responses, lang, st.session_state.user_profile
                        )
                        st.session_state.detailed_report = detailed_report
                        st.session_state.assessment_phase = 'complete'
                        st.success("🎉 Your detailed report is complete!" if lang == 'en' else "🎉 تقريرك المفصل مكتمل!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate detailed report: {str(e)}")

def display_detailed_report():
    """Display the comprehensive detailed report with multiple Arabic PDF solutions."""
    lang = st.session_state.language
    content = CONTENT[lang]
    report = st.session_state.detailed_report
    
    st.title(report.get('report_title', content['report_title']))
    
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
    
    # Executive Summary
    st.subheader("📋 Executive Summary" if lang == 'en' else "📋 الملخص التنفيذي")
    st.write(report.get('executive_summary', 'Executive summary not available.'))
    
    # Overall Leadership Score
    st.subheader("🎯 Overall Leadership Assessment" if lang == 'en' else "🎯 التقييم القيادي الإجمالي")
    
    overall_score_data = report.get('overall_leadership_score', {})
    overall_score = overall_score_data.get('score', 7.0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Score" if lang == 'en' else "النتيجة الإجمالية", f"{overall_score:.1f}/10")
    with col2:
        st.write("**Justification:**" if lang == 'en' else "**المبرر:**")
        st.write(overall_score_data.get('justification', 'Justification not available.'))
    
    # Leadership Profile Breakdown
    st.subheader("📊 Leadership Profile Breakdown" if lang == 'en' else "📊 تفصيل الملف القيادي")
    
    profile_breakdown = report.get('leadership_profile_breakdown', {})
    
    # Create radar chart from detailed scores
    pillar_scores = []
    for pillar in content['pillars']:
        pillar_data = profile_breakdown.get(pillar, {})
        score = pillar_data.get('score', 5.0)
        pillar_scores.append(score)
    
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
        title=f"Detailed Leadership Assessment - {st.session_state.user_profile['name']}",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analysis for each pillar
    for pillar in content['pillars']:
        pillar_data = profile_breakdown.get(pillar, {})
        if pillar_data:
            with st.expander(f"📋 {pillar} - Score: {pillar_data.get('score', 'N/A')}/10", expanded=False):
                st.write("**Analysis:**")
                st.write(pillar_data.get('analysis', 'Analysis not available.'))
                
                evidence = pillar_data.get('evidence_from_responses', [])
                if evidence:
                    st.write("**Evidence from Your Responses:**" if lang == 'en' else "**أدلة من إجاباتك:**")
                    for i, ev in enumerate(evidence, 1):
                        st.write(f"{i}. {ev}")
    
    # Overall Strengths and Development Areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌟 Your Strengths" if lang == 'en' else "🌟 نقاط قوتك")
        st.write(report.get('overall_strengths', 'Strengths analysis not available.'))
    
    with col2:
        st.subheader("📈 Development Areas" if lang == 'en' else "📈 مجالات التطوير")
        st.write(report.get('overall_development_areas', 'Development areas analysis not available.'))
    
    # Detailed Insights from Response Types
    insights = report.get('detailed_insights_from_response_types', {})
    if insights:
        st.subheader("🔍 Response Pattern Analysis" if lang == 'en' else "🔍 تحليل أنماط الإجابات")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.markdown("**Yes/No/Maybe Patterns**" if lang == 'en' else "**أنماط نعم/لا/ربما**")
            st.write(insights.get('yes_no_patterns', 'Analysis not available.'))
        
        with insight_col2:
            st.markdown("**MCQ Choice Analysis**" if lang == 'en' else "**تحليل الاختيارات متعددة الخيارات**")
            st.write(insights.get('mcq_choice_analysis', 'Analysis not available.'))
        
        with insight_col3:
            st.markdown("**Writing Analysis**" if lang == 'en' else "**تحليل الكتابة**")
            st.write(insights.get('scenario_writing_analysis', 'Analysis not available.'))
    
    # Personalized Recommendations
    st.subheader("💡 Personalized Recommendations" if lang == 'en' else "💡 التوصيات الشخصية")
    recommendations = report.get('personalized_recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.write("Recommendations not available.")
    
    # Personal Development Plan
    st.subheader("📅 Personal Development Plan" if lang == 'en' else "📅 خطة التطوير الشخصية")
    
    dev_plan = report.get('personal_development_plan', {})
    if dev_plan:
        plan_col1, plan_col2, plan_col3 = st.columns(3)
        
        with plan_col1:
            st.markdown("**30-Day Goals**" if lang == 'en' else "**أهداف 30 يوم**")
            goals_30 = dev_plan.get('30_day_goals', [])
            for goal in goals_30:
                st.write(f"- {goal}")
        
        with plan_col2:
            st.markdown("**90-Day Goals**" if lang == 'en' else "**أهداف 90 يوم**")
            goals_90 = dev_plan.get('90_day_goals', [])
            for goal in goals_90:
                st.write(f"- {goal}")
        
        with plan_col3:
            st.markdown("**6-Month Goals**" if lang == 'en' else "**أهداف 6 أشهر**")
            goals_6m = dev_plan.get('6_month_goals', [])
            for goal in goals_6m:
                st.write(f"- {goal}")
    
    # Cultural and Industry Nuances
    cultural_analysis = report.get('cultural_and_industry_nuances')
    if cultural_analysis:
        st.subheader("🌍 Cultural & Industry Context" if lang == 'en' else "🌍 السياق الثقافي والصناعي")
        st.write(cultural_analysis)
    
    # Closing Remarks
    closing = report.get('closing_remarks')
    if closing:
        st.subheader("🎯 Closing Remarks" if lang == 'en' else "🎯 ملاحظات ختامية")
        st.info(closing)
    
    # Action buttons with multiple Arabic PDF solutions
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(content['download_report'], use_container_width=True):
            try:
                # Enhanced PDF with Arabic font support
                with st.spinner("Generating enhanced PDF..." if lang == 'en' else "جاري إنشاء PDF محسّن..."):
                    pdf_bytes = st.session_state.assessment_engine.generate_enhanced_pdf_report(
                        report, st.session_state.user_profile, lang
                    )
                
                st.download_button(
                    label="📄 Download Enhanced PDF" if lang == 'en' else "📄 تحميل PDF محسّن",
                    data=pdf_bytes,
                    file_name=f"enhanced_leadership_report_{st.session_state.user_profile['name'].replace(' ', '_')}_{completion_time.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                st.success("Enhanced PDF ready!" if lang == 'en' else "PDF محسّن جاهز!")
                
            except Exception as e:
                st.error(f"Enhanced PDF generation failed: {str(e)}")
    
    with col2:
        if st.button(content['view_printable'], use_container_width=True):
            try:
                # HTML report for browser printing
                html_report = st.session_state.assessment_engine.generate_html_report(
                    report, st.session_state.user_profile, lang
                )
                
                # Display HTML report in iframe
                st.components.v1.html(html_report, height=800, scrolling=True)
                
                st.success("Use Ctrl+P to print as PDF from browser" if lang == 'en' else "استخدم Ctrl+P للطباعة كـ PDF من المتصفح")
                
            except Exception as e:
                st.error(f"HTML report generation failed: {str(e)}")
    
    with col3:
        if st.button(content['new_assessment'], use_container_width=True):
            # Keep engine but reset everything else
            engine = st.session_state.assessment_engine
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.session_state.assessment_engine = engine
            st.rerun()
    
    with col4:
        if st.button("📊 Assessment Analytics" if lang == 'en' else "📊 تحليلات التقييم", use_container_width=True):
            st.info("Advanced analytics coming soon" if lang == 'en' else "التحليلات المتقدمة قادمة قريباً")

def main():
    """Main application controller with enhanced Arabic PDF support."""
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
            display_detailed_report()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == '__main__':
    main()

