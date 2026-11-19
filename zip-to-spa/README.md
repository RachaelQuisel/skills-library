# ZIP code to Service Planning Area

Use this skill to look up the Los Angeles County Service Planning Area associated with one or more ZIP codes. It uses the county's public geographic data and reports the selected area, the source, and any unresolved result.

Give the assistant the ZIP codes you want checked. A ZIP code can overlap more than one area; the bundled script selects the area with the largest qualifying overlap. A ZIP code outside the available county data can remain unresolved. Review unresolved results before using them in a client record.

The working instructions and command examples are in [SKILL.md](SKILL.md). The lookup script is in [scripts/zip_to_spa.py](scripts/zip_to_spa.py). It requires Python and the dependencies listed in the instructions, plus access to the county's public data service.

RachaelQuisel maintains this skill. Its files are registered in the repository's maintenance inventory. The scheduled maintenance check does not call the county service or verify the geographic results. Those capabilities remain unverified by that check.
