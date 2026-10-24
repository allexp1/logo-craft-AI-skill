#!/usr/bin/env node
'use strict';

// Installs the logo-craft skill into a Claude skills directory. Copies files
// and nothing else: it does not run the skill, and it touches nothing outside
// the destination and ~/.claude/skill-backups.

const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');

const SKILL = 'logo-craft';
const PARTS = ['SKILL.md', 'references', 'scripts', 'assets', '.living'];

const argv = process.argv.slice(2);
const has = (f) => argv.includes(f);
const dryRun = has('--dry-run') || has('-n');

if (has('--help') || has('-h')) {
  console.log(`
  ${SKILL} — installer

  Usage
    npx ${SKILL} [options]

  Options
        --project   Install to ./.claude/skills/${SKILL} (this project only)
        --dest DIR  Install to DIR instead
    -n, --dry-run   Show what would be written, change nothing
    -h, --help      This

  By default the skill goes to ~/.claude/skills/${SKILL}. An existing install
  is moved to ~/.claude/skill-backups/ first — never overwritten, and never
  left inside skills/, where a backup would register as a second skill.

  The skill's Python scripts need python3 (3.9+) and, for rendering, either
  rsvg-convert (brew install librsvg) or ImageMagick. Python packages are
  installed on first use into ~/.cache/logo-craft/venv, never system-wide.
`);
  process.exit(0);
}

const src = path.resolve(__dirname, '..', SKILL);
const destFlag = argv.indexOf('--dest');
let dest;
if (destFlag !== -1 && argv[destFlag + 1]) {
  dest = path.resolve(argv[destFlag + 1]);
} else if (has('--project')) {
  dest = path.join(process.cwd(), '.claude', 'skills', SKILL);
} else {
  dest = path.join(os.homedir(), '.claude', 'skills', SKILL);
}
const backupRoot = path.join(os.homedir(), '.claude', 'skill-backups');

const say = (s) => console.log(s);
const tick = (s) => say(`  ✓ ${s}`);

// The last_updated date of a KNOWLEDGE.md, or '' when there is none.
const knowledgeDate = (file) => {
  if (!fs.existsSync(file)) return '';
  const m = fs.readFileSync(file, 'utf8').match(/^last_updated:\s*(\S+)/m);
  return m ? m[1] : '';
};

// Skip Python caches and OS junk when copying.
const filter = (p) => {
  const base = path.basename(p);
  return base !== '__pycache__' && base !== '.DS_Store' && !base.endsWith('.pyc');
};

say(`\n  ${SKILL} v${require('../package.json').version}`);
say(`  from ${src}`);
say(`  to   ${dest}${dryRun ? '   (dry run)' : ''}\n`);

// Refuse to run from a tree that is missing its own content, which would
// otherwise install a hollow skill over a working one.
const missing = PARTS.filter((p) => !fs.existsSync(path.join(src, p)));
if (missing.length) {
  console.error(`  Cannot install: this package is missing ${missing.join(', ')}.`);
  console.error(`  Nothing was changed.\n`);
  process.exit(1);
}

// Back up any existing install. Backups go OUTSIDE skills/ deliberately:
// anything with a SKILL.md under skills/ is discovered as a skill, so a
// backup left in place would show up as a duplicate.
let backup = '';
if (fs.existsSync(dest)) {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`
    + `-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  backup = path.join(backupRoot, `${SKILL}-${stamp}`);
  if (dryRun) {
    tick(`would back up existing install to ${backup}`);
  } else {
    fs.mkdirSync(backupRoot, { recursive: true });
    fs.renameSync(dest, backup);
    tick(`backed up existing install to ${backup}`);
  }
}

if (!dryRun) fs.mkdirSync(dest, { recursive: true });

for (const part of PARTS) {
  const from = path.join(src, part);
  const to = path.join(dest, part);
  if (dryRun) {
    const stat = fs.statSync(from);
    const n = stat.isDirectory() ? fs.readdirSync(from).filter(filter).length : 1;
    tick(`would copy ${part}${stat.isDirectory() ? ` (${n} entries)` : ''}`);
    continue;
  }
  fs.cpSync(from, to, { recursive: true, filter });
  tick(`copied ${part}`);
}

// A refresh may have updated the installed knowledge after this package was
// built. Never overwrite newer knowledge with older.
if (!dryRun && backup) {
  const oldKnowledge = path.join(backup, '.living', 'KNOWLEDGE.md');
  const newKnowledge = path.join(dest, '.living', 'KNOWLEDGE.md');
  const oldDate = knowledgeDate(oldKnowledge);
  const newDate = knowledgeDate(newKnowledge);
  if (oldDate && oldDate > newDate) {
    fs.copyFileSync(oldKnowledge, newKnowledge);
    const oldLog = path.join(backup, '.living', 'CHANGELOG.md');
    if (fs.existsSync(oldLog)) {
      fs.copyFileSync(oldLog, path.join(dest, '.living', 'CHANGELOG.md'));
    }
    tick(`kept the installed knowledge (${oldDate}); it is newer than this package's (${newDate || 'none'})`);
  }
}

// Re-baseline the living sidecar's integrity hash against the SKILL.md just
// written, so it does not immediately report a mismatch it caused itself.
const hashFile = path.join(dest, '.living', 'ORIGINAL.sha256');
if (!dryRun && fs.existsSync(path.join(dest, '.living'))) {
  const sum = crypto.createHash('sha256')
    .update(fs.readFileSync(path.join(dest, 'SKILL.md')))
    .digest('hex');
  fs.writeFileSync(hashFile, sum + '\n');
  tick('re-baselined the .living integrity hash');
}

say(dryRun ? `
  Dry run. Nothing was written.
` : `
  Done. Use it in Claude Code with:

    /logo-craft <what you want: a logo for this project, an app icon, a wordmark...>

  or just ask for a logo, icon, wordmark or brand identity while working in
  a project. If the skill does not show up, restart Claude Code.
`);
