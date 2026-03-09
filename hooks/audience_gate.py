"""
MkDocs hook: audience-based content gating.

Strips content blocks based on the `extra.audience` config variable.
Uses HTML comment markers that are invisible in markdown editors/previews.

Usage in markdown:

    <!-- @public -->
    Content shown for public and internal audiences (hidden from enterprise).
    <!-- @/public -->

    <!-- @enterprise -->
    Content shown only for enterprise audience.
    <!-- @/enterprise -->

    <!-- @internal -->
    Content shown only for internal audience (hidden from both enterprise and public).
    <!-- @/internal -->

Audience hierarchy:
    internal  — sees @public and @internal content
    public    — sees @public content only
    enterprise — sees @enterprise content only

Markers are case-insensitive and whitespace-tolerant.
Content is fully removed at build time (not CSS-hidden).
"""

import re

_GATE_PATTERN = re.compile(
    r'<!-- @(public|enterprise|internal)\s*-->(.*?)<!-- @/\1\s*-->',
    re.DOTALL | re.IGNORECASE,
)


def on_page_markdown(markdown, page, config, files):
    audience = config.get('extra', {}).get('audience', 'public')

    def _replace(match):
        tag = match.group(1).lower()
        content = match.group(2)

        # @public: visible to internal + public, hidden from enterprise
        if tag == 'public' and audience == 'enterprise':
            return ''

        # @enterprise: visible only to enterprise
        if tag == 'enterprise' and audience != 'enterprise':
            return ''

        # @internal: visible only to internal
        if tag == 'internal' and audience != 'internal':
            return ''

        return content

    return _GATE_PATTERN.sub(_replace, markdown)
