# JSON Resume - Kirill Demidov

A professional resume/CV built using the JSON Resume standard and rendered as a modern web page.

## About

This repository contains my professional resume in JSON format, following the [JSON Resume](https://jsonresume.org/) schema, along with a styled HTML presentation.

## Files

- `cv_Kirill_Demidov_DE.json` - Resume data in JSON Resume format
- `resume.html` - Styled HTML presentation of the resume
- `index.css` - Styling for the resume presentation

## Features

- **JSON Resume Standard**: Follows the official JSON Resume schema v1.0.0
- **Responsive Design**: Mobile-friendly layout that works on all devices
- **Modern Styling**: Clean, professional appearance with dark/light mode support
- **Print Optimized**: Designed to look great both on screen and when printed
- **Semantic HTML**: Well-structured markup for accessibility

## View Resume

To view the resume:

1. Open `resume.html` in your web browser
2. Or visit the live version (if hosted)

## JSON Resume Schema

The resume follows the standard JSON Resume schema which includes:
- Basic information and contact details
- Professional summary
- Work experience
- Education
- Skills
- Projects
- Languages
- References

## Technical Details

- **Schema**: JSON Resume v1.0.0
- **Styling**: Modern CSS with CSS Grid and Flexbox
- **Typography**: Lato font family
- **Color Scheme**: Adaptive light/dark theme support
- **Icons**: Integrated icon support for contact methods

## About the Person

**Kirill Demidov** - Data Engineer Team Lead with expertise in BI, analytics, and large-scale data systems. Proficient in cloud data platforms, pipeline orchestration, and leading engineering teams to build scalable data solutions.

## Contact

- **Location**: Tel Aviv, Israel
- **LinkedIn**: [linkedin.com/in/kirill-demidov-72711317](https://www.linkedin.com/in/kirill-demidov-72711317/)
- **GitHub**: [github.com/kirill-demidov](https://github.com/kirill-demidov)

## Usage

This resume format can be used with:
- JSON Resume CLI tools
- Online resume builders
- Custom resume applications
- Print/PDF generation tools

To validate the JSON structure, you can use the official JSON Resume validator or schema validation tools.
## Editing

`index.html` is generated — do not edit it by hand.

The source of truth is `cv_Kirill_Demidov_DE.json` ([JSON Resume](https://jsonresume.org/)
schema). Change it, then rebuild:

```sh
python3 build.py            # regenerate index.html
python3 build.py --check    # fail if index.html is out of date
```

The GitHub Actions workflow rebuilds before publishing, so the live page always
matches the JSON even if a stale `index.html` is committed. This replaced a
hand-written copy of the same data, which had already drifted: a renamed
employer had to be fixed in two files, the skill list in the markup had
overtaken the JSON, and seven public repositories were missing from Key
Projects entirely.

## Keeping LinkedIn in step

There is no two-way sync to build: LinkedIn has no API for writing profile data,
and automating the browser breaks its user agreement. Reading the full profile
is equally unavailable. The one legitimate channel is the official export —
Settings → Data privacy → Get a copy of your data.

So `check_linkedin.py` is a watchdog, not a sync. It reports what has drifted;
you fix it, here or there.

```sh
python3 check_linkedin.py ~/Downloads/Basic_LinkedInDataExport_*.zip
```

It reads only the profile files in the archive. The export also contains
connections, messages and phone numbers — do not commit it.
