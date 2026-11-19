"""Build private ChatGPT updates from checked-out canonical GitHub files."""
from pathlib import Path
import argparse,hashlib,json,posixpath,re,shutil,subprocess,zipfile
import yaml
parser=argparse.ArgumentParser();parser.add_argument('--repositories',required=True);parser.add_argument('--state',required=True);parser.add_argument('--out',required=True);parser.add_argument('--remove-duplicate-entry-points',action='store_true',help='Use only after the exact cleanup has been approved.');args=parser.parse_args()
R=Path(args.repositories);B=Path(args.state);O=Path(args.out);O.mkdir(parents=True,exist_ok=True)
M=json.loads((R/'Skills/maintenance/chatgpt-source-map.json').read_text());mapping=M['entries'];live={x['name']:x for x in json.loads((B/'live-plugins.json').read_text())}
layouts=[{'repo':p.name,'name':x['name'],'root':x['root']} for p in R.iterdir() if (p/'release-registry.json').exists() for x in json.loads((p/'release-registry.json').read_text())['packages']]
collection=R/'Skills/distribution/rachael-github-skills'
heads={p.name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip() for p in R.iterdir() if (p/'.git').exists()}
plan=[];provenance=[]
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def source_info(row):
 repo=row['repository'].split('/')[-1];file=R/repo/row['source_path'];header=yaml.safe_load(file.read_text().split('---',2)[1]);actual=str(header.get('version') or (header.get('metadata') or {}).get('version'))
 assert actual==row['version'],f'Stale source version: {row["repository"]}/{row["source_path"]}: {actual} != {row["version"]}'
 return {'repository':row['repository'],'path':row['source_path'],'version':row['version'],'commit':heads[repo],'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}

for layout in layouts:
 name=layout['name'];repo=layout['repo'];src=R/repo/layout['root'];dest=O/name
 if dest.exists():shutil.rmtree(dest)
 dest.mkdir();record=live[name];rows=[x for x in mapping if x['package']==name]
 # Retain the current package's exact supported file layout; refresh files from GitHub.
 for item in record['files']:
  path=item['path']
  if path.endswith('/INSTRUCTIONS-BEFORE-PLAIN-ENGLISH.md'):continue
  a=src/path
  if a.is_file():copy(a,dest/path)
 for row in rows:
  a=R/repo/row['source_path'];b=dest/row['export_path'];copy(a,b)
  for file in ['README.md','TECHNICAL-GUIDE.md']:
   if a.with_name(file).exists():copy(a.with_name(file),b.with_name(file))
 # The missing logger is a checked generated copy of the canonical execute helper.
 if name=='client-docs':copy(R/'Skills/execute/scripts/log_event.py',dest/'skills/execute/scripts/log_event.py')
 for path in ['plugin.json','.codex-plugin/plugin.json']:
  assert (src/path).exists();copy(src/path,dest/path)
 version=json.loads((dest/'plugin.json').read_text())['version']
 # Package-relative references to repository-only documentation become pinned source links.
 for f in dest.rglob('*.md'):
  text=f.read_text()
  def link(match):
   target=match[1]
   if target.startswith(('#','http:','https:','mailto:','plugin:','app:','/')):return match[0]
   path,sep,anchor=target.partition('#');resolved=posixpath.normpath(posixpath.join(str(f.relative_to(dest).parent),path))
   if (dest/resolved).exists():return match[0]
   source=(src/resolved).resolve()
   if source.is_file() and source.is_relative_to(R/repo):return ']('+f'https://github.com/RachaelQuisel/{repo}/blob/{heads[repo]}/{source.relative_to(R/repo)}'+(sep+anchor if sep else '')+')'
   return match[0]
  f.write_text(re.sub(r'\]\(([^\s)]+)\)',link,text))
 save(dest/'SOURCE-OF-TRUTH.json',{'repository':'RachaelQuisel/'+repo,'packageRoot':layout['root'],'version':version,'commit':heads[repo],'skills':[{**source_info(x),'exportPath':x['export_path']} for x in rows]})
 provenance.append({'name':name,'version':version,'repository':'RachaelQuisel/'+repo,'root':layout['root'],'commit':heads[repo]})

name='rachael-github-skills';dest=O/name
if dest.exists():shutil.rmtree(dest)
dest.mkdir();record=live[name]
for folder in ['catalog','scripts']:
 if (collection/folder).exists():shutil.copytree(collection/folder,dest/folder)
for file in ['README.md','LICENSE']:
 if (collection/file).exists():copy(collection/file,dest/file)
records=[]
for row in [x for x in mapping if x['package']==name]:
 repo=row['repository'].split('/')[-1];canonical=R/repo/row['source_path'];imported={}
 info=source_info(row);data={**imported,'name':row['skill'],'source_repository':row['repository'],'source_path':row['source_path'],'source_commit':heads[repo],'source_url':f'https://github.com/{row["repository"]}/blob/{heads[repo]}/{row["source_path"]}','version':row['version'],'canonical_sha256':info['sha256'],'available_in_plugin':row['available_in_plugin']}
 header=yaml.safe_load(canonical.read_text().split('---',2)[1]);data['original_name']=header.get('name',row['skill']);data['description']=header.get('description','')
 records.append(data)
 if not row['export'] and args.remove_duplicate_entry_points:
  guide=dest/'skills'/row['skill']/'README.md';guide.parent.mkdir(parents=True,exist_ok=True)
  guide.write_text('# '+row['skill'].replace('-', ' ').title()+'\n\nUse this skill in the existing `'+row['available_in_plugin']+'` plugin. Its working instructions come from the [canonical source]('+data['source_url']+').\n')
  continue
 target=dest/'skills'/row['skill'];target.mkdir(parents=True)
 # Resource paths stay relative to the canonical folder. Removed source files are omitted.
 for file in row.get('resource_files',[]):
  source=R/repo/file['source_path']
  assert source.is_file(),source
  copy(source,target/file['export_path'])
 text=canonical.read_text();parts=text.split('---',2);h=yaml.safe_load(parts[1]);h['name']=row['skill'];text='---\n'+yaml.safe_dump(h,sort_keys=False,allow_unicode=True).rstrip()+'\n---'+parts[2]
 (target/'SKILL.md').write_text(text)
 for file in ['README.md','TECHNICAL-GUIDE.md']:
  if canonical.with_name(file).exists():copy(canonical.with_name(file),target/file)
 save(target/'IMPORT-SOURCE.json',data)
save(dest/'catalog/skills.json',records)
(dest/'catalog/skills.md').write_text('# Skills and their current sources\n\n'+''.join(f'- **{x["name"]}**: {x["description"]} Available in `{x["available_in_plugin"]}`. [Canonical source]({x["source_url"]})\n' for x in records))
copy(R/'Skills/distribution/rachael-github-skills/plugin.json',dest/'plugin.json');copy(R/'Skills/distribution/rachael-github-skills/codex-plugin.json',dest/'.codex-plugin/plugin.json')
export_count=sum(1 for x in mapping if x['package']==name and (x['export'] or not args.remove_duplicate_entry_points))
(dest/'README.md').write_text(f'# Rachael’s GitHub skills\n\nThis private collection contains {export_count} generated skill entries built from canonical GitHub sources. Shared copies use the same instructions and versions as the existing specialist plugins. The source catalog records their current location and version.\n\nUse the GitHub skill library to find the right workflow. Each skill includes a plain-English guide and its working instructions. Required account connections and local tools depend on the chosen workflow.\n\nRelease changes through the private Skills repository and update existing ChatGPT, Claude, and catalog records together.\n')
save(dest/'SOURCE-OF-TRUTH.json',{'repository':'RachaelQuisel/Skills','path':'maintenance/chatgpt-source-map.json','commit':heads['Skills'],'collectionVersion':M['collectionVersion'],'exportedSkills':export_count,'sharedSkillsRoutedToExistingPlugins':48,'duplicateEntryPointRemoval':args.remove_duplicate_entry_points})
provenance.append({'name':name,'version':M['collectionVersion'],'repository':'RachaelQuisel/Skills','root':'distribution/rachael-github-skills','commit':heads['Skills']})

for p in provenance:
 name=p['name'];dest=O/name;record=live[name];files={str(f.relative_to(dest)) for f in dest.rglob('*') if f.is_file()}
 # Keep all support files. Remove only our temporary backups and duplicate discovery entry points.
 retired={x['export_path'] for x in mapping if x['package']==name and not x.get('export',True)}
 deletes=[f['path'] for f in record['files'] if f['path'] not in files and (f['path'].endswith('INSTRUCTIONS-BEFORE-PLAIN-ENGLISH.md') or f['path'] in retired)] if args.remove_duplicate_entry_points else []
 archive=O/(name+'.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for file in sorted(files):z.write(dest/file,name+'/'+file)
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 plan.append({**p,'plugin_id':record['plugin']['plugin_id'],'expected_release_id':record['plugin']['current_release_id'],'archive':str(archive),'delete_paths':deletes,'file_count':len(files),'instruction_count':sum(f.endswith('/SKILL.md') for f in files)})
save(O/'plan.json',plan);save(O/'provenance.json',provenance)
print(json.dumps({'packages':len(plan),'instructions':sum(p['instruction_count'] for p in plan),'deletedPaths':sum(len(p['delete_paths']) for p in plan),'versions':{p['name']:p['version'] for p in plan}},indent=2))
