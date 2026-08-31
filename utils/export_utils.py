import pandas as pd
import io
from fpdf import FPDF
from datetime import datetime

def export_to_excel(df, kpis=None, insights=None, filename='report'):
    """Export data, KPIs, and insights to an Excel workbook."""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Data sheet
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Summary sheet
            df.describe().to_excel(writer, sheet_name='Summary')
            
            # KPIs sheet
            if kpis:
                kpi_df = pd.DataFrame(kpis)
                kpi_df.to_excel(writer, sheet_name='KPIs', index=False)
                
            # Insights sheet
            if insights:
                insight_df = pd.DataFrame(insights)
                insight_df.to_excel(writer, sheet_name='Insights', index=False)
                
            # Formatting (basic)
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    
        return output.getvalue()
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return b""

def export_to_pdf(df, kpis=None, insights=None, filename='report'):
    """Export summary report to PDF using fpdf2 library."""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        def safe_text(text):
            if not isinstance(text, str):
                text = str(text)
            return text.encode('latin-1', 'replace').decode('latin-1')

        # Title
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, safe_text(f"AI Business Dashboard Report - {datetime.now().strftime('%Y-%m-%d')}"), ln=True, align='C')
        pdf.ln(10)
        
        # Data Summary
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Data Summary', ln=True)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 8, safe_text(f"Total Rows: {len(df)}"), ln=True)
        pdf.cell(0, 8, safe_text(f"Total Columns: {len(df.columns)}"), ln=True)
        pdf.cell(0, 8, safe_text(f"Columns: {', '.join(df.columns.tolist())}"), ln=True)
        pdf.ln(5)
        
        # KPIs
        if kpis:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Key Performance Indicators (KPIs)', ln=True)
            pdf.set_font('Helvetica', '', 12)
            for kpi in kpis:
                name = kpi.get('name', 'Unknown')
                val = kpi.get('formatted_value', kpi.get('value', ''))
                pdf.cell(0, 8, safe_text(f"- {name}: {val}"), ln=True)
            pdf.ln(5)
            
        # Insights
        if insights:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Top Insights', ln=True)
            pdf.set_font('Helvetica', '', 12)
            for i, insight in enumerate(insights[:5]):
                title = insight.get('title', f"Insight {i+1}")
                detail = insight.get('detail', '')
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 8, safe_text(f"{i+1}. {title}"), ln=True)
                pdf.set_font('Helvetica', '', 12)
                pdf.multi_cell(0, 6, safe_text(detail))
                pdf.ln(2)
            pdf.ln(5)
            
        # Statistical Summary
        num_cols = df.select_dtypes(include=['number']).columns
        if len(num_cols) > 0:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Statistical Summary', ln=True)
            pdf.set_font('Helvetica', '', 12)
            
            stats = df[num_cols].describe().round(2)
            for col in num_cols:
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 8, safe_text(col), ln=True)
                pdf.set_font('Helvetica', '', 12)
                mean_val = stats.loc['mean', col]
                min_val = stats.loc['min', col]
                max_val = stats.loc['max', col]
                pdf.cell(0, 6, safe_text(f"  Mean: {mean_val} | Min: {min_val} | Max: {max_val}"), ln=True)
                pdf.ln(2)
                
        # output pdf as bytes
        out = pdf.output()
        if isinstance(out, (bytearray, str)):
            if isinstance(out, str):
                return out.encode('latin-1')
            return bytes(out)
        return bytes(out)
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        return b""

def get_download_timestamp():
    """Get formatted timestamp for file names."""
    return datetime.now().strftime('%Y-%m-%d_%H-%M')
