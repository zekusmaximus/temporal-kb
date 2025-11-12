# kb/cli/commands/add.py

from datetime import datetime

import click

from ...core.database import get_db
from ...core.schemas import EntryCreate, EntryType
from ...services.entry_service import EntryService
from ...storage.file_manager import FileManager
from ..ui import (
    console,
    print_entry,
    print_error,
    print_success,
    prompt_for_editor,
    prompt_text,
)


@click.command()
@click.option('--title', '-t', help='Entry title')
@click.option('--content', '-c', help='Entry content (or use --editor)')
@click.option('--editor', '-e', is_flag=True, help='Open editor for content')
@click.option('--type', 'entry_type',
              type=click.Choice([t.value for t in EntryType]),
              default='note',
              help='Entry type')
@click.option('--tags', '-T', multiple=True, help='Tags (can specify multiple)')
@click.option('--project', '-p', multiple=True, help='Projects (can specify multiple)')
@click.option('--source', '-s', help='Source of the entry')
@click.option('--quick', '-q', help='Quick note: kb add -q "Your note here"')
@click.option('--template', help='Use a template (legal_case, concept, etc.)')
@click.pass_context
def add(ctx, title, content, editor, entry_type, tags, project, source, quick, template):
    """Create a new entry

    Examples:
        kb add -q "Remember to review the contract"
        kb add -t "Meeting Notes" -e --tags meeting --project ClientX
        kb add --template legal_case
    """

    db = get_db()

    try:
        # Quick mode: single-line note
        if quick:
            title = f"Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            content = quick
            entry_type = 'note'

        # Template mode
        elif template:
            title, content, entry_type, tags = _get_template(template)

        # Interactive mode
        else:
            # Prompt for title if not provided
            if not title:
                title = prompt_text("Entry title")
                if not title:
                    print_error("Title is required")
                    return

            # Get content
            if editor or (not content and not quick):
                with console.status("[bold blue]Opening editor..."):
                    initial = _get_template_content(entry_type) if not content else content
                    content = prompt_for_editor(initial)

            if not content:
                print_error("Content is required")
                return

        # Create entry
        with console.status("[bold blue]Creating entry..."):
            with db.session_scope() as session:
                file_manager = FileManager()
                entry_service = EntryService(session, file_manager)

                entry_data = EntryCreate(
                    title=title,
                    content=content,
                    entry_type=EntryType(entry_type),
                    tags=list(tags),
                    projects=list(project),
                    source=source or 'cli'
                )

                entry = entry_service.create_entry(entry_data)

        print_success(f"✓ Entry created: {entry.id}")
        print_entry(entry, show_content=False)

        # Git commit if enabled
        _git_commit(entry, "create")

    except Exception as e:
        print_error(f"Failed to create entry: {str(e)}")
        raise


def _get_template(template_name: str) -> tuple:
    """Get template content based on name"""

    templates = {
        'legal_case': {
            'title': 'Case Brief: [Case Name]',
            'content': '''# Case Brief

## Citation
[Full citation]

## Court
[Court name and jurisdiction]

## Date Decided
[YYYY-MM-DD]

## Facts
[Key facts of the case]

## Issue(s)
[Legal questions presented]

## Holding
[Court's decision]

## Reasoning
[Court's legal reasoning]

## Relevance to Practice
[How this impacts your work]

## Fiction Implications
[Speculative/worldbuilding connections if any]
''',
            'type': 'legal_case',
            'tags': ['legal', 'case-law']
        },
        'concept': {
            'title': '[Concept Name]',
            'content': '''# [Concept Name]

## Definition
[Clear, concise definition]

## Context
[Where this concept appears - Buddhist philosophy, cyberpunk, etc.]

## Related Concepts
- [Concept 1]
- [Concept 2]

## Applications in Work
### Fiction
[How this appears in your stories]

### Legal/Technical
[Professional applications if any]

## Sources
- [Source 1]
- [Source 2]

## Personal Notes
[Your thoughts, interpretations, connections]
''',
            'type': 'concept',
            'tags': ['concept']
        },
        'meeting': {
            'title': 'Meeting - [Topic] - [Date]',
            'content': '''# Meeting Notes

## Date & Time
[YYYY-MM-DD HH:MM]

## Attendees
- [Person 1]
- [Person 2]

## Agenda
1. [Topic 1]
2. [Topic 2]

## Discussion Points
[Key discussions]

## Decisions Made
- [Decision 1]
- [Decision 2]

## Action Items
- [ ] [Action 1] (@person)
- [ ] [Action 2] (@person)

## Next Steps
[What happens next]
''',
            'type': 'meeting_note',
            'tags': ['meeting']
        },
        'story_note': {
            'title': '[Story Element Name]',
            'content': '''# [Story Element]

## Project
[Which narrative project]

## Type
[Character / Setting / Plot / Theme / Technical]

## Description
[Core description]

## Thematic Connections
[Buddhist/philosophical themes, cyberpunk elements, etc.]

## Technical Considerations
[Implementation details for interactive fiction]

## Related Elements
- [Element 1]
- [Element 2]

## Development Notes
[Evolution of this idea]
''',
            'type': 'note',
            'tags': ['fiction', 'worldbuilding']
        }
    }

    template = templates.get(template_name)
    if not template:
        available = ", ".join(templates.keys())
        raise ValueError(f"Unknown template. Available: {available}")

    return (
        template['title'],
        template['content'],
        template['type'],
        template['tags']
    )


def _get_template_content(entry_type: str) -> str:
    """Get minimal template for entry type"""
    if entry_type == 'legal_case':
        return "# Case Brief\n\n## Citation\n\n## Holding\n\n"
    elif entry_type == 'concept':
        return "# Concept\n\n## Definition\n\n## Context\n\n"
    elif entry_type == 'code_snippet':
        return "# Code Snippet\n\n```python\n# Your code here\n```\n\n## Purpose\n\n"
    else:
        return "# Entry\n\n"


def _git_commit(entry, action: str):
    """Auto-commit to git if enabled"""
    from ...core.config import get_config

    config = get_config()
    if config.git_enabled and config.git_auto_commit:
        from ...storage.git_manager import GitManager

        try:
            git_mgr = GitManager(config.data_dir)
            message = f"{action.capitalize()}: {entry.title}"
            git_mgr.commit(message)
        except Exception as e:
            print_error(f"Git commit failed: {e}")
