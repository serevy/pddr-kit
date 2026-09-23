# Repository rulesets

This directory keeps the reviewed, source-controlled form of the GitHub repository rulesets used by PDDR Kit.

## protect-main.json

`protect-main.json` mirrors the active `protect-main` policy for the default branch:

- require changes through pull requests
- block branch deletion
- block force pushes
- require linear history
- require the always-on `validate` GitHub Actions check
- require the branch to be up to date before merging

The JSON intentionally omits GitHub-generated identifiers and timestamps so it can be reviewed and imported again.

## Consumer repositories

When reusing this ruleset in another repository, keep the common branch protections and replace the required status check with an **always-on pull-request check for that repository**. Do not require a workflow that is filtered by `paths`, because a pull request outside those paths can otherwise be left waiting for a check that never runs.

For current PDDR Kit consumers using hardened Checkpoint CI, `checkpoint` is the recommended required check because the signal workflow runs on every pull request.

## Applying the file

Merging this file does not change GitHub repository settings automatically. Review the JSON in a pull request first, then import it from:

`Settings -> Rules -> Rulesets -> New ruleset -> Import a ruleset`

Review the imported settings before creating the ruleset.
