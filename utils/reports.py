import google.generativeai as genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_AI_KEY"))

class ReportGenerator:
    @staticmethod
    def generate_hotspot_prediction(data):
        prompt = f"""
        Analyze this migration data to identify potential future hotspots:
        {data}

        Provide:
        1. Risk assessment with probability estimates
        2. Predicted future hotspots (top 3 countries)
        3. Timeline of expected migration surges
        4. Recommended interventions

        Format as a professional report with clear sections.
        """

        # ✅ Fix the model name here
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text

    @staticmethod
    def generate_impact_report(data):
        prompt = f"""
        Create a detailed impact report based on:
        {data}

        Include these sections:
        1. Executive Summary
        2. Key Statistics (with numbers)
        3. Economic Impact Analysis
        4. Social Consequences
        5. Policy Recommendations
        6. Long-term Projections

        Use professional tone with bullet points for key findings.
        """

        # ✅ Same here
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text

    @staticmethod
    def create_pdf(content, title="Migration Report"):
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, 750, title)

        pdf.setFont("Helvetica", 12)
        y_position = 700
        for line in content.split('\n'):
            if y_position < 50:
                pdf.showPage()
                y_position = 750
            pdf.drawString(72, y_position, line)
            y_position -= 15

        pdf.save()
        buffer.seek(0)
        return buffer
