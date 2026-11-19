// Bulk schema fetch — one round-trip instead of N MCP describe_table calls.
// Substitute APP_ID and SECRET_SOCKET_ID before running via evaluate_script.
//
// Returns an array of { id, name, fields: [{id,name,type,choices?}], views: [{id,name,type}] }
//
// Why bulk: on a large base (29 tables, 1300+ fields), per-table MCP
// describe_table calls cost ~18 sequential round-trips. This endpoint returns
// the full schema in one call (~90KB JSON).
//
// Caveat — personal views: the application-level read endpoint OMITS views
// that have `personalForUserId` set (per-user grids, sandboxes). If a
// trigger's viewId is missing from the result, fall back to
// mcp__airtable__describe_table on that table at `identifiersOnly`, which
// does include personal views. The SKILL.md "Phase 2c" describes the
// supplemental fetch flow.
//
// Caveat — select option resolution: this fetch captures `choicesById` for
// singleSelect/multiSelect fields, so the Python parser can render option
// IDs (selXXX) as their human names instead of opaque IDs in filter
// formulas and trigger conditions.

async function fetchSchema() {
  const appId = 'APP_ID';
  const secretSocketId = 'SECRET_SOCKET_ID';
  const headers = {
    'x-requested-with': 'XMLHttpRequest',
    'x-airtable-application-id': appId,
    'x-airtable-inter-service-client': 'webClient',
    'x-time-zone': 'America/Chicago',
    'x-user-locale': 'en',
    'accept': 'application/json'
  };

  const params = encodeURIComponent(JSON.stringify({
    shouldIncludeSchemaChecksum: false,
    mayOnlyIncludeRowAndCellDataForIncludedViews: true,
    mayExcludeCellDataForLargeViews: true,
    allowMsgpackOfResult: false,
    canClientSupportPreviewMode: true,
  }));
  const url = `https://airtable.com/v0.3/application/${appId}/read?stringifiedObjectParams=${params}&requestId=reqSchemaAll&secretSocketId=${secretSocketId}`;
  const r = await fetch(url, { credentials: 'include', headers });
  const d = await r.json();
  const data = d.data || d;
  const tableSchemas = data.tableSchemas || [];

  // Extract select choices (id → name) from singleSelect / multiSelect fields.
  // typeOptions.choices is { [choiceId]: { id, name, color } } in the v0.3 shape.
  const extractChoices = (col) => {
    const typeOpts = col.typeOptions || (col.fieldType && col.fieldType.options) || null;
    if (!typeOpts) return null;
    const choices = typeOpts.choices || typeOpts.choicesById || null;
    if (!choices) return null;
    const out = {};
    for (const cid of Object.keys(choices)) {
      const c = choices[cid];
      if (c && c.name) out[cid] = c.name;
    }
    return Object.keys(out).length ? out : null;
  };

  return tableSchemas.map(t => ({
    id: t.id,
    name: t.name,
    fields: (t.columns || t.fields || []).map(c => {
      const out = { id: c.id, name: c.name, type: c.type || (c.fieldType && c.fieldType.type) || null };
      const choices = extractChoices(c);
      if (choices) out.choices = choices;
      return out;
    }),
    views: (t.viewOrder || []).map(vid => {
      const v = (t.viewsById && t.viewsById[vid]) || null;
      return v ? { id: v.id, name: v.name, type: v.type } : { id: vid, name: null };
    }),
  }));
}

return fetchSchema();
