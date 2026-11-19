// Airtable Automations Bulk Fetch
// Substitute APP_ID and SECRET_SOCKET_ID before running via evaluate_script.
// Returns a JSON array of automation objects with trigger and action details.
//
// Captures:
//   - Workflow id, name, description, deploymentStatus, URL
//   - Trigger type + inputs (tableId, viewId, fieldId, cron type)
//   - Trigger conditions:
//       * watchFields  — for "record updated" triggers (wttRECORDUPDATED0)
//       * filtersObj   — for "matches conditions" triggers (wttRECORDMATCHES0)
//   - Each action's type, target table, fields written (resolved from the
//     properties tree, not from positional indices), email recipient/subject,
//     script length, view ID, and filterByFormula.

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

  // Airtable's expression trees use a `properties` ARRAY of
  // { key: {value: 'fldXXX'}, value: <expr> } entries — NOT a plain object.
  // Calling Object.keys() on it returns positional indices ("0","1","2"),
  // which silently looks like field IDs but is wrong. Walk the array instead.
  const extractFieldIdsFromProperties = (propertiesArr) => {
    if (!Array.isArray(propertiesArr)) return [];
    return propertiesArr
      .map(p => p?.key?.value)
      .filter(v => typeof v === 'string' && v.startsWith('fld'));
  };

  // Walks a filtersObj tree and collects every literal field ID referenced
  // anywhere in the operand chain. Used so the parser can resolve those IDs
  // to field names without re-walking the tree.
  const extractFilterFieldIds = (node) => {
    if (!node || typeof node !== 'object') return [];
    const out = [];
    const props = node.properties || [];
    if (Array.isArray(props)) {
      for (const p of props) {
        if (p?.key?.value === 'operands' && p?.value?.elements) {
          for (const el of p.value.elements) {
            if (el?.type === 'literal' && typeof el.value === 'string' && el.value.startsWith('fld')) {
              out.push(el.value);
            } else if (el?.type === 'object') {
              out.push(...extractFilterFieldIds(el));
            }
          }
        }
      }
    }
    return out;
  };

  // Step 1: Get the full workflow list
  const listRes = await fetch(
    `https://airtable.com/v0.3/application/${appId}/listWorkflows?stringifiedObjectParams=%7B%7D&requestId=reqAuditList&secretSocketId=${secretSocketId}`,
    { credentials: 'include', headers }
  );
  const listData = await listRes.json();
  const workflows = (listData.data || listData).workflows || [];

  // Step 2: Fetch full details for each workflow in parallel
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

      // Common shortcut fields (some are null depending on trigger type)
      const trigInputs = trigger.inputExpressions || {};
      const tableId = trigInputs.tableId?.value || null;
      const fieldId = trigInputs.fieldId?.value || null;
      const viewId = trigInputs.viewId?.value || null;
      const cronType = trigInputs.type?.value || null;

      // Trigger condition specifics — these are what makes "any-update" vs
      // "specific-field-update" vs "filter-formula" distinguishable. Without
      // capturing these, the audit can't tell why a trigger fires.
      const watchFields = (trigInputs.watchFields?.elements || [])
        .map(e => e?.value)
        .filter(Boolean);
      const filtersObj = trigInputs.filtersObj || null;
      const filterFieldIds = filtersObj ? extractFilterFieldIds(filtersObj) : [];

      const actions = Object.values(actionsById).map(a => {
        const inp = a.inputExpressions || {};
        const fieldsWritten = extractFieldIdsFromProperties(inp.fields?.properties);
        return {
          actionType: a.workflowActionTypeId || '?',
          tableId: inp.tableId?.value || null,
          fieldsWritten,
          toVal: JSON.stringify(inp.to || inp.toEmailAddresses || '').slice(0, 300),
          subjectVal: JSON.stringify(inp.subject || '').slice(0, 300),
          scriptLen: (inp.code?.value || '').length,
          viewId: inp.viewId?.value || null,
          filterFormula: inp.filterByFormula?.value || ''
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
        triggerConditions: {
          watchFields,
          filterFieldIds,
          filtersObj
        },
        actions
      };
    } catch (e) {
      return { id: wf.id, name: wf.name, error: e.message };
    }
  }));

  return details;
}

return fetchAutomations();
