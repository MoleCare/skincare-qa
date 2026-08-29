# Maintainer checklist (GitHub UI or `gh`)

Do this once on each public repo after the first push. The agent will not
change GitHub settings for you.

## Branch protection (`main`)

- Require a pull request before merging
- Require 1 approving review
- Require status checks: `test`
- Do not allow force pushes
- Do not allow deletions

## Security

- Enable Dependabot alerts
- Enable the Security tab private vulnerability reporting
- Confirm `SECURITY.md` is the contact path (`info@molecare.co.uk`)

## Labels (optional)

`bug`, `enhancement`, `good first issue`, `needs-triage`

`skin-care-harness` stays private until you choose to publish it. CI here
skips those tests when the package is not checked out.
