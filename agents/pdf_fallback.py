"""
Fallback PDF generation for when WeasyPrint fails on Windows
"""

def create_pdf_with_reportlab(title: str, sections: list, metadata: dict, output_path: str):
    """Create a PDF using ReportLab as fallback when WeasyPrint fails."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        import re
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4, 
                              topMargin=1*inch, bottomMargin=1*inch,
                              leftMargin=1.2*inch, rightMargin=1.2*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=HexColor('#2d3748')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=1,
            textColor=HexColor('#718096'),
            fontName='Helvetica-Oblique'
        )
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=20,
            textColor=HexColor('#667eea')
        )
        
        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Paragraph("A comprehensive, step-by-step guide to mastering every concept", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Add metadata
        metadata_text = f"Generated: {metadata.get('generated_at', 'Unknown')} | Source: {metadata.get('source_query', 'Unknown')} | Sections: {len(sections)}"
        story.append(Paragraph(metadata_text, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Add table of contents
        toc_style = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=HexColor('#495057')
        )
        story.append(Paragraph("Table of Contents", toc_style))
        
        for i, section in enumerate(sections):
            section_title = section.get('title', 'Section').replace('## ', '').replace('# ', '')
            toc_item = f"{i+1}. {section_title}"
            story.append(Paragraph(toc_item, styles['Normal']))
        
        story.append(PageBreak())
        
        # Add sections
        for i, section in enumerate(sections):
            section_title = section.get('title', 'Section').replace('## ', '').replace('# ', '')
            section_content = section.get('content', '')
            
            # Section heading
            story.append(Paragraph(f"{i+1}. {section_title}", section_title_style))
            story.append(Spacer(1, 12))
            
            # Process content - simplified approach
            paragraphs = section_content.split('\n\n')
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                    
                # Handle code blocks
                if para.startswith('```'):
                    code_content = re.sub(r'```.*?\n(.*?)\n```', r'\1', para, flags=re.DOTALL)
                    if code_content:
                        code_style = ParagraphStyle(
                            'Code',
                            parent=styles['Normal'],
                            fontSize=10,
                            fontName='Courier',
                            leftIndent=20,
                            rightIndent=20,
                            spaceAfter=12,
                            spaceBefore=12,
                            backColor=HexColor('#f8f9fa')
                        )
                        story.append(Paragraph(code_content, code_style))
                    continue
                
                # Handle headers
                if para.startswith('###'):
                    header_text = para.replace('###', '').strip()
                    header_style = ParagraphStyle(
                        'SubHeader',
                        parent=styles['Heading3'],
                        fontSize=14,
                        spaceAfter=10,
                        spaceBefore=15,
                        textColor=HexColor('#4a5568')
                    )
                    story.append(Paragraph(header_text, header_style))
                    continue
                
                # Handle lists
                if para.startswith('- ') or para.startswith('* '):
                    list_items = para.split('\n')
                    for item in list_items:
                        if item.strip().startswith(('- ', '* ')):
                            item_text = item.strip()[2:]  # Remove bullet
                            story.append(Paragraph(f"• {item_text}", styles['Normal']))
                    story.append(Spacer(1, 6))
                    continue
                
                # Regular paragraphs
                # Clean up markdown formatting
                clean_text = para
                clean_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', clean_text)  # Bold
                clean_text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', clean_text)      # Italic
                clean_text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', clean_text)  # Inline code
                clean_text = re.sub(r'#{1,6}\s*', '', clean_text)  # Remove remaining headers
                
                if clean_text.strip():
                    story.append(Paragraph(clean_text, styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Add spacing between sections
            story.append(Spacer(1, 30))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"ReportLab PDF generation failed: {e}")
        return False