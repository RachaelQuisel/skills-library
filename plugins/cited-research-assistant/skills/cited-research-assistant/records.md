# Record format

This example is fictional test data, not a real paper or research finding. Replace it with actually retrieved evidence in normal use.

```json
{
  "sources": [{
    "source_id": "s1",
    "identifier": "fictional-fixture-v1",
    "url": "https://example.org/fixture",
    "title": "Fictional fixture source",
    "authors": null,
    "submitted_date": null,
    "publication_date": null,
    "retrieved_at": "2026-10-03T00:00:00Z",
    "scope": "abstract",
    "publication_status": "preprint",
    "content": "The fixture sample contained 12 participants.",
    "external_ids": {}
  }],
  "claims": [{
    "claim_id": "c1",
    "text": "The fixture sample contained 12 participants.",
    "kind": "substantive",
    "status": "supported",
    "inference": false,
    "support_review": "The supplied fictional abstract explicitly states the sample size.",
    "evidence": [{
      "source_id": "s1",
      "passage": "sample contained 12 participants",
      "relationship": "supports"
    }]
  }, {
    "claim_id": "c2",
    "text": "The fixture randomized allocation.",
    "status": "unverifiable",
    "reason": "The supplied abstract does not describe allocation.",
    "reason_source_ids": ["s1"],
    "evidence": []
  }]
}
```

`kind: bibliographic` permits metadata evidence for bibliographic claims; substantive claims need an abstract or full text. `contradicted` needs at least one `contradicts` passage. `unverifiable` can have no evidence, or both supporting and contrary passages when sources disagree. A `supported` record cannot hide contrary evidence.

Each `text` and selected `passage` is one line. Stored source content may span multiple lines. Missing author/date information stays null. `reason_source_ids` adds citations for source descriptions in a refusal explanation; an empty list is appropriate when the explanation only states that no evidence was retrieved. The tool checks structure and exact membership; Claude or the user must still review whether each passage and explanation actually matches the source.
