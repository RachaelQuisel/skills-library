// View filter capture for "Record enters view" triggers.
// Substitute APP_ID, SECRET_SOCKET_ID, and TARGETS (an array of
// { tableId, viewId, name }) before running via evaluate_script.
//
// Why this exists: the documented endpoints (Airtable MCP describe_table at
// `full`, or /v0.3/application/{appId}/read with includeDataForViewIds) return
// only the view's metadata header — name, columnOrder, lock, etc. — and DO
// NOT include the filter expression itself. The endpoint that actually returns
// the filter is /v0.3/view/{viewId}/readData. We discovered this by trial
// during an earlier run; encoding it here so the next run gets it for free.
//
// Returns: { [viewId]: { tableId, name, filterRaw, filterRendered } }
//   filterRaw      — the Airtable filterSet/conjunction object, preserved
//                    in case the parser wants to do its own rendering
//   filterRendered — a readable formula string using fldXXX columnIds; the
//                    Python parser substitutes field names downstream

async function fetchViewFilters() {
  const appId = 'APP_ID';
  const secretSocketId = 'SECRET_SOCKET_ID';
  const targets = TARGETS; // [{ tableId, viewId, name? }]

  const headers = {
    'x-requested-with': 'XMLHttpRequest',
    'x-airtable-application-id': appId,
    'x-airtable-inter-service-client': 'webClient',
    'x-time-zone': 'America/Chicago',
    'x-user-locale': 'en',
    'accept': 'application/json'
  };

  const renderClause = (c) => {
    if (!c || typeof c !== 'object') return '';
    if (Array.isArray(c.filterSet)) {
      const conj = (c.conjunction || 'and').toUpperCase();
      return '(' + c.filterSet.map(renderClause).join(` ${conj} `) + ')';
    }
    const col = c.columnId || c.fieldId || '?';
    const op = c.operator || '=';
    const val = c.value;
    if (val == null) return `\`${col}\` ${op}`;
    if (Array.isArray(val)) {
      return `\`${col}\` ${op} [${val.map(v => JSON.stringify(v)).join(', ')}]`;
    }
    return `\`${col}\` ${op} ${JSON.stringify(val)}`;
  };

  const renderTopLevel = (f) => {
    if (!f || !Array.isArray(f.filterSet)) return null;
    const conj = (f.conjunction || 'and').toUpperCase();
    return f.filterSet.map(renderClause).join(` ${conj} `);
  };

  const out = {};
  await Promise.all(targets.map(async (t) => {
    try {
      const url = `https://airtable.com/v0.3/view/${t.viewId}/readData?stringifiedObjectParams=%7B%7D&requestId=reqVF_${t.viewId}&secretSocketId=${secretSocketId}`;
      const r = await fetch(url, { credentials: 'include', headers });
      if (!r.ok) {
        out[t.viewId] = { tableId: t.tableId, name: t.name || null, error: `HTTP ${r.status}` };
        return;
      }
      const d = await r.json();
      const data = d.data || d;
      const filterRaw = data.filters || null;
      out[t.viewId] = {
        tableId: t.tableId,
        name: t.name || data.name || null,
        filterRaw,
        filterRendered: filterRaw ? renderTopLevel(filterRaw) : null,
      };
    } catch (e) {
      out[t.viewId] = { tableId: t.tableId, name: t.name || null, error: e.message };
    }
  }));
  return out;
}

return fetchViewFilters();
