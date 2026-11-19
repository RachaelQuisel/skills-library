# Keep one current source

Edit the canonical skill path recorded in `release-registry.json`. Bundled copies are generated exports. Keep private operating instructions in private repositories. Preserve public adaptations and third-party attribution.

The registry is the version authority. Each plugin and its bundled skills use the same version. The collection that carries several plugins has its own collection version. Every maintained release starts at 1.0.0 or higher. Historical releases remain in Git history.

## Make a change

1. Edit the canonical instructions and their guide. Use plain English for explanations. Preserve exact commands, conditions, permissions, and required product terms.
2. Bump the affected version in the registry and skill frontmatter. For a plugin, bump its package and all bundled skills together. Edit a template when the registry names one, then run that repository's generator.
3. Run `python3 scripts/release_sync.py --write`, then `python3 scripts/release_sync.py`. The first command updates local exports and manifests. The check rejects changed instructions accepted without a version bump.
4. When adding or restoring a skill, register its actual path, owner, guide, and baseline in `maintenance/collection.json` in the same change. Keep live compatibility unverified until it has its own evidence. Install `maintenance/requirements.txt` and run `python3 maintenance/run_checks.py --output /tmp/skill-check-results --check-base HEAD^`. This runs release consistency, inventory validation, and all registered regression suites, retaining both reports if one check fails. Run any further checks required by the changed behavior. Review the diff, commit, and push without overwriting other work. Verify the combined Skill checks workflow on the pushed commit before reporting success. The inventory checker reads the committed file tree; recheck after committing newly added files.
5. Update the existing ChatGPT plugin by its saved identity. Build its files from these canonical sources. Read back the saved version and instructions. Do not create a replacement plugin for an update.
6. Update the existing Claude listing to the pushed source. Check the portal's validation and review state. A GitHub push is not proof of approval or a live listing.
7. Update the existing public catalog record. Keep its ID, notes, icons, aliases, and publication evidence. Put platform versions inside that record. Never publish private skill bodies or mark a blocked check as current.

This repository's check covers local files. ChatGPT uploads, Claude reviews, and catalog deployment need their own verification. If a destination cannot be updated, record the exact pending step. Do not claim that all destinations are synchronized.

For a catalog plugin, keep its existing identity and package root in `maintenance/plugin-sync.json`. Register any added, removed, or renamed packaged file there, with its canonical repository and path. Generated provenance and known export adaptations have explicit rules. The registry and actual source manifests remain the version authority. After an approved release, compare the current saved archive and deployed catalog before refreshing the private observation. The hourly check detects drift; it does not publish a repair or submit anything to Anthropic.
