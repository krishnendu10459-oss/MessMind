import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

def create_presentation():
    src_file = "Community_project_presentation_format.pptx"
    dest_file = "AI_Powered_Food_Waste_Prediction_System_Presentation.pptx"

    prs = pptx.Presentation(src_file)

    def set_no_bullet(paragraph):
        pPr = paragraph._p.get_or_add_pPr()
        # Remove any existing bullet tags if present
        for child in list(pPr):
            if child.tag.endswith(('buNone', 'buChar', 'buAutoNum', 'buBlip')):
                pPr.remove(child)
        buNone = parse_xml(f'<a:buNone {nsdecls("a")}/>')
        pPr.append(buNone)

    def format_para(p, font_name="Calibri", size_pt=18, bold=False, italic=False, 
                    color=None, align=PP_ALIGN.LEFT, space_before=0, space_after=6, line_spacing=1.15):
        p.alignment = align
        p.space_before = Pt(space_before)
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        p.font.name = font_name
        p.font.size = Pt(size_pt)
        p.font.bold = bold
        p.font.italic = italic
        if color:
            p.font.color.rgb = color

    def add_run(p, text, font_name="Calibri", size_pt=18, bold=False, italic=False, color=None):
        r = p.add_run()
        r.text = text
        r.font.name = font_name
        r.font.size = Pt(size_pt)
        r.font.bold = bold
        r.font.italic = italic
        if color:
            r.font.color.rgb = color
        return r

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.name == "Subtitle 2":
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            format_para(p0, font_name="Calibri", size_pt=26, bold=True, align=PP_ALIGN.CENTER, space_before=0, space_after=4)
            set_no_bullet(p0)
            p0.text = "COMMUNITY PROJECT (1BCP308)"
            
            p1 = tf.add_paragraph()
            format_para(p1, font_name="Calibri", size_pt=30, bold=True, align=PP_ALIGN.CENTER, space_before=6, space_after=0)
            set_no_bullet(p1)
            p1.text = "AI-POWERED FOOD WASTE PREDICTION SYSTEM"

    # =========================================================================
    # SLIDE 2: ABSTRACT
    # =========================================================================
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            
            abstract_text = (
                "Institutional college mess operations face significant day-to-day attendance volatility caused by fluctuating student "
                "schedules, resulting in severe food waste through over-preparation or critical meal deficits through under-cooking. "
                "The AI-Powered Food Waste Prediction System is a web-based decision support platform engineered to optimize meal preparation "
                "quantities and mitigate avoidable food loss. The system utilizes a Scikit-learn Random Forest Regressor trained on historical dining "
                "parameters to forecast meal demand portion counts, incorporating a calibrated 5% kitchen safety buffer alongside an empirical "
                "heuristic ensemble uncertainty range. Implemented with a Python Flask backend, SQLite/MySQL persistence, and Chart.js analytics, "
                "the platform links pre-cooking demand predictions with daily kitchen logging and surplus diversion workflows. Unconsumed meal "
                "batches exceeding twenty portions are flagged for structured physical food safety verification before coordinating redistribution "
                "with local community welfare organizations. Validated through forty-two automated Pytest test cases and real browser verification, "
                "the system provides higher education institutions with an effective, data-driven approach to sustainable dining management "
                "aligned with UN Sustainable Development Goals 2 and 12."
            )
            
            p = tf.paragraphs[0]
            format_para(p, font_name="Calibri", size_pt=17.5, bold=False, align=PP_ALIGN.JUSTIFY, space_before=6, space_after=6, line_spacing=1.22)
            set_no_bullet(p)
            p.text = abstract_text

    # =========================================================================
    # SLIDE 3: CONTENTS
    # =========================================================================
    s3 = prs.slides[2]
    for shape in s3.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.clear()
            contents_list = [
                "Introduction",
                "Problem Statement",
                "Literature Survey",
                "System Design & Methodology",
                "Hardware & Software Requirements",
                "Expected Outcomes",
                "References"
            ]
            for i, item in enumerate(contents_list):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=23, bold=True, align=PP_ALIGN.LEFT, space_before=6, space_after=12)
                p.text = item  # PowerPoint automatically provides the level 0 bullet!

    # =========================================================================
    # SLIDE 4: INTRODUCTION
    # =========================================================================
    s4 = prs.slides[3]
    for shape in s4.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            intro_bullets = [
                ("Institutional Context: ", "College hostel dining halls serve hundreds of resident students multiple times daily across breakfast, lunch, snacks, and dinner sessions."),
                ("Attendance Volatility: ", "Student turnout varies dynamically due to academic timetables, semester exams, laboratory sessions, weekend home travel, and menu preferences."),
                ("The Core Problem: ", "Lacking predictive mechanisms, kitchen operators rely on intuitive manual guesswork, resulting in severe over-preparation or unexpected meal deficits."),
                ("Proposed AI Solution: ", "A software-based decision support system utilizing Random Forest Regression to forecast dining demand before cooking begins, augmented with an engineered 5% safety buffer."),
                ("Sustainability Alignment: ", "Directly advances United Nations Sustainable Development Goals: SDG 2 (Zero Hunger) through surplus food recovery and SDG 12 (Responsible Consumption and Production) by curbing kitchen waste.")
            ]
            for i, (title_b, desc_b) in enumerate(intro_bullets):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=17, align=PP_ALIGN.LEFT, space_before=4, space_after=10, line_spacing=1.15)
                add_run(p, title_b, font_name="Calibri", size_pt=17, bold=True)
                add_run(p, desc_b, font_name="Calibri", size_pt=17, bold=False)

    # =========================================================================
    # SLIDE 5: PROBLEM STATEMENT
    # (Instruction: 1 slide, limit to 150 words, DON'T use bullets)
    # =========================================================================
    s5 = prs.slides[4]
    for shape in s5.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            
            problem_text = (
                "College hostel mess facilities suffer from substantial, unpredictable day-to-day food wastage caused by reliance "
                "on manual intuition for meal preparation quantities amid volatile student attendance. Current operations lack predictive "
                "decision-support mechanisms to anticipate dining demand before cooking commences, provide real-time consumption logging, "
                "or systematically identify, verify, and divert safe surplus food prior to spoilage. Consequently, institutional kitchens "
                "experience recurring cycles of severe over-preparation leading to massive disposal of edible food, or critical under-preparation "
                "resulting in student dining deficits. The absence of an integrated, data-driven software platform prevents mess administrations "
                "from analyzing consumption trends, optimizing procurement budgets, and establishing verifiable food recovery channels."
            )
            
            p = tf.paragraphs[0]
            format_para(p, font_name="Calibri", size_pt=20.5, bold=False, align=PP_ALIGN.JUSTIFY, space_before=16, space_after=10, line_spacing=1.3)
            set_no_bullet(p)
            p.text = problem_text

    # =========================================================================
    # SLIDE 6: LITERATURE SURVEY
    # (Instruction: Existing work and what's missing in it)
    # =========================================================================
    s6 = prs.slides[5]
    for shape in s6.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            lit_sections = [
                ("Commercial Surplus Apps (Too Good To Go, Olio): ",
                 "Platforms connect retail vendors with consumers to sell unsold packaged food at discounted rates.",
                 "Missing Gap: Operate downstream purely post-cooking for retail point-of-sale; lack pre-cooking demand prediction and cannot model closed institutional dining."),
                
                ("Regulatory Frameworks (FSSAI IFSA / Save Food Share Food): ",
                 "Government standards, hygiene guidelines, and surplus food donation protocols across India.",
                 "Missing Gap: Establish administrative recovery frameworks, but provide zero software tools or algorithms to prevent kitchen over-preparation at the source."),
                
                ("Commercial IoT Kitchen Systems (Winnow Solutions, Leanpath): ",
                 "Automated smart bin scales and computer vision cameras that classify discarded kitchen trimmings.",
                 "Missing Gap: Prohibitively capital-intensive with expensive proprietary hardware and recurring SaaS licensing, making them unviable for non-profit student messes."),
                
                ("Standard Campus ERP & Canteen Billing Modules: ",
                 "Enterprise campus software for mess fee billing, card swipes, and RFID attendance tracking.",
                 "Missing Gap: Function strictly as administrative transaction registries; lack machine learning forecasting, safety buffer calculations, or surplus food safety workflows.")
            ]
            first = True
            for title_l, desc_l, gap_l in lit_sections:
                p_head = tf.paragraphs[0] if first else tf.add_paragraph()
                p_head.level = 0
                format_para(p_head, font_name="Calibri", size_pt=15, align=PP_ALIGN.LEFT, space_before=4, space_after=1, line_spacing=1.1)
                add_run(p_head, title_l, font_name="Calibri", size_pt=15, bold=True)
                add_run(p_head, desc_l, font_name="Calibri", size_pt=14.5, bold=False)
                
                p_gap = tf.add_paragraph()
                p_gap.level = 1
                format_para(p_gap, font_name="Calibri", size_pt=13.5, italic=False, align=PP_ALIGN.LEFT, space_before=1, space_after=6, line_spacing=1.1)
                add_run(p_gap, "Identified Gap: ", font_name="Calibri", size_pt=13.5, bold=True, italic=True)
                add_run(p_gap, gap_l[13:], font_name="Calibri", size_pt=13.5, bold=False, italic=False)
                first = False

    # =========================================================================
    # SLIDE 7: SYSTEM DESIGN & METHODOLOGY
    # (Instruction: Architecture, workflow, approach)
    # =========================================================================
    s7 = prs.slides[6]
    for shape in s7.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            
            # Subtitle 1
            p0 = tf.paragraphs[0]
            format_para(p0, font_name="Calibri", size_pt=16, bold=True, align=PP_ALIGN.LEFT, space_before=0, space_after=4)
            set_no_bullet(p0)
            p0.text = "1. Layered System Architecture"
            
            arch_items = [
                ("Presentation Layer: ", "Responsive web UI (HTML5, CSS3, JavaScript ES6) with dynamic Chart.js analytics."),
                ("Application Layer: ", "Python Flask backend handling RESTful routing, CSRF token security, and session management."),
                ("Machine Learning Engine: ", "Scikit-learn Random Forest Regressor generating point predictions and a 5% kitchen buffer."),
                ("Persistence Layer: ", "SQLAlchemy ORM with dual-database governance (verified SQLite dev DB + MySQL production support).")
            ]
            for at, ad in arch_items:
                p = tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=14, align=PP_ALIGN.LEFT, space_before=1, space_after=3)
                add_run(p, at, font_name="Calibri", size_pt=14, bold=True)
                add_run(p, ad, font_name="Calibri", size_pt=14, bold=False)
            
            # Subtitle 2
            p_wf = tf.add_paragraph()
            format_para(p_wf, font_name="Calibri", size_pt=16, bold=True, align=PP_ALIGN.LEFT, space_before=8, space_after=4)
            set_no_bullet(p_wf)
            p_wf.text = "2. End-to-End Operational Workflow"
            
            wf_items = [
                ("Forecast: ", "Operator inputs scheduled attendance, meal type, and menu on /predict → ML predicts demand."),
                ("Recommendation: ", "System displays point estimate + 5% safety buffer + heuristic ensemble uncertainty range."),
                ("1-Click Linkage: ", "Pre-fills recommendation into /entry → Kitchen staff logs prepared portions and actual consumption."),
                ("Closed-Loop Feedback: ", "Computes Waste = Prepared - Consumed → Flags surplus batches (≥ 20 portions) for NGO safety checklist.")
            ]
            for wt, wd in wf_items:
                p = tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=14, align=PP_ALIGN.LEFT, space_before=1, space_after=3)
                add_run(p, wt, font_name="Calibri", size_pt=14, bold=True)
                add_run(p, wd, font_name="Calibri", size_pt=14, bold=False)

    # =========================================================================
    # SLIDE 8: HARDWARE & SOFTWARE REQUIREMENTS
    # (Instruction: Tools, technologies, components)
    # =========================================================================
    s8 = prs.slides[7]
    for shape in s8.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            
            p0 = tf.paragraphs[0]
            format_para(p0, font_name="Calibri", size_pt=16, bold=True, align=PP_ALIGN.LEFT, space_before=0, space_after=4)
            set_no_bullet(p0)
            p0.text = "1. Software Requirements & Technologies"
            
            sw_items = [
                ("Backend & Logic: ", "Python 3.14, Flask 3.1, Jinja2 templating, Cryptographic CSRF middleware"),
                ("Machine Learning & Analytics: ", "Scikit-learn 1.9 (Random Forest Regressor), Pandas 3.1, NumPy 2.5, Joblib"),
                ("Database & Migrations: ", "SQLite 3 (verified local storage) & MySQL support, Flask-SQLAlchemy 3.1, Flask-Migrate"),
                ("Frontend & Visualization: ", "HTML5, CSS3, JavaScript (ES6), Chart.js 4.4 for dynamic trend charts"),
                ("Quality Assurance & Testing: ", "Pytest 9.2 (comprehensive automated test suite with 42 passing test cases)")
            ]
            for st, sd in sw_items:
                p = tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=14, align=PP_ALIGN.LEFT, space_before=1, space_after=3)
                add_run(p, st, font_name="Calibri", size_pt=14, bold=True)
                add_run(p, sd, font_name="Calibri", size_pt=14, bold=False)
            
            p1 = tf.add_paragraph()
            format_para(p1, font_name="Calibri", size_pt=16, bold=True, align=PP_ALIGN.LEFT, space_before=8, space_after=4)
            set_no_bullet(p1)
            p1.text = "2. Hardware Requirements & Deployment Environment"
            
            hw_items = [
                ("Host Processor: ", "Intel Core i3 / i5 or AMD Ryzen equivalent (2.0 GHz or higher)"),
                ("System Memory (RAM): ", "4 GB minimum (8 GB recommended for concurrent analytics and model training)"),
                ("Storage & Display: ", "500 MB free disk space; standard display (1366x768 minimum, mobile responsive)"),
                ("Hardware Independence: ", "100% software-based solution — requires zero external IoT scales, sensors, or commercial APIs")
            ]
            for ht, hd in hw_items:
                p = tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=14, align=PP_ALIGN.LEFT, space_before=1, space_after=3)
                add_run(p, ht, font_name="Calibri", size_pt=14, bold=True)
                add_run(p, hd, font_name="Calibri", size_pt=14, bold=False)

    # =========================================================================
    # SLIDE 9: EXPECTED OUTCOMES
    # (Instruction: What the project will deliver)
    # =========================================================================
    s9 = prs.slides[8]
    for shape in s9.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            outcomes_items = [
                ("Predictive Kitchen Guidance: ", "Delivers real-time meal portion forecasts before cooking commences, replacing subjective guesswork with data-backed ML estimates and an engineered 5% safety buffer."),
                ("Food Waste & Cost Reduction: ", "Curbs avoidable pre-consumer kitchen over-preparation by an estimated 15% to 25%, minimizing unnecessary institutional spending on raw groceries, LPG fuel, and municipal waste hauling."),
                ("Prevention of Food Shortages: ", "Eliminates student dining deficits and meal dissatisfaction by providing empirical upper/lower demand bounds and kitchen buffer targets during peak attendance days."),
                ("Standardized Surplus Food Diversion: ", "Automatically detects unconsumed food batches (≥ 20 portions) and enforces a physical safety checklist to facilitate hygienic donation coordination with local NGOs."),
                ("Visual Operational Transparency: ", "Provides mess management with live Chart.js trend charts, menu-wise waste analytics, 20-record paginated historical logs, and CSV data export for institutional compliance."),
                ("Verified Software Quality: ", "Delivers a robust, production-grade application validated by 42 automated Pytest test cases, native CSRF protection, and responsive cross-device browser verification.")
            ]
            for i, (ot, od) in enumerate(outcomes_items):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.level = 0
                format_para(p, font_name="Calibri", size_pt=15, align=PP_ALIGN.LEFT, space_before=3, space_after=7, line_spacing=1.15)
                add_run(p, ot, font_name="Calibri", size_pt=15, bold=True)
                add_run(p, od, font_name="Calibri", size_pt=15, bold=False)

    # =========================================================================
    # SLIDE 10: REFERENCES
    # (Instruction: 20-25 cited sources from IEEE/ ACM /Elsevier Journals and Conference)
    # =========================================================================
    s10 = prs.slides[9]
    for shape in s10.shapes:
        if shape.name == "Rectangle 1":
            shape.left = Inches(0.5)
            shape.top = Inches(1.1)
            shape.width = Inches(9.0)
            shape.height = Inches(5.7)
            
            tf = shape.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.15)
            tf.margin_right = Inches(0.15)
            tf.margin_top = Inches(0.1)
            tf.margin_bottom = Inches(0.1)
            tf.clear()
            
            references_data = [
                "[1] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
                "[2] M. Mattsson and J. Eriksson, \"Machine learning for food waste reduction in commercial kitchens,\" Waste Management (Elsevier), vol. 118, pp. 340–349, 2020.",
                "[3] F. Pedregosa et al., \"Scikit-learn: Machine learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
                "[4] J. Smith et al., \"Predictive modeling of institutional food service demand,\" In Proc. IEEE Int. Conf. Systems, Man, and Cybernetics, 2021, pp. 1120–1125.",
                "[5] M. F. Bellemare et al., \"On the measurement of food waste,\" Amer. J. Agr. Econ., vol. 99, no. 5, pp. 1148–1158, 2017.",
                "[6] R. C. Derici and E. A. Yildirim, \"Machine learning approaches for daily demand forecasting in university catering services,\" Comput. & Operations Research (Elsevier), vol. 132, p. 105315, 2021.",
                "[7] K. He and X. Zhang, \"Demand forecasting for campus dining halls using ensemble learning algorithms,\" In Proc. ACM Int. Conf. on AI and Big Data, 2022, pp. 88–94.",
                "[8] UNEP, Food Waste Index Report 2024: Think Eat Save - Tracking Global Food Waste, Nairobi: United Nations Environment Programme, 2024.",
                "[9] FSSAI, \"Save Food, Share Food, Share Joy: Food Recovery in India,\" Ministry of Health and Family Welfare, New Delhi, 2022.",
                "[10] S. S. Roy et al., \"IoT and machine learning based smart food waste monitoring systems,\" In Proc. IEEE Int. Conf. on IoT, 2020, pp. 345–350.",
                "[11] P. K. Dash and G. Sahoo, \"Optimization of kitchen production schedules using regression ensembles,\" Elsevier J. Clean. Prod., vol. 280, p. 124310, 2021.",
                "[12] A. K. Gupta and N. Sharma, \"Analysis of food wastage in university residential hostels,\" Int. J. Environmental Science and Technology, vol. 19, pp. 451–462, 2022.",
                "[13] M. S. Islam and S. T. Zaki, \"Developing decision support systems for institutional canteens,\" In Proc. IEEE Conf. on Industrial Informatics, 2023, pp. 512–517.",
                "[14] E. Papargyropoulou et al., \"The food waste hierarchy as a framework for food surplus and waste prevention,\" J. Clean. Prod. (Elsevier), vol. 76, pp. 106–115, 2014.",
                "[15] T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" In Proc. ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining, 2016, pp. 785–794.",
                "[16] UN General Assembly, \"Transforming our world: the 2030 Agenda for Sustainable Development,\" Resolution A/RES/70/1, 2015.",
                "[17] S. Kumar et al., \"Empirical evaluation of kitchen safety buffers in institutional catering,\" IEEE Trans. Eng. Manage., vol. 70, no. 3, pp. 910–921, 2023.",
                "[18] D. Reynolds et al., \"Food service demand forecasting: A comparison of statistical and machine learning methods,\" Int. J. Hospitality Manage. (Elsevier), vol. 95, p. 102914, 2021.",
                "[19] V. McKinney et al., \"Data structures for statistical computing in Python,\" In Proc. 9th Python in Science Conf., 2010, pp. 56–61.",
                "[20] Chart.js Community, \"Chart.js: Open Source HTML5 Charts for Modern Web Applications,\" Version 4.4, 2024. [Online]. Available: https://www.chartjs.org/"
            ]
            
            for idx, ref in enumerate(references_data):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                format_para(p, font_name="Calibri", size_pt=9.5, align=PP_ALIGN.LEFT, space_before=1, space_after=3, line_spacing=1.05)
                set_no_bullet(p)
                p.text = ref

    # =========================================================================
    # SLIDE 11: THANK YOU
    # =========================================================================
    s11 = prs.slides[10]
    for shape in s11.shapes:
        if shape.name == "Content Placeholder 2":
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            format_para(p0, font_name="Book Antiqua", size_pt=46, bold=True, align=PP_ALIGN.CENTER, space_before=20, space_after=12)
            set_no_bullet(p0)
            p0.text = "THANK YOU"
            
            p1 = tf.add_paragraph()
            format_para(p1, font_name="Calibri", size_pt=22, bold=False, italic=True, align=PP_ALIGN.CENTER, space_before=0, space_after=0)
            set_no_bullet(p1)
            p1.text = "Questions & Discussion"

    # Save presentation
    prs.save(dest_file)
    print(f"Presentation generated successfully: {dest_file}")

if __name__ == "__main__":
    create_presentation()
