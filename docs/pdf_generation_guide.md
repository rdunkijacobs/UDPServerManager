# PDF Generation Guide

**Document Version:** 1.0  
**Last Updated:** February 19, 2026  
**Application Version:** UDP Server Manager v2.0+

---

## Overview

This guide explains how to generate professional PDF documents from the markdown documentation files in the UDP Server Manager project. All documentation is pre-formatted for optimal PDF output on 8.5" x 11" (US Letter) paper.

### PDF Specifications

- **Paper Size:** 8.5" x 11" (US Letter)
- **Base Font:** Arial  
- ** Font Size:** 9pt for body text
- **Margins:** 0.5" on all sides (narrow margins)
- **Headers/Footers:** Automatic page numbering and document identification
- **Styling:** Professional appearance via `docs/pdf-style.css`

---

## Prerequisites

### Required Software

#### Option 1: markdown-pdf (Node.js)

**Install Node.js** (if not already installed):
- Download from [nodejs.org](https://nodejs.org/)
- Install LTS version (recommended)
- Verify installation: `node --version`

**Install markdown-pdf:**
```bash
npm install -g markdown-pdf
```

**Verify installation:**
```bash
markdown-pdf --version
```

#### Option 2: Pandoc + LaTeX

**Install Pandoc:**
- Download from [pandoc.org](https://pandoc.org/installing.html)
- Windows: Use installer (pandoc-x.xx-windows-x86_64.msi)
- Add to PATH during installation

**Install LaTeX Distribution:**
- Windows: MiKTeX from [miktex.org](https://miktex.org/)
- Or: TeX Live from [tug.org/texlive](https://tug.org/texlive/)

**Verify installations:**
```bash
pandoc --version
pdflatex --version
```

#### Option 3: Print to PDF (Built-in)

**Requirements:**
- Web browser (Chrome, Firefox, Edge)
- Markdown preview extension (if needed)
- Print to PDF capability (built into most modern browsers)

---

## Method 1: Using markdown-pdf (Recommended)

### Basic Conversion

**Single Document:**
```bash
cd docs
markdown-pdf architecture.md -s pdf-style.css -o architecture.pdf
```

**Multiple Documents:**
```bash
markdown-pdf architecture.md usage.md -s pdf-style.css
```

Creates `architecture.pdf` and `usage.pdf` in same directory.

### Batch Conversion Script

**PowerShell Script** (`generate_pdfs.ps1`):
```powershell
# Generate PDFs for all markdown files in docs folder

$docsPath = "docs"
$stylePath = "docs/pdf-style.css"

# Get all markdown files
$mdFiles = Get-ChildItem -Path $docsPath -Filter "*.md"

foreach ($file in $mdFiles) {
    $inputPath = $file.FullName
    $outputPath = $inputPath -replace '\.md$', '.pdf'
    
    Write-Host "Converting $($file.Name)..."
    markdown-pdf $inputPath -s $stylePath -o $outputPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Created $outputPath" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to convert $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "`nPDF generation complete!" -ForegroundColor Cyan
```

**Run Script:**
```bash
cd C:\...\UDPServerManager
powershell -ExecutionPolicy Bypass -File generate_pdfs.ps1
```

### Advanced Options

**Custom Page Size:**
```bash
markdown-pdf doc.md -s pdf-style.css --paper-format Letter
```

**Custom Margins:**
```bash
markdown-pdf doc.md -s pdf-style.css --paper-border 0.5in
```

**Include Table of Contents:**
```bash
markdown-pdf doc.md -s pdf-style.css --toc
```

---

## Method 2: Using Pandoc

### Basic Conversion

**Simple PDF:**
```bash
cd docs
pandoc architecture.md -o architecture.pdf --pdf-engine=pdflatex
```

**With CSS Styling:**
```bash
pandoc architecture.md -o architecture.pdf \
  --css=pdf-style.css \
  --pdf-engine=pdflatex \
  --variable=geometry:margin=0.5in \
  --variable=fontsize=9pt \
  --variable=mainfont="Arial"
```

### Template-Based Conversion

**Create Pandoc Template** (`pandoc-template.tex`):
```latex
\documentclass[9pt,letterpaper]{article}
\usepackage[margin=0.5in]{geometry}
\usepackage{fontspec}
\setmainfont{Arial}
\usepackage{hyperref}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhead{}
\fancyfoot{}
\fancyfoot[R]{\thepage}
\fancyfoot[L]{UDP Server Manager Documentation}

\begin{document}
$body$
\end{document}
```

**Use Template:**
```bash
pandoc architecture.md -o architecture.pdf \
  --template=pandoc-template.tex \
  --pdf-engine=xelatex
```

### Batch Conversion (Windows)

**Batch File** (`generate_pdfs.bat`):
```batch
@echo off
cd docs

for %%f in (*.md) do (
    echo Converting %%f...
    pandoc "%%f" -o "%%~nf.pdf" ^
      --css=pdf-style.css ^
      --pdf-engine=pdflatex ^
      --variable=geometry:margin=0.5in ^
      --variable=fontsize=9pt
)

echo.
echo PDF generation complete!
pause
```

---

## Method 3: Browser Print to PDF

### Setup

1. **Install Markdown Preview Extension:**
   - Visual Studio Code: "Markdown Preview Enhanced" or "Markdown All in One"
   - Or use online viewer: [dillinger.io](https://dillinger.io/)

2. **Open Markdown File:**
   - In VS Code: Right-click file → "Open Preview"
   - Or: Double-click in GitHub Desktop
   - Or: Upload to online markdown viewer

3. **Print to PDF:**
   - Press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
   - Select "Microsoft Print to PDF" or "Save as PDF"
   - Click "More settings"
   - Set:
     - **Paper size:** Letter
     - **Margins:** Custom (0.5 in all sides)
     - **Headers/footers:** On
   - Click "Save"

### Browser-Specific Instructions

**Chrome/Edge:**
1. Open markdown preview
2. `Ctrl+P` → Destination: "Save as PDF"
3. More settings:
   - Paper size: Letter
   - Margins: Custom → 0.5" all sides
   - Options: Check "Background graphics"
4. Save

**Firefox:**
1. Open markdown preview
2. `Ctrl+P` → Print using system dialog
3. Select Microsoft Print to PDF
4. Properties → Paper: Letter, Margins: Narrow
5. Print

---

## CSS Customization

### Modifying pdf-style.css

The stylesheet is located at `docs/pdf-style.css`. Key settings:

**Page Setup:**
```css
@page {
    size: letter;  /* 8.5 x 11 inches */
    margin-top: 0.5in;
    margin-bottom: 0.6in;
    margin-left: 0.5in;
    margin-right: 0.5in;
}
```

**Body Font:**
```css
body {
    font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
    font-size: 9pt;
    line-height: 1.4;
}
```

**Headings:**
```css
h1 {
    font-size: 16pt;
    font-weight: bold;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
}
```

### Custom Company Branding

**Add Logo to Header:**
```css
@page {
    @top-left {
        content: url('company-logo.png');
        width: 1in;
    }
}
```

**Custom Footer:**
```css
@page {
    @bottom-left {
        content: "Company Name - Confidential";
        font-size: 8pt;
        color: #666;
    }
}
```

---

## Quality Assurance

### Pre-Generation Checklist

- [ ] All markdown files have proper frontmatter
- [ ] Code blocks use syntax highlighting language tags
- [ ] Tables are well-formatted
- [ ] Images have alt text and proper paths
- [ ] Links are valid (internal and external)
- [ ] Document version and date are current

### Post-Generation Verification

**Visual Inspection:**
1. **Page Breaks:** No awkward breaks mid-paragraph or after headings
2. **Tables:** All tables fit within margins
3. **Code Blocks:** Syntax highlighting applied, no overflow
4. **Images:** Clear, properly sized, not pixelated
5. **Headers/Footers:** Present on all pages, correct numbering

**Content Verification:**
1. **Table of Contents:** Accurate page numbers (if included)
2. **Links:** Clickable and functional
3. **Font Consistency:** Arial throughout
4. **Spacing:** Appropriate white space, not cramped

**Technical Validation:**
1. **File Size:** Under 5MB per document (typical)
2. **Resolution:** 300 DPI for images
3. **Searchability:** Text is selectable and searchable
4. **Accessibility:** PDF/A compliant (optional)

---

## Troubleshooting

### Issue: Fonts not applied

**Cause:** Font not installed or name mismatch  
**Solution:**
- Verify Arial installed: `Control Panel → Fonts`
- Use fallback fonts: `"Helvetica Neue", Helvetica, sans-serif`
- Install font family if missing

### Issue: Code blocks hard to read

**Cause:** Font size too small or no monospace font  
**Solution:**
- Increase code font size in CSS: `pre { font-size: 8pt; }`
- Ensure Courier New installed
- Add background color for contrast

### Issue: Images not appearing

**Cause:** Relative paths not resolved  
**Solution:**
- Use absolute paths when possible
- Copy images to same directory as markdown file
- Check image file extension matching (case-sensitive on some systems)

### Issue: Page breaks in wrong places

**Cause:** CSS page-break rules not applied  
**Solution:**
- Add `page-break-inside: avoid` to elements
- Use `page-break-before: always` for major sections
- Check PDF generator supports CSS page break properties

### Issue: Links not clickable

**Cause:** PDF generator doesn't preserve hyperlinks  
**Solution:**
- Use Pandoc which preserves links
- Or: Manually add links in PDF editor afterward
- Verify `\usepackage{hyperref}` in LaTeX template

---

## Automation

### Continuous PDF Generation

**Watch for Changes** (using Node.js):
```javascript
// watch-and-generate.js
const chokidar = require('chokidar');
const { exec } = require('child_process');

const watcher = chokidar.watch('docs/*.md');

watcher.on('change', (path) => {
    console.log(`${path} changed, regenerating PDF...`);
    const pdfPath = path.replace('.md', '.pdf');
    exec(`markdown-pdf ${path} -s docs/pdf-style.css -o ${pdfPath}`, 
        (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                return;
            }
            console.log(`✓ Generated ${pdfPath}`);
        });
});

console.log('Watching for markdown file changes...');
```

**Run Watcher:**
```bash
node watch-and-generate.js
```

### Git Pre-commit Hook

**Automatically generate PDFs before commit:**

`.git/hooks/pre-commit`:
```bash
#!/bin/bash

echo "Generating PDFs from markdown..."

cd docs
for md in *.md; do
    pdf="${md%.md}.pdf"
    markdown-pdf "$md" -s pdf-style.css -o "$pdf"
    git add "$pdf"
done

echo "PDFs generated and staged."
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Distribution

### PDF Package Creation

**Create Distribution ZIP:**
```powershell
# Package all PDFs for distribution
$timestamp = Get-Date -Format "yyyyMMdd"
$archiveName = "UDPServerManager_Docs_$timestamp.zip"

$pdfFiles = Get-ChildItem -Path docs -Filter "*.pdf"

Compress-Archive -Path $pdfFiles -DestinationPath $archiveName

Write-Host "Created $archiveName with $($pdfFiles.Count) PDFs"
```

### Document Versioning

Include version info in PDF filename:
```bash
# Example: architecture_v2.0_20260219.pdf
cp architecture.pdf "architecture_v2.0_$(date +%Y%m%d).pdf"
```

---

## Best Practices

### Markdown Authoring for PDF

1. **Use ATX Headings:** `# Heading` not `Heading\n=======`
2. **Limit Table Width:** Keep tables under 80 characters wide
3. **Code Block Language:** Always specify: ` ```python ` not just ` ``` `
4. **Alt Text for Images:** `![Description](image.png)` for accessibility
5. **Relative Links:** Use relative paths for intra-document links
6. **Page Breaks:** Add `---` where you want manual page breaks
7. **Avoid Deep Nesting:** Keep lists and headings 3 levels deep maximum

### Professional Presentation

- **Consistent Formatting:** Use same heading styles throughout
- **White Space:** Don't crowd content, let it breathe
- **Logical Structure:** Clear hierarchy from title to sections to subsections
- **Professional Language:** Clear, concise, free of colloquialisms
- **Spell Check:** Run through spell checker before generation
- **Peer Review:** Have someone review before distribution

### Maintenance

- **Regular Updates:** Regenerate PDFs when markdown changes
- **Version Control:** Track PDFs in Git or separate archive
- **Changelog:** Maintain document revision history
- **Archive Old Versions:** Keep previous versions for reference
- **Naming Convention:** Use consistent naming across all documents

---

## Complete Workflow Example

**End-to-End PDF Generation:**

1. **Write/Update Markdown:**
   ```markdown
   # My Document
   
   Content here...
   ```

2. **Validate Markdown:**
   - Check syntax with linter
   - Preview in VS Code
   - Test internal links

3. **Generate PDF:**
   ```bash
   markdown-pdf my_document.md -s pdf-style.css -o my_document.pdf
   ```

4. **Quality Check:**
   - Open PDF and review all pages
   - Verify formatting and layout
   - Check page numbers and header/footer

5. **Version and Archive:**
   ```bash
   cp my_document.pdf "archive/my_document_v1.0_$(date +%Y%m%d).pdf"
   ```

6. **Commit to Repository:**
   ```bash
   git add my_document.md my_document.pdf
   git commit -m "Update my_document with new features"
   git push
   ```

---

## Resources

### Tools

- **markdown-pdf:** [npm markdown-pdf](https://www.npmjs.com/package/markdown-pdf)
- **Pandoc:** [pandoc.org](https://pandoc.org/)
- **MiKTeX:** [miktex.org](https://miktex.org/)
- **VS Code Markdown Extensions:** [marketplace.visualstudio.com](https://marketplace.visualstudio.com/)

### References

- **Markdown Guide:** [markdownguide.org](https://www.markdownguide.org/)
- **CSS Paged Media:** [w3.org/TR/css-page-3](https://www.w3.org/TR/css-page-3/)
- **PDF/A Standard:** [pdfa.org](https://www.pdfa.org/)

---

## Related Documentation

- **Architecture:** See `architecture.md` for system architecture
- **UI Components:** See `ui_components_guide.md` for UI details
- **Command Menu System:** See `command_menu_system.md`
- **Usage Guide:** See `usage.md` for application usage

---

**Note:** This document itself can be converted to PDF using the methods described herein. Use `pdf-style.css` for optimal formatting.
