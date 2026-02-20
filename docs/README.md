# UDP Server Manager Documentation

**Version:** 2.0  
**Last Updated:** February 19, 2026

---

## Welcome

Welcome to the UDP Server Manager documentation suite. This collection provides comprehensive guidance for using, extending, and maintaining the application.

---

## Quick Start

**New to UDP Server Manager?** Start here:

1. **[Usage Guide](usage.md)** - Complete user manual with instructions and examples
2. **[UI Components Guide](ui_components_guide.md)** - Detailed reference for all UI features
3. **[Architecture](architecture.md)** - System design and technical overview

---

## Documentation Index

### User Guides

| Document | Description | Audience |
|----------|-------------|----------|
| **[Usage Guide](usage.md)** | Complete application usage manual | All users |
| **[UI Components Guide](ui_components_guide.md)** | Detailed UI reference and keyboard shortcuts | All users |
| **[Command Menu System](command_menu_system.md)** | Hierarchical command menu customization | Power users, developers |

### Technical Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[Architecture](architecture.md)** | System architecture and design patterns | Developers, architects |
| **[Message Creator Panel](message_creator_panel.md)** | Technical reference for message creator component | Developers |
| **[Command Dictionary Tutorial](command_dictionary_tutorial.md)** | JSON command dictionary format and best practices | Developers |
| **[Configuration File Tutorial](config_file_tutorial.md)** | Application configuration reference | Developers, system admins |
| **[Servers File Tutorial](servers_file_tutorial.md)** | Device configuration (servers.json) | System admins, developers |

### Planning & Future Development

| Document | Description | Audience |
|----------|-------------|----------|
| **[Live Streaming Roadmap](live_streaming_roadmap.md)** | Future Raspberry Pi 4B streaming features | Stakeholders, developers |
| **[Project Plan](project_plan.md)** | Overall project roadmap and milestones | Project managers, stakeholders |
| **[Feature Summary](feature_summary.md)** | v2.0 feature highlights and improvements | All stakeholders |

### Maintenance & Contribution

| Document | Description | Audience |
|----------|-------------|----------|
| **[Contributing Guide](contributing.md)** | Development guidelines and contribution process | Contributors, developers |
| **[MAINTAINERS](MAINTAINERS.md)** | Project maintainer information and contacts | Contributors |

### Documentation Tools

| Document | Description | Audience |
|----------|-------------|----------|
| **[PDF Generation Guide](pdf_generation_guide.md)** | How to export documentation to professional PDFs | Documentation authors |
| **[Markdown Features Demo](markdown_features_demo.md)** | Markdown syntax examples and capabilities | Documentation authors |

---

## Version 2.0 Highlights

### Major New Features

✨ **Hierarchical Command Menu**
- Commands organized by category with flyout submenus
- Replaces flat dropdown for better scalability
- 4 default categories: Device Control, Device Status, Error Handling, System Administration

✨ **Status Panel**
- New middle-tier panel (350px height)
- Dual modes: Table view for data, Split view for text + media
- Video playback with full controls (play, pause, stop, timeline)
- Support for local video files (MP4, AVI, MOV, MKV)
- Network stream support (HTTP/HTTPS/RTSP)

✨ **Expanded Parameter Support**
- Increased from 8 to 10 parameters per command
- Enhanced conditional display logic
- Real-time validation with visual feedback

✨ **Improved UI Layout**
- Restructured to 3-tier design (Interactive 350px / Status 350px / Logging 200px)
- More efficient use of screen space
- Better organization of information

✨ **Professional Documentation**
- Comprehensive documentation suite with 14+ documents
- PDF-ready formatting (Arial 9pt, 0.5" margins, Letter size)
- Complete usage guides, technical references, and roadmaps

### Future Capabilities (Planned)

🔮 **Raspberry Pi 4B Live Streaming** (Future Phase)
- CSI camera integration
- Real-time H.264 streaming over network
- Multi-camera support
- Recording and overlays
- See [Live Streaming Roadmap](live_streaming_roadmap.md)

---

## Documentation by Use Case

### I want to...

**Use the application**
→ Start with [Usage Guide](usage.md)

**Understand the UI**
→ Read [UI Components Guide](ui_components_guide.md)

**Add a new device**
→ Follow [Servers File Tutorial](servers_file_tutorial.md) and [Command Dictionary Tutorial](command_dictionary_tutorial.md)

**Add new commands**
→ See [Command Dictionary Tutorial](command_dictionary_tutorial.md), section "Adding New Commands"

**Customize the command menu**
→ Check [Command Menu System](command_menu_system.md)

**Understand the system architecture**
→ Review [Architecture](architecture.md)

**Contribute code**
→ Read [Contributing Guide](contributing.md)

**Export docs to PDF**
→ Follow [PDF Generation Guide](pdf_generation_guide.md)

**Plan future features**
→ Consult [Live Streaming Roadmap](live_streaming_roadmap.md) and [Project Plan](project_plan.md)

---

## Getting Help

### Documentation Issues

If you find errors, outdated information, or unclear explanations in the documentation:

1. Check if issue already reported in project issue tracker
2. Verify you're reading the correct version (v2.0 or later)
3. Report issue with document name, section, and description of problem
4. Suggest improvements if you have ideas

### Application Issues

For problems with the application itself:

1. Check [Usage Guide](usage.md) Troubleshooting section
2. Review [UI Components Guide](ui_components_guide.md) for feature-specific issues
3. Check error messages in logging panel
4. Report bug with steps to reproduce

### Feature Requests

To request new features:

1. Review [Project Plan](project_plan.md) and [Live Streaming Roadmap](live_streaming_roadmap.md)
2. Check if feature already planned
3. Submit feature request with clear description and use case
4. Explain benefits and priority

---

## Document Conventions

### Formatting Standards

**Headings:**
- H1 (`#`) - Document title only
- H2 (`##`) - Major sections
- H3 (`###`) - Subsections
- H4 (`####`) - Sub-subsections (use sparingly)

**Code:**
- Inline code: \`code\`
- Code blocks: \`\`\`language ... \`\`\`
- File paths: Use absolute paths with proper separators

**Links:**
- Internal docs: `[Link Text](filename.md)`
- Sections: `[Link Text](filename.md#section-name)`
- External: `[Link Text](https://example.com)`

**Text Styling:**
- **Bold** for UI elements, important terms
- *Italic* for emphasis
- `Code font` for commands, code, file names

### Version Information

All documentation includes header with:
- **Document Version:** X.X
- **Last Updated:** Date
- **Application Version:** UDP Server Manager vX.X+

---

## PDF Generation

### Quick PDF Export

**Single Document:**
```bash
cd docs
markdown-pdf usage.md -s pdf-style.css -o usage.pdf
```

**All Documents:**
```powershell
cd docs
foreach ($file in Get-ChildItem *.md) {
    markdown-pdf $file.Name -s pdf-style.css -o "$($file.BaseName).pdf"
}
```

**See:** [PDF Generation Guide](pdf_generation_guide.md) for detailed instructions.

---

## Maintenance Schedule

### Regular Updates

**After Each Release:**
- [ ] Update version numbers in all docs
- [ ] Update "Last Updated" dates
- [ ] Review and update feature lists
- [ ] Regenerate PDFs
- [ ] Test all internal links

**Quarterly:**
- [ ] Review all documentation for accuracy
- [ ] Update screenshots if UI changed
- [ ] Check for broken external links
- [ ] Solicit feedback from users
- [ ] Update roadmap documents

**As Needed:**
- [ ] New features → update relevant guides
- [ ] Bug fixes → update troubleshooting sections
- [ ] API changes → update technical references
- [ ] Architecture changes → update architecture.md

---

## Contributing to Documentation

We welcome documentation improvements! See [Contributing Guide](contributing.md) for:

- Documentation style guide
- How to submit documentation changes
- Review process
- Documentation testing procedures

**Good Documentation:**
- Clear and concise
- Includes examples
- Covers edge cases
- Tested by someone other than author
- Follows formatting conventions
- Properly linked from index

---

## Credits

### Documentation Authors

- Primary author: Project Team
- Contributors: See [MAINTAINERS.md](MAINTAINERS.md)
- Technical reviewers: Development Team

### Tools Used

- **Markdown:** Documentation format
- **markdown-pdf:** PDF generation
- **VS Code:** Document authoring
- **Git:** Version control

---

## Contact

For documentation feedback or questions:

- **Project Repository:** [Link to repository]
- **Issue Tracker:** [Link to issues]
- **Email:** [Contact email]

---

**Last Updated:** February 19, 2026  
**Documentation Version:** 2.0  
**Application Version:** UDP Server Manager v2.0+
