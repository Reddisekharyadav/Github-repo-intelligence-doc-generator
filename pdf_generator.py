"""
Advanced PDF Report Generator
Generates comprehensive, well-structured PDF reports with detailed code analysis.
"""

import io
from datetime import datetime
from typing import Dict, List, Any, Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, KeepTogether, Image, Flowable
)
from reportlab.lib import colors


# ──────────────────────────────────────────────
# Custom Styles
# ──────────────────────────────────────────────

def create_custom_styles():
    """Create custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()
    
    # Cover page title
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Title'],
        fontSize=32,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Cover subtitle
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#4e8cff'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Section headers
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=16,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#4e8cff'),
        borderPadding=8,
        backColor=colors.HexColor('#f0f5ff')
    ))
    
    # Sub-section headers
    styles.add(ParagraphStyle(
        name='SubHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))
    
    # File path style
    styles.add(ParagraphStyle(
        name='FilePath',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2980b9'),
        fontName='Courier-Bold',
        backColor=colors.HexColor('#ecf0f1'),
        borderPadding=4,
        spaceAfter=6
    ))
    
    # Code style
    styles.add(ParagraphStyle(
        name='CodeBlock',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        textColor=colors.HexColor('#2c3e50'),
        backColor=colors.HexColor('#f8f9fa'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=4
    ))
    
    # Description style
    styles.add(ParagraphStyle(
        name='Description',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leftIndent=10
    ))
    
    # Metadata style
    styles.add(ParagraphStyle(
        name='Metadata',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=4
    ))
    
    # List item style
    styles.add(ParagraphStyle(
        name='ListItem',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=4
    ))
    
    return styles


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def create_table_style():
    """Create reusable table style."""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e8cff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])


def sanitize_text(text: str) -> str:
    """Sanitize text for PDF (escape special characters)."""
    if not text:
        return ""
    # Replace problematic characters
    text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text


# ──────────────────────────────────────────────
# Section Generators
# ──────────────────────────────────────────────

def add_cover_page(story: List, results: Dict, styles: Dict):
    """Add cover page to the report."""
    meta = results["master_json"]["project_metadata"]
    
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("📊 REPOSITORY INTELLIGENCE REPORT", styles['CoverTitle']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(f"{meta['owner']}/{meta['repo']}", styles['CoverSubtitle']))
    story.append(Spacer(1, 0.5*inch))
    
    # Info box
    info_data = [
        ["Primary Language", sanitize_text(meta['primary_language'])],
        ["Project Type", sanitize_text(meta['project_type'])],
        ["Total Files", str(meta['total_files'])],
        ["Generated", datetime.now().strftime('%B %d, %Y at %H:%M:%S')],
    ]
    
    t = Table(info_data, colWidths=[2*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    story.append(t)
    
    story.append(PageBreak())


def add_table_of_contents(story: List, results: Dict, styles: Dict):
    """DEPRECATED: Table of contents removed for more compact format."""
    pass


# ──────────────────────────────────────────────
# Page-Based Section Functions (Optimized Layout)
# ──────────────────────────────────────────────


def add_executive_summary_page(story: List, results: Dict, styles: Dict):
    """Executive summary page - optimized for page layout."""
    story.append(Paragraph("1. EXECUTIVE SUMMARY", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    meta = results["master_json"]["project_metadata"]
    source_analysis = results.get("source_analysis", [])
    
    # Calculate statistics
    total_classes = sum(len(a.get("classes", [])) for a in source_analysis)
    total_functions = sum(len(a.get("functions", [])) for a in source_analysis)
    total_components = sum(len(a.get("components", [])) for a in source_analysis)
    total_routes = sum(len(a.get("routes", [])) for a in source_analysis)
    
    summary_text = f"""
    This repository contains a <b>{sanitize_text(meta['project_type'])}</b> project primarily written in 
    <b>{sanitize_text(meta['primary_language'])}</b>. The codebase consists of <b>{meta['total_files']}</b> total files, 
    including <b>{meta['source_files']}</b> source code files, <b>{meta['config_files']}</b> configuration files, 
    and <b>{meta['documentation_files']}</b> documentation files.
    """
    
    story.append(Paragraph(summary_text, styles['Description']))
    story.append(Spacer(1, 0.15*inch))
    
    # Key metrics table
    metrics_data = [
        ["Metric", "Count"],
        ["Total Classes", str(total_classes)],
        ["Total Functions/Methods", str(total_functions)],
        ["React Components", str(total_components)],
        ["API Routes", str(total_routes)],
        ["Frontend Detected", "Yes" if meta['frontend_detected'] else "No"],
        ["Backend Detected", "Yes" if meta['backend_detected'] else "No"],
    ]
    
    t = Table(metrics_data, colWidths=[3*inch, 2*inch])
    t.setStyle(create_table_style())
    story.append(t)
    story.append(Spacer(1, 0.2*inch))


def add_project_overview_page(story: List, results: Dict, styles: Dict):
    """Project overview page with language distribution."""
    story.append(Paragraph("2. PROJECT OVERVIEW", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    meta = results["master_json"]["project_metadata"]
    
    # Language breakdown
    story.append(Paragraph("2.1 Language Distribution", styles['SubHeader']))
    
    lang_breakdown = meta.get("language_breakdown", {})
    if lang_breakdown:
        lang_data = [["Language", "Files"]]
        for lang, count in sorted(lang_breakdown.items(), key=lambda x: x[1], reverse=True):
            lang_data.append([sanitize_text(lang), str(count)])
        
        t = Table(lang_data, colWidths=[3*inch, 2*inch])
        t.setStyle(create_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No detailed language breakdown available.", styles['Description']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Project type
    story.append(Paragraph("2.2 Project Type Classification", styles['SubHeader']))
    story.append(Paragraph(f"Detected Type: <b>{sanitize_text(meta['project_type'])}</b>", styles['Description']))
    story.append(Spacer(1, 0.2*inch))
    
    # File counts
    story.append(Paragraph("2.3 File Statistics", styles['SubHeader']))
    file_stats_data = [
        ["Category", "Count"],
        ["Total Files", str(meta['total_files'])],
        ["Source Files", str(meta['source_files'])],
        ["Configuration Files", str(meta['config_files'])],
        ["Documentation Files", str(meta['documentation_files'])],
        ["Test Files", str(meta.get('test_files', 0))],
    ]
    
    t = Table(file_stats_data, colWidths=[3*inch, 2*inch])
    t.setStyle(create_table_style())
    story.append(t)
    story.append(Spacer(1, 0.15*inch))


def add_dependencies_infrastructure_page(story: List, results: Dict, styles: Dict):
    """Add dependencies, frameworks, and infrastructure on one optimized page."""
    story.append(Paragraph("3. DEPENDENCIES, FRAMEWORKS & INFRASTRUCTURE", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    frameworks = results["master_json"].get("frameworks", {})
    deps = results["master_json"].get("dependencies", {})
    infrastructure = results["master_json"].get("infrastructure", {})
    
    # Frameworks
    story.append(Paragraph("3.1 Detected Frameworks", styles['SubHeader']))
    
    if frameworks.get("frontend"):
        story.append(Paragraph("<b>Frontend:</b>", styles['Normal']))
        for fw in frameworks["frontend"]:
            story.append(Paragraph(f"• {sanitize_text(fw)}", styles['ListItem']))
        story.append(Spacer(1, 0.05*inch))
    
    if frameworks.get("backend"):
        story.append(Paragraph("<b>Backend:</b>", styles['Normal']))
        for fw in frameworks["backend"]:
            story.append(Paragraph(f"• {sanitize_text(fw)}", styles['ListItem']))
        story.append(Spacer(1, 0.05*inch))
    
    if not frameworks.get("frontend") and not frameworks.get("backend"):
        story.append(Paragraph("No major frameworks detected.", styles['Description']))
    
    story.append(Spacer(1, 0.12*inch))
    
    # Dependencies
    story.append(Paragraph("3.2 Package Dependencies", styles['SubHeader']))
    
    if deps.get("frontend"):
        story.append(Paragraph(f"<b>Frontend ({len(deps['frontend'])}):</b>", styles['Normal']))
        dep_list = ", ".join([sanitize_text(d) for d in sorted(deps["frontend"][:20])])
        story.append(Paragraph(dep_list, styles['Description']))
        if len(deps['frontend']) > 20:
            story.append(Paragraph(f"... +{len(deps['frontend']) - 20} more", styles['Metadata']))
        story.append(Spacer(1, 0.08*inch))
    
    if deps.get("backend"):
        story.append(Paragraph(f"<b>Backend ({len(deps['backend'])}):</b>", styles['Normal']))
        dep_list = ", ".join([sanitize_text(d) for d in sorted(deps["backend"][:20])])
        story.append(Paragraph(dep_list, styles['Description']))
        if len(deps['backend']) > 20:
            story.append(Paragraph(f"... +{len(deps['backend']) - 20} more", styles['Metadata']))
    
    # Infrastructure section
    story.append(Spacer(1, 0.12*inch))
    story.append(Paragraph("3.3 Infrastructure & Build", styles['SubHeader']))
    
    infra = results["master_json"].get("infrastructure", {})
    
    infra_data = [
        ["Component", "Status"],
        ["Docker", "✓" if infra.get('docker_used') else "✗"],
        ["CI/CD", "✓" if infra.get('ci_cd_detected') else "✗"],
    ]
    
    t = Table(infra_data, colWidths=[3*inch, 1.5*inch])
    t.setStyle(create_table_style())
    story.append(t)
    story.append(Spacer(1, 0.15*inch))


def add_file_structure_page(story: List, results: Dict, styles: Dict):
    """Add file structure and classification page."""
    story.append(Paragraph("4. FILE STRUCTURE & CLASSIFICATION", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    classification = results.get("classification", {})
    
    # Group files by category
    categories = {
        'Frontend': [],
        'Backend': [],
        'Configuration': [],
        'Documentation': [],
        'Tests': [],
        'Build & CI/CD': [],
        'Other': []
    }
    
    for file_info in classification.get('files', []):
        path = file_info.get('path', '')
        category = file_info.get('category', 'Other')
        
        if 'frontend' in category.lower() or 'ui' in category.lower():
            categories['Frontend'].append(path)
        elif 'backend' in category.lower() or 'api' in category.lower():
            categories['Backend'].append(path)
        elif 'config' in category.lower():
            categories['Configuration'].append(path)
        elif 'doc' in category.lower() or 'readme' in path.lower():
            categories['Documentation'].append(path)
        elif 'test' in category.lower() or 'spec' in path.lower():
            categories['Tests'].append(path)
        elif 'ci' in category.lower() or 'build' in category.lower():
            categories['Build & CI/CD'].append(path)
        else:
            categories['Other'].append(path)
    
    for cat_name, files in categories.items():
        if files:
            story.append(Paragraph(f"4.{list(categories.keys()).index(cat_name) + 1} {cat_name} ({len(files)} files)", styles['SubHeader']))
            for file_path in sorted(files)[:20]:  # Limit to 20 files per category
                story.append(Paragraph(f"• {sanitize_text(file_path)}", styles['CodeBlock']))
            if len(files) > 20:
                story.append(Paragraph(f"... and {len(files) - 20} more files", styles['Metadata']))
            story.append(Spacer(1, 0.1*inch))


def add_detailed_source_analysis_pages(story: List, results: Dict, styles: Dict):
    """Add detailed source code analysis across multiple pages."""
    story.append(Paragraph("5. DETAILED SOURCE CODE ANALYSIS", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(
        "Comprehensive analysis of each source file with all classes, methods, functions, components, and routes.",
        styles['Description']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    source_analysis = results.get("source_analysis", [])
    
    for idx, file_analysis in enumerate(source_analysis, 1):
        file_path = file_analysis.get("file_path", "Unknown")
        language = file_analysis.get("language", "Unknown")
        
        # File header
        story.append(Paragraph(f"5.{idx} {sanitize_text(file_path)}", styles['SubHeader']))
        story.append(Paragraph(f"Language: <b>{sanitize_text(language)}</b>", styles['Metadata']))
        story.append(Spacer(1, 0.05*inch))
        
        # Docstring/Summary
        docstring = file_analysis.get("docstring", "")
        if docstring:
            story.append(Paragraph("<b>File Description:</b>", styles['Normal']))
            story.append(Paragraph(sanitize_text(docstring[:500]), styles['Description']))
            story.append(Spacer(1, 0.05*inch))
        
        # Semantic description
        semantic_desc = file_analysis.get("semantic_description", "")
        if semantic_desc:
            story.append(Paragraph("<b>🧠 Semantic Analysis:</b>", styles['Normal']))
            story.append(Paragraph(sanitize_text(semantic_desc), styles['Description']))
            story.append(Spacer(1, 0.05*inch))
        
        # Classes
        classes = file_analysis.get("classes", [])
        if classes:
            story.append(Paragraph(f"<b>Classes ({len(classes)}):</b>", styles['Normal']))
            for cls in classes:
                cls_name = cls.get("name", "Unknown")
                cls_desc = cls.get("description", "")
                methods = cls.get("methods", [])
                
                story.append(Paragraph(f"  • <b>{sanitize_text(cls_name)}</b>", styles['CodeBlock']))
                if cls_desc:
                    story.append(Paragraph(f"    {sanitize_text(cls_desc[:200])}", styles['Description']))
                
                if methods:
                    story.append(Paragraph(f"    Methods: {len(methods)}", styles['Metadata']))
                    for method in methods[:10]:  # Limit to 10 methods
                        method_name = method.get("name", "")
                        params = method.get("parameters", [])
                        method_desc = method.get("description", "")
                        
                        param_str = ", ".join([sanitize_text(str(p)) for p in params])
                        story.append(Paragraph(
                            f"      - {sanitize_text(method_name)}({param_str})",
                            styles['CodeBlock']
                        ))
                        if method_desc:
                            story.append(Paragraph(f"        {sanitize_text(method_desc[:150])}", styles['Description']))
                    
                    if len(methods) > 10:
                        story.append(Paragraph(f"      ... and {len(methods) - 10} more methods", styles['Metadata']))
                
                story.append(Spacer(1, 0.05*inch))
        
        # Functions - ENHANCED with detailed descriptions
        functions = file_analysis.get("functions", [])
        if functions:
            story.append(Paragraph(f"<b>Functions ({len(functions)}):</b>", styles['Normal']))
            story.append(Spacer(1, 0.07*inch))
            
            for func_idx, func in enumerate(functions, 1):  # Show ALL functions
                func_name = func.get("name", "Unknown")
                params = func.get("parameters", [])
                func_desc = func.get("description", "")
                decorators = func.get("decorators", [])
                returns = func.get("returns", "")
                docstring = func.get("docstring", "")
                is_async = func.get("is_async", False)
                
                param_str = ", ".join([sanitize_text(str(p)) for p in params])
                
                # Decorators
                if decorators:
                    dec_str = " ".join([f"@{sanitize_text(d)}" for d in decorators])
                    story.append(Paragraph(f"  {dec_str}", styles['CodeBlock']))
                
                # Function signature
                async_prefix = "async " if is_async else ""
                story.append(Paragraph(
                    f"  {func_idx}. <b>{async_prefix}{sanitize_text(func_name)}</b>({param_str})",
                    styles['CodeBlock']
                ))
                
                # Return type
                if returns:
                    story.append(Paragraph(f"     Returns: {sanitize_text(returns)}", styles['Metadata']))
                
                # Main description
                if func_desc:
                    story.append(Paragraph(f"     📝 {sanitize_text(func_desc[:300])}", styles['Description']))
                
                # Additional docstring
                if docstring and docstring != func_desc:
                    story.append(Paragraph(f"     📄 {sanitize_text(docstring[:250])}", styles['Description']))
                
                # Parameters with descriptions if available
                if params and len(params) > 0:
                    param_info = func.get("param_descriptions", {})
                    story.append(Paragraph(f"     Parameters: {len(params)}", styles['Metadata']))
                    for param in params[:8]:  # Limit params shown
                        param_desc = param_info.get(str(param), "") if param_info else ""
                        if param_desc:
                            story.append(Paragraph(
                                f"       • <b>{sanitize_text(str(param))}</b>: {sanitize_text(param_desc[:150])}",
                                styles['Description']
                            ))
                        else:
                            story.append(Paragraph(
                                f"       • {sanitize_text(str(param))}",
                                styles['Metadata']
                            ))
                
                story.append(Spacer(1, 0.08*inch))
                
                # Page break every 8 functions to manage page space
                if func_idx % 8 == 0 and func_idx < len(functions):
                    story.append(PageBreak())
        
        # React Components
        components = file_analysis.get("components", [])
        if components:
            story.append(Paragraph(f"<b>React Components ({len(components)}):</b>", styles['Normal']))
            for comp in components:
                comp_name = comp.get("name", "Unknown")
                comp_type = comp.get("type", "")
                props = comp.get("props", [])
                hooks = comp.get("hooks", [])
                comp_desc = comp.get("description", "")
                
                story.append(Paragraph(
                    f"  • <b>{sanitize_text(comp_name)}</b> ({sanitize_text(comp_type)})",
                    styles['CodeBlock']
                ))
                
                if props:
                    story.append(Paragraph(f"    Props: {', '.join([sanitize_text(p) for p in props[:5]])}", styles['Metadata']))
                
                if hooks:
                    story.append(Paragraph(f"    Hooks: {', '.join([sanitize_text(h) for h in hooks])}", styles['Metadata']))
                
                if comp_desc:
                    story.append(Paragraph(f"    {sanitize_text(comp_desc[:150])}", styles['Description']))
                
                story.append(Spacer(1, 0.03*inch))
        
        # API Routes
        routes = file_analysis.get("routes", [])
        if routes:
            story.append(Paragraph(f"<b>API Routes ({len(routes)}):</b>", styles['Normal']))
            for route in routes:
                method = route.get("method", "GET")
                path = route.get("path", "")
                handler = route.get("handler", "")
                route_desc = route.get("description", "")
                
                story.append(Paragraph(
                    f"  • <b>{sanitize_text(method)}</b> {sanitize_text(path)}",
                    styles['CodeBlock']
                ))
                
                if handler:
                    story.append(Paragraph(f"    Handler: {sanitize_text(handler)}", styles['Metadata']))
                
                if route_desc:
                    story.append(Paragraph(f"    {sanitize_text(route_desc[:150])}", styles['Description']))
                
                story.append(Spacer(1, 0.03*inch))
        
        story.append(Spacer(1, 0.15*inch))
        
        # Page break after every 5 files for readability
        if idx % 5 == 0 and idx < len(source_analysis):
            story.append(PageBreak())


def add_config_analysis_page(story: List, results: Dict, styles: Dict):
    """Add configuration files analysis page."""
    story.append(Paragraph("6. CONFIGURATION FILES ANALYSIS", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    config_analysis = results.get("config_analysis", [])
    
    if not config_analysis:
        story.append(Paragraph("No configuration files analyzed.", styles['Description']))
        return
    
    for idx, config in enumerate(config_analysis, 1):
        file_path = config.get("file_path", "Unknown")
        config_type = config.get("config_type", "Unknown")
        
        story.append(Paragraph(f"6.{idx} {sanitize_text(file_path)}", styles['SubHeader']))
        story.append(Paragraph(f"Type: <b>{sanitize_text(config_type)}</b>", styles['Metadata']))
        story.append(Spacer(1, 0.05*inch))
        
        # Scripts (for package.json)
        scripts = config.get("scripts", {})
        if scripts:
            story.append(Paragraph("<b>Scripts:</b>", styles['Normal']))
            for script_name, script_cmd in list(scripts.items())[:10]:
                story.append(Paragraph(
                    f"  • {sanitize_text(script_name)}: {sanitize_text(script_cmd)}",
                    styles['CodeBlock']
                ))
            if len(scripts) > 10:
                story.append(Paragraph(f"... and {len(scripts) - 10} more scripts", styles['Metadata']))
            story.append(Spacer(1, 0.05*inch))
        
        # Environment variables
        env_vars = config.get("environment_variables", [])
        if env_vars:
            story.append(Paragraph(f"<b>Environment Variables ({len(env_vars)}):</b>", styles['Normal']))
            for var in env_vars[:15]:
                story.append(Paragraph(f"  • {sanitize_text(var)}", styles['CodeBlock']))
            if len(env_vars) > 15:
                story.append(Paragraph(f"... and {len(env_vars) - 15} more variables", styles['Metadata']))
            story.append(Spacer(1, 0.05*inch))
        
        # Build settings
        build_settings = config.get("build_settings", {})
        if build_settings:
            story.append(Paragraph("<b>Build Settings:</b>", styles['Normal']))
            for key, value in list(build_settings.items())[:10]:
                story.append(Paragraph(
                    f"  • {sanitize_text(key)}: {sanitize_text(str(value)[:100])}",
                    styles['CodeBlock']
                ))
        
        story.append(Spacer(1, 0.15*inch))


def add_architecture_insights_page(story: List, results: Dict, styles: Dict):
    """Add architecture insights page."""
    story.append(Paragraph("7. ARCHITECTURE INSIGHTS", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    graphs = results.get("graphs", {})
    
    if graphs.get("dependency_graph"):
        story.append(Paragraph("7.1 Dependency Graph", styles['SubHeader']))
        story.append(Paragraph(
            "A dependency graph has been generated showing the relationships between modules and components.",
            styles['Description']
        ))
        story.append(Spacer(1, 0.1*inch))
    
    if graphs.get("call_graph"):
        story.append(Paragraph("7.2 Call Graph", styles['SubHeader']))
        story.append(Paragraph(
            "A call graph has been generated showing function call relationships.",
            styles['Description']
        ))
        story.append(Spacer(1, 0.1*inch))
    
    # Architecture patterns detected
    story.append(Paragraph("7.3 Detected Patterns", styles['SubHeader']))
    
    meta = results["master_json"]["project_metadata"]
    patterns = []
    
    if meta.get('frontend_detected') and meta.get('backend_detected'):
        patterns.append("Full-Stack Application (Frontend + Backend)")
    elif meta.get('frontend_detected'):
        patterns.append("Frontend-Only Application")
    elif meta.get('backend_detected'):
        patterns.append("Backend-Only Application")
    
    if patterns:
        for pattern in patterns:
            story.append(Paragraph(f"• {pattern}", styles['ListItem']))
    else:
        story.append(Paragraph("No specific architectural patterns detected.", styles['Description']))
    
    story.append(Spacer(1, 0.15*inch))


def add_appendix_page(story: List, results: Dict, styles: Dict):
    """Add appendix with additional information."""
    story.append(Paragraph("8. APPENDIX", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("8.1 Report Generation Details", styles['SubHeader']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("Tool: Repository Intelligence Engine v1.0", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("8.2 Analysis Methodology", styles['SubHeader']))
    methodology = """
    This report was generated through a multi-stage analysis pipeline:
    1. Repository fetching via GitHub API
    2. File classification and categorization
    3. Static code parsing using AST (Abstract Syntax Tree) analysis
    4. Configuration file parsing
    5. Dependency graph construction
    6. Semantic pattern analysis using rule-based inference
    7. Optional AI architectural review
    """
    story.append(Paragraph(methodology, styles['Description']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("8.3 Disclaimer", styles['SubHeader']))
    disclaimer = """
    This automated analysis provides insights based on static code analysis and pattern recognition.
    While comprehensive, it may not capture all architectural nuances or context-specific design decisions.
    Human review and validation are recommended for critical architectural decisions.
    """
    story.append(Paragraph(disclaimer, styles['Description']))


# ──────────────────────────────────────────────
# Main PDF Generation Function
# ──────────────────────────────────────────────

def generate_comprehensive_pdf_report(results: Dict) -> bytes:
    """
    Generate a comprehensive, well-structured PDF report with detailed analysis.
    Uses page-based formatting to optimize content distribution.
    Automatically manages page breaks based on available space.
    
    Args:
        results: Analysis results dictionary containing all data
        
    Returns:
        bytes: PDF file as bytes
    """
    buffer = io.BytesIO()
    
    # Use letter size, professional margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    story = []
    styles = create_custom_styles()
    
    # Build the report sections with page management
    # NOTE: TOC removed for more compact format
    add_cover_page(story, results, styles)
    add_executive_summary_page(story, results, styles)
    add_project_overview_page(story, results, styles)
    add_dependencies_infrastructure_page(story, results, styles)
    add_file_structure_page(story, results, styles)
    add_detailed_source_analysis_pages(story, results, styles)
    add_config_analysis_page(story, results, styles)
    add_architecture_insights_page(story, results, styles)
    add_appendix_page(story, results, styles)
    
    # Build the PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()
