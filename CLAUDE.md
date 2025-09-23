# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static website for the Save Birchanger campaign, opposing a large-scale development on Green Belt land between Stansted Mountfitchet and Birchanger in Essex, UK.

## Build and Development Commands

This is a simple static HTML site with no build process required. Common commands:

```bash
# View the site locally
python3 -m http.server 8000    # Then open http://localhost:8000

# Deploy to GitHub Pages (if configured)
git add -A && git commit -m "Update site" && git push origin main
```

## Architecture

The website consists of:
- **index.html** - Single-page static site with embedded CSS and JavaScript
- **img/** - Image assets directory containing photos of Birchanger village
- All styling is embedded within the HTML file for simplicity
- Minimal JavaScript for smooth scrolling and newsletter form handling

## Key Development Considerations

### Styling
- The site uses inline CSS within the HTML file
- Color scheme: Green (#2c5f2d, #4a7c59) for environmental theme, red (#ff6b6b) for action buttons
- Responsive design with mobile breakpoints at 768px

### Images
- Images are stored in the `img/` directory
- Current images: church.jpg, Woods.jpg, ThreeWillows.jpg, Fields.jpg, Walks.jpg, village green.jpg, header.jpg

### Content Sections
The site is organized into distinct sections:
- Hero banner with call-to-action buttons
- Alert banner for urgent updates
- About section explaining the threat
- Statistics display
- Impact list
- "Grey Belt" explanation
- Action cards for community involvement
- Birchanger showcase with image gallery
- Newsletter signup form
- Contact information
- Footer with resources and links

### External Links
- Facebook group: https://www.facebook.com/groups/2568902686636114
- Email link to councillor: Cllr.Ray.Gooding@essex.gov.uk
- Birchanger Parish Council: https://www.birchanger.com/
- CPRE Essex: https://cpressex.org.uk/

## Deployment

The site is deployed via GitHub Pages from the main branch. Any commits pushed to main will automatically update the live site.