# Code Review Notes (Complete after reviewing the running project)

Record actual review findings rather than assumed results.

## Review checklist
- [ ] Routes have clear responsibilities and HTTP methods.
- [ ] SQL statements use parameterized values.
- [ ] User-provided text is validated and rendered through Jinja auto-escaping.
- [ ] Invalid category and status filters are handled safely.
- [ ] State transitions prevent accepting a non-open request.
- [ ] Tests cover successful and unsuccessful workflows.
- [ ] README contains setup, test, and Docker instructions.
- [ ] `.gitignore` excludes local databases, virtual environments, and secrets.

## Findings template
For every finding, record the file/function, severity, observation, evidence, recommended correction, and verification after correction.

## Known prototype limitations
- No authentication or role-based authorization.
- The default secret key is for local development only.
- No moderation, notifications, or verified emergency-response workflow.
- User display names are not verified identities.
- Do not deploy for real emergency handling without a security and privacy review.
