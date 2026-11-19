// Airtable Automations Bulk Fetch
// Substitute APP_ID and SECRET_SOCKET_ID before running via evaluate_script.
// Returns a JSON array of automation objects with trigger and action details.
//
// Captures (per automation):
//   - Workflow id, name, description, deploymentStatus, URL
//   - Trigger type + inputs (tableId, viewId, fieldId, cron type)
//   - Trigger conditions:
//       * watchFields  — for "record updated" triggers (wttRECORDUPDATED0)
//       * filtersObj   — for "matches conditions" triggers (wttRECORDMATCHES0)
//   - Each action's type, target table, fields written (resolved from the
//     properties tree, not from positional indices), email recipient/subject
//     (decoded from Airtable's expression-tree AST into plain strings),
//     script length, view ID, and filterByFormula.
//
// Why we decode toVal/subjectVal at fetch time: Airtable stores email
// destinations and subjects as nested expression trees ("template" / "array" /
// "objectPropertyLookup" / "functionCall"). Returning the raw JSON to the
// parser meant the audit doc showed unreadable JSON for every dynamic email.
// Decoding here keeps the parser simple and the audit immediately readable.
// Field IDs inside template paths (e.g. cellValuesByFieldId, fldXXX) survive
// as-is so the parser can substitute names from the field map.

async function fetchAutomations() {
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

  // ── Expression-tree decoder ────────────────────────────────────────────────
  // Walks Airtable's internal AST for templates and returns a readable string.
  // Field IDs and select-option IDs are preserved with simple wrappers so the
  // Python parser can substitute names.
  const renderNode = (node) => {
    if (node == null) return '';
    if (typeof node === 'string') return node;
    if (typeof node !== 'object') return String(node);
    const t = node.type;
    if (t === 'literal') return node.value == null ? '' : String(node.value);
    if (t === 'template') return (node.elements || []).map(renderNode).join('');
    if (t === 'array') {
      return (node.elements || []).map(renderNode).filter(s => s).join(', ');
    }
    if (t === 'objectPropertyLookup') {
      const path = node.path ? renderNode(node.path) : '';
      // Common patterns:
      //   "cellValuesByFieldId.fldXXX" → preserve fldXXX for parser substitution
      //   "fields.fldXXX"              → same
      //   "value"                      → generic property accessor on a record
      const m = path.match(/(?:cellValuesByFieldId|fields)\.(fld[A-Za-z0-9]+)/);
      if (m) return `{field:${m[1]}}`;
      // Some paths are richer like "fields.fldXXX.name" — keep the field ref
      const m2 = path.match(/(fld[A-Za-z0-9]+)/);
      if (m2) return `{field:${m2[1]}}`;
      if (path === 'value' || path === 'name') return '(dynamic value)';
      return path ? `{${path}}` : '(dynamic value)';
    }
    if (t === 'functionCall') {
      const fn = (node.function && node.function.id) || 'fn';
      const params = node.parameters || [];
      // Common functions used in templates:
      if (fn === 'map' && params.length >= 2) return renderNode(params[1]);
      if (fn === 'concat') return params.map(renderNode).join('');
      if (fn === 'if' && params.length >= 2) return renderNode(params[1]);
      // Generic fall-back so unfamiliar calls don't render as empty
      return `{${fn}(${params.map(renderNode).join(', ')})}`;
    }
    if (t === 'nodeIdentifier') {
      // References another action's output. Best effort: indicate dynamic.
      return '';
    }
    if (t === 'object') return '{expr}';
    return '';
  };
  const decode = (node) => {
    if (!node) return '';
    return renderNode(node).replace(/\s+/g, ' ').trim();
  };

  // ── Script input-variable decoder ───────────────────────────────────────────
  // "Run a script" actions (watCUSTOMSCRIPT00) configure input variables via
  // inputExpressions.inputObj, an `object` whose `properties` array maps a
  // variable name to a source expression — e.g. recordId ← the trigger record's
  // `id`, or a value pulled from a preceding "Find records" action. Capturing
  // this is what lets the audit explain *what data a script operates on* without
  // reading the code line by line. Field IDs in a path survive as {field:fldXXX}
  // and upstream action references as {node:wacXXX} so the parser can resolve
  // both to readable names.
  const decodeScriptInputs = (inputObj) => {
    if (!inputObj || !Array.isArray(inputObj.properties)) return [];
    const refOf = (v) => {
      if (v == null || typeof v !== 'object') return decode(v);
      if (v.type === 'literal') return v.value == null ? '' : String(v.value);
      if (v.type === 'objectPropertyLookup') {
        const obj = v.object || {};
        const path = ((v.path && v.path.elements) || [])
          .map(e => e && e.value).filter(x => x != null);
        const fld = path.find(p => typeof p === 'string' && p.startsWith('fld'));
        let src;
        if (obj.type === 'nodeIdentifier') {
          src = obj.nodeType === 'trigger' ? 'trigger record' : `{node:${obj.nodeId}}`;
        } else {
          src = 'record';
        }
        if (fld) return `${src} → {field:${fld}}`;
        return path.length ? `${src} → ${path.join('.')}` : src;
      }
      return decode(v);
    };
    return inputObj.properties.map(p => ({
      name: (p.key && p.key.value) || '?',
      ref: refOf(p.value),
    }));
  };

  // ── Field-ID collectors ─────────────────────────────────────────────────────
  // Airtable's expression trees use a `properties` ARRAY of
  // { key: {value: 'fldXXX'}, value: <expr> } entries — NOT a plain object.
  // Object.keys() returns positional indices ("0","1","2"), which silently
  // looks like field IDs but is wrong. Walk the array.
  const extractFieldIdsFromProperties = (propertiesArr) => {
    if (!Array.isArray(propertiesArr)) return [];
    return propertiesArr
      .map(p => p && p.key && p.key.value)
      .filter(v => typeof v === 'string' && v.startsWith('fld'));
  };

  // Walks a filtersObj tree and collects every literal field ID referenced
  // anywhere. The parser uses this to resolve names without re-walking.
  const extractFilterFieldIds = (node) => {
    if (!node || typeof node !== 'object') return [];
    const out = [];
    const props = node.properties || [];
    if (Array.isArray(props)) {
      for (const p of props) {
        if (p && p.key && p.key.value === 'operands' && p.value && p.value.elements) {
          for (const el of p.value.elements) {
            if (el && el.type === 'literal' && typeof el.value === 'string' && el.value.startsWith('fld')) {
              out.push(el.value);
            } else if (el && el.type === 'object') {
              out.push(...extractFilterFieldIds(el));
            }
          }
        }
      }
    }
    return out;
  };

  // ── Step 1: Workflow list ──────────────────────────────────────────────────
  const listRes = await fetch(
    `https://airtable.com/v0.3/application/${appId}/listWorkflows?stringifiedObjectParams=%7B%7D&requestId=reqAuditList&secretSocketId=${secretSocketId}`,
    { credentials: 'include', headers }
  );
  const listData = await listRes.json();
  const workflows = (listData.data || listData).workflows || [];

  // ── Step 2: Per-workflow detail ────────────────────────────────────────────
  const details = await Promise.all(workflows.map(async (wf) => {
    try {
      const res = await fetch(
        `https://airtable.com/v0.3/workflow/${wf.id}/read?stringifiedObjectParams=%7B%7D&requestId=req${wf.id}&secretSocketId=${secretSocketId}`,
        { credentials: 'include', headers }
      );
      const d = await res.json();
      const w = (d.data || d).workflow || {};
      const trigger = w.trigger || {};
      const graph = w.graph || {};
      const actionsById = graph.actionsById || {};

      const trigInputs = trigger.inputExpressions || {};
      const tableId = trigInputs.tableId && trigInputs.tableId.value || null;
      const fieldId = trigInputs.fieldId && trigInputs.fieldId.value || null;
      const viewId = trigInputs.viewId && trigInputs.viewId.value || null;
      const cronType = trigInputs.type && trigInputs.type.value || null;
      // Form-submitted triggers (wttFORMSUBMITTED0) reference their form/page via
      // formId (a pagXXX id), not viewId. Capture it so the parser can resolve the
      // form's human name from a form map.
      const formId = trigInputs.formId && trigInputs.formId.value || null;

      const watchFields = ((trigInputs.watchFields && trigInputs.watchFields.elements) || [])
        .map(e => e && e.value)
        .filter(Boolean);
      const filtersObj = trigInputs.filtersObj || null;
      const filterFieldIds = filtersObj ? extractFilterFieldIds(filtersObj) : [];

      // Workflow nodes come in two flavors:
      //   - Actions:   have workflowActionTypeId (watXXX) — send email, update record, etc.
      //   - Decisions: have workflowDecisionTypeId (wdtXXX) — fan-out loops, branch reducers, N-way conditionals
      // Both live in `actionsById`. Previously we treated decisions as "?" because we only
      // checked workflowActionTypeId; capture both kinds so the audit shows control flow.
      const actions = Object.entries(actionsById).map(([nodeId, a]) => {
        const inp = a.inputExpressions || {};
        const fieldsWritten = extractFieldIdsFromProperties(inp.fields && inp.fields.properties);

        // Discriminator: actions return their watXXX type; decisions return their wdtXXX type
        // so the parser can label them. Falling back to '?' would lose control flow.
        const actionType = a.workflowActionTypeId
          || a.workflowDecisionTypeId
          || '?';
        const nodeKind = a.workflowDecisionTypeId ? 'decision' : 'action';

        // Decision-specific shape: extract the "what does this orchestrate" detail so the
        // audit can say "iterate over records from <source action>" rather than just "Fan-out".
        let loopOver = null;
        if (a.workflowDecisionTypeId === 'wdtFANOUT00000000' && inp.fanOutArray) {
          const lookup = inp.fanOutArray;
          if (lookup && lookup.type === 'objectPropertyLookup' && lookup.object && lookup.object.nodeId) {
            loopOver = lookup.object.nodeId; // an action ID — parser can resolve to its label
          }
        }
        let branchCount = null;
        if (a.workflowDecisionTypeId === 'wdtNWAY0000000000' && inp.groups && Array.isArray(inp.groups.elements)) {
          branchCount = inp.groups.elements.length;
        }

        // Script body lives at inputExpressions.script.value (a `literal`). Older
        // code read inp.code, which doesn't exist on current bases — that bug
        // silently reported every script as 0 chars. Keep `code` as a fallback in
        // case an older base still uses it.
        const scriptCode = (inp.script && inp.script.value)
          || (inp.code && inp.code.value)
          || '';

        return {
          id: nodeId,
          actionType,
          nodeKind,
          tableId: inp.tableId && inp.tableId.value || null,
          fieldsWritten,
          toVal: decode(inp.to || inp.toEmailAddresses),
          subjectVal: decode(inp.subject),
          script: scriptCode,
          scriptLen: scriptCode.length,
          scriptInputs: decodeScriptInputs(inp.inputObj),
          viewId: inp.viewId && inp.viewId.value || null,
          filterFormula: (inp.filterByFormula && inp.filterByFormula.value) || '',
          loopOver,
          branchCount,
        };
      });

      return {
        id: wf.id,
        name: wf.name,
        url: `https://airtable.com/${appId}/${wf.id}`,
        enabled: wf.deploymentStatus === 'deployed',
        deploymentStatus: wf.deploymentStatus,
        description: wf.description || null,
        triggerTypeId: trigger.workflowTriggerTypeId,
        trigInputs: { tableId, fieldId, viewId, cronType },
        triggerConditions: { watchFields, filterFieldIds, filtersObj },
        actions
      };
    } catch (e) {
      return { id: wf.id, name: wf.name, error: e.message };
    }
  }));

  return details;
}

return fetchAutomations();
