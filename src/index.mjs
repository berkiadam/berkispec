#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { spawn, spawnSync } from "node:child_process";
import { stdin as input, stdout as output } from "node:process";
import { fileURLToPath } from "node:url";

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(toolDir, "..");
const workDir = process.cwd();
const specsDir = path.join(workDir, "specs");
const stateDir = path.join(workDir, ".berkispec");
const historyDir = path.join(stateDir, "history");
const projectPromptsDir = path.join(stateDir, "prompts");
const configPath = path.join(stateDir, "config.json");
const projectDescPath = path.join(stateDir, "project-desc.md");
const latestPromptPath = path.join(stateDir, "latest-prompt.md");
const completerState = { mode: "none" };

const phases = [
  { id: "init", label: "init", promptName: "00-init.md" },
  { id: "project", label: "project", promptName: "01-project.md" },
  { id: "spec", label: "spec", promptName: "01-write-spec.md" },
  { id: "plan", label: "plan", promptName: "02-write-plan.md" },
  { id: "tasks", label: "tasks", promptName: "03-write-tasks.md" },
  { id: "implement", label: "implement", promptName: "04-implement-tasks.md" },
  { id: "validate", label: "validate", promptName: "05-validate-cycle.md" }
];

const interactiveOptions = [...phases, { id: "exit", label: "exit" }];
const supportedProjectLanguages = ["HU", "EN"];
const defaultProjectLanguage = "EN";
const toolPromptsDir = path.join(rootDir, "prompts");
const promptFileNames = [...new Set([...phases.map((phase) => phase.promptName), "01-modify-spec.md"])];

const defaultProjectDesc = `# Project Description

## Summary

## Reference Files
`;

function ask(rl, question) {
  return new Promise((resolve) => {
    rl.question(question, resolve);
  });
}

function ensureStateDir() {
  fs.mkdirSync(stateDir, { recursive: true });
  fs.mkdirSync(historyDir, { recursive: true });
}

function readConfig() {
  if (!fs.existsSync(configPath)) {
    return {};
  }

  const content = fs.readFileSync(configPath, "utf8").trim();

  if (content.length === 0) {
    return {};
  }

  try {
    return JSON.parse(content);
  } catch (error) {
    throw new Error(`Invalid berkispec config: ${relativeToWorkDir(configPath)}`);
  }
}

function getCodexConfig() {
  const config = readConfig();
  const codexConfig = config.codex ?? {};

  return {
    enabled: codexConfig.enabled ?? true,
    command: codexConfig.command ?? "codex",
    mode: codexConfig.mode ?? "exec",
    sandbox: codexConfig.sandbox ?? "workspace-write",
    approval: codexConfig.approval ?? "never"
  };
}

function writeConfig(config) {
  ensureStateDir();
  fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, "utf8");
}

function getProjectLanguage() {
  const { projectLanguage } = readConfig();

  if (!projectLanguage) {
    return "";
  }

  if (!supportedProjectLanguages.includes(projectLanguage)) {
    throw new Error(`Unsupported project language in ${relativeToWorkDir(configPath)}: ${projectLanguage}`);
  }

  return projectLanguage;
}

function projectPromptReference(promptName) {
  return `.berkispec/prompts/${promptName}`;
}

function resolvePromptPath(language, promptName) {
  const projectPromptPath = path.join(projectPromptsDir, promptName);

  if (fs.existsSync(projectPromptPath) && fs.statSync(projectPromptPath).isFile()) {
    return projectPromptPath;
  }

  return path.join(toolPromptsDir, language, promptName);
}

function readPromptTemplate(language, promptName) {
  const promptPath = resolvePromptPath(language, promptName);

  if (!fs.existsSync(promptPath) || !fs.statSync(promptPath).isFile()) {
    throw new Error(`Missing prompt template: ${path.relative(workDir, promptPath)}`);
  }

  return fs.readFileSync(promptPath, "utf8").trim();
}

function ensurePromptSource(language) {
  const sourceDir = path.join(toolPromptsDir, language);

  if (!fs.existsSync(sourceDir) || !fs.statSync(sourceDir).isDirectory()) {
    throw new Error(`Missing prompt source directory: ${path.relative(workDir, sourceDir)}`);
  }

  for (const fileName of promptFileNames) {
    const sourcePath = path.join(sourceDir, fileName);

    if (!fs.existsSync(sourcePath) || !fs.statSync(sourcePath).isFile()) {
      throw new Error(`Missing prompt source file: ${path.relative(workDir, sourcePath)}`);
    }
  }
}

function copyProjectPrompts(language) {
  ensurePromptSource(language);
  fs.mkdirSync(projectPromptsDir, { recursive: true });

  let copied = 0;

  for (const fileName of promptFileNames) {
    const sourcePath = path.join(toolPromptsDir, language, fileName);
    const targetPath = path.join(projectPromptsDir, fileName);

    if (fs.existsSync(targetPath)) {
      continue;
    }

    fs.copyFileSync(sourcePath, targetPath);
    copied += 1;
  }

  return copied;
}

function ensureInitialized() {
  const projectLanguage = getProjectLanguage();

  if (!projectLanguage) {
    throw new Error("Validation error: run `berkispec init` and select the project language first.");
  }

  copyProjectPrompts(projectLanguage);
  return projectLanguage;
}

function ensureProjectDescTemplate() {
  ensureStateDir();

  if (!fs.existsSync(projectDescPath)) {
    fs.writeFileSync(projectDescPath, defaultProjectDesc, "utf8");
  }
}

function writePrompt(prompt) {
  ensureStateDir();
  fs.writeFileSync(latestPromptPath, `${prompt}\n`, "utf8");
}

function printPrompt(prompt) {
  writePrompt(prompt);
  output.write("\n--- Codex prompt ---\n\n");
  output.write(`${prompt}\n`);
  output.write("--- End prompt ---\n\n");
  output.write(`Prompt file: ${path.relative(workDir, latestPromptPath)}\n`);
}

function runCodex(prompt, { command, mode = "exec", cwd = workDir, sandbox = "workspace-write", approval = "never" } = {}) {
  writePrompt(prompt);

  return new Promise((resolve, reject) => {
    const args = ["--cd", cwd, mode];

    if (mode === "exec") {
      args.unshift("--ask-for-approval", approval);
      args.unshift("--sandbox", sandbox);
      args.push("--skip-git-repo-check");
    }

    args.push(prompt);

    const child = spawn(command, args, {
      cwd,
      stdio: ["ignore", "pipe", "pipe"]
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      const text = chunk.toString();
      stdout += text;
      output.write(text);
    });

    child.stderr.on("data", (chunk) => {
      const text = chunk.toString();
      stderr += text;
      output.write(text);
    });

    child.on("error", (error) => {
      reject(error);
    });

    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Codex CLI failed with exit code ${code}.`));
        return;
      }

      resolve({ code, stdout, stderr });
    });
  });
}

function readProjectDesc() {
  if (!fs.existsSync(projectDescPath)) {
    return { summary: "", files: [] };
  }

  const content = fs.readFileSync(projectDescPath, "utf8");
  const match = content.match(/## Summary\s*([\s\S]*?)\n## Reference Files\s*([\s\S]*)$/);

  if (!match) {
    return { summary: "", files: [] };
  }

  const summary = match[1].trim();
  const files = match[2]
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("- "))
    .map((line) => line.slice(2).trim());

  return { summary, files };
}

function writeProjectDesc({ summary, files }) {
  ensureStateDir();

  const normalizedFiles = [...new Set(files.map((file) => file.trim()).filter(Boolean))].sort();
  const content = [
    "# Project Description",
    "",
    "## Summary",
    "",
    summary.trim(),
    "",
    "## Reference Files",
    ...normalizedFiles.map((file) => `- ${file}`)
  ].join("\n");

  fs.writeFileSync(projectDescPath, `${content}\n`, "utf8");
}

function hasProjectContext() {
  if (!fs.existsSync(projectDescPath)) {
    return false;
  }

  const { summary, files } = readProjectDesc();
  return summary.length > 0 || files.length > 0;
}

function relativeToWorkDir(absolutePath) {
  return path.relative(workDir, absolutePath).replace(/\\/g, "/");
}

function ensureInsideWorkDir(targetPath) {
  const relative = path.relative(workDir, targetPath);
  return relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
}

function normalizeProjectPath(inputPath) {
  const resolved = path.resolve(workDir, inputPath);

  if (!ensureInsideWorkDir(resolved)) {
    throw new Error("Path must stay inside the current working directory.");
  }

  return resolved;
}

function listCycles() {
  if (!fs.existsSync(specsDir)) {
    return [];
  }

  return fs
    .readdirSync(specsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^cycle-\d+-/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
}

function nextCycleNumber() {
  const max = listCycles().reduce((currentMax, name) => {
    const match = name.match(/^cycle-(\d+)-/);
    return match ? Math.max(currentMax, Number(match[1])) : currentMax;
  }, 0);

  return String(max + 1).padStart(2, "0");
}

function slugify(value) {
  const normalized = value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return normalized || "new-cycle";
}

function projectFileCompleter(line) {
  const safeLine = line.trimStart();
  const hadLeadingDotSlash = safeLine.startsWith("./");
  const inputValue = safeLine === "" ? "." : safeLine;
  const parsed = inputValue.endsWith("/") ? { dir: inputValue, base: "" } : { dir: path.posix.dirname(inputValue), base: path.posix.basename(inputValue) };
  const dirPart = parsed.dir === "." ? "" : parsed.dir;
  const baseName = parsed.base;
  const targetDir = path.resolve(workDir, dirPart || ".");

  if (!ensureInsideWorkDir(targetDir) || !fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
    return [[], line];
  }

  const entries = fs
    .readdirSync(targetDir, { withFileTypes: true })
    .filter((entry) => entry.name.startsWith(baseName))
    .map((entry) => {
      const relativePrefix = dirPart ? `${dirPart}/` : "";
      const suffix = entry.isDirectory() ? "/" : "";
      const suggestion = `${relativePrefix}${entry.name}${suffix}`;
      return hadLeadingDotSlash && !suggestion.startsWith("./") ? `./${suggestion}` : suggestion;
    })
    .sort();

  return [entries, line];
}

function completer(line) {
  if (completerState.mode === "file") {
    return projectFileCompleter(line);
  }

  return [[], line];
}

async function askRequired(rl, label) {
  while (true) {
    const value = (await ask(rl, `${label}: `)).trim();

    if (value.length > 0) {
      return value;
    }

    output.write(`${label} is required.\n`);
  }
}

async function askMultiline(rl, label, { required = false } = {}) {
  output.write(`${label}:\n`);
  output.write("Type /done on its own line to finish.\n\n");

  const lines = [];

  while (true) {
    const line = await ask(rl, "> ");

    if (line.trim() === "/done") {
      break;
    }

    lines.push(line);
  }

  const value = lines.join("\n").trim();

  if (required && value.length === 0) {
    output.write(`${label} is required.\n\n`);
    return askMultiline(rl, label, { required });
  }

  return value;
}

async function choosePhase(rl) {
  output.write("Choose phase:\n");
  interactiveOptions.forEach((phase, index) => {
    output.write(`  ${index + 1}. ${phase.label}\n`);
  });

  while (true) {
    const value = (await ask(rl, "\nPhase: ")).trim().toLowerCase();
    const byNumber = interactiveOptions[Number(value) - 1];
    const byName = interactiveOptions.find((phase) => phase.id === value);
    const selected = byNumber ?? byName;

    if (selected) {
      return selected.id;
    }

    output.write(`Unknown phase: ${value}\n`);
  }
}

async function chooseCycle(rl) {
  const cycles = listCycles();

  if (cycles.length === 0) {
    throw new Error("No specs/cycle-* folders found in the current working directory.");
  }

  output.write("Choose cycle:\n");
  cycles.forEach((cycle, index) => {
    output.write(`  ${index + 1}. ${cycle}\n`);
  });

  while (true) {
    const value = (await ask(rl, "\nCycle: ")).trim();
    const byNumber = cycles[Number(value) - 1];
    const byName = cycles.find((cycle) => cycle === value);
    const selected = byNumber ?? byName;

    if (selected) {
      return selected;
    }

    output.write(`Unknown cycle: ${value}\n`);
  }
}

async function chooseProjectLanguage(rl) {
  output.write(`Project language (default: ${defaultProjectLanguage}):\n`);
  supportedProjectLanguages.forEach((language, index) => {
    output.write(`  ${index + 1}. ${language}\n`);
  });

  while (true) {
    const value = (await ask(rl, "\nLanguage: ")).trim().toUpperCase();

    if (value.length === 0) {
      return defaultProjectLanguage;
    }

    const byNumber = supportedProjectLanguages[Number(value) - 1];
    const selected = byNumber ?? supportedProjectLanguages.find((language) => language === value);

    if (selected) {
      return selected;
    }

    output.write(`Unknown language: ${value}\n`);
  }
}

async function chooseInitAction(rl) {
  output.write("Init action:\n");
  output.write("  1. Select project language\n");
  output.write("  2. finish\n");

  while (true) {
    const value = (await ask(rl, "\nAction: ")).trim().toLowerCase();
    const actions = {
      "1": "select-language",
      "2": "finish",
      "select project language": "select-language",
      "select language": "select-language",
      finish: "finish"
    };

    if (actions[value]) {
      return actions[value];
    }

    output.write(`Unknown action: ${value}\n`);
  }
}

function buildSpecPrompt({ name, goal, language }) {
  const number = nextCycleNumber();
  const cycle = `cycle-${number}-${slugify(name)}`;
  const specPath = `specs/${cycle}/spec.md`;
  const promptTemplate = readPromptTemplate(language, "01-write-spec.md");

  if (language === "EN") {
    return {
      cycle,
      targetPath: specPath,
      prompt: `${promptTemplate}

Project base description:
.berkispec/project-desc.md

Cycle name:
${name}

Goal:
${goal}

Expected new spec location:
${specPath}`
    };
  }

  return {
    cycle,
    targetPath: specPath,
    prompt: `${promptTemplate}

Projekt alapleírás:
.berkispec/project-desc.md

Ciklus neve:
${name}

Cél:
${goal}

A várható új spec helye:
${specPath}`
  };
}

function createSpecTarget({ targetPath }) {
  const absolutePath = path.join(workDir, targetPath);
  const targetDir = path.dirname(absolutePath);

  fs.mkdirSync(targetDir, { recursive: true });
  return { path: absolutePath };
}

function buildSpecModifyPrompt({ specPath, lastCodexResponse, userInput, language }) {
  const promptTemplate = readPromptTemplate(language, "01-modify-spec.md");

  if (language === "EN") {
    return `${promptTemplate}

Existing spec:
${specPath}

Previous Codex response / open questions:
${lastCodexResponse || "(No previous response captured.)"}

User clarification:
${userInput}

Update only the existing spec file in place.`;
  }

  return `${promptTemplate}

Meglévő spec:
${specPath}

Előző Codex válasz / nyitott kérdések:
${lastCodexResponse || "(Nincs eltárolt előző válasz.)"}

User pontosítás:
${userInput}

Kizárólag a meglévő spec fájlt módosítsd a helyén.`;
}

function parseSpecStatus(specContent) {
  const lines = specContent.split("\n").map((line) => line.trim());
  const statusLine = lines.find((line) => /^(Status|Állapot)\s*:/.test(line));

  if (!statusLine) {
    return "";
  }

  const match = statusLine.match(/^(?:Status|Állapot)\s*:\s*(.+)$/);
  return match ? match[1].trim() : "";
}

function hasNeedsClarificationMarkers(specContent) {
  return /\[NEEDS CLARIFICATION Q\d{3}:/i.test(specContent);
}

function hasOpenQuestions(specContent) {
  const openQuestionLine = /^\s*-\s*\[\s\]\s*Q\d{3}\s*:/m.test(specContent);
  const openStatusLine = /Státusz\s*:\s*OPEN|Status\s*:\s*OPEN/i.test(specContent);
  return openQuestionLine || openStatusLine;
}

function validateSpecReadyForPlan(specPath) {
  if (!fs.existsSync(specPath)) {
    throw new Error(`Validation error: missing spec file: ${relativeToWorkDir(specPath)}`);
  }

  const content = fs.readFileSync(specPath, "utf8");
  const status = parseSpecStatus(content);
  const isReady = status === "READY_FOR_PLAN";

  if (!isReady) {
    throw new Error(
      "A spec még DRAFT állapotban van, ezért nem indítható a plan fázis.\nElőbb fejezd be a spec tisztázását a `berkispec spec` fázisban, majd csak akkor lépj tovább, ha a spec státusza READY_FOR_PLAN."
    );
  }

  if (hasNeedsClarificationMarkers(content)) {
    throw new Error("Validation error: a spec még tartalmaz [NEEDS CLARIFICATION ...] markert.");
  }

  if (hasOpenQuestions(content)) {
    throw new Error("Validation error: a Nyitott kérdések szekcióban maradt OPEN vagy kipipálatlan kérdés.");
  }
}

function isSpecReadyForPlan(specPath) {
  if (!fs.existsSync(specPath)) {
    return false;
  }

  const content = fs.readFileSync(specPath, "utf8");
  return parseSpecStatus(content) === "READY_FOR_PLAN" && !hasNeedsClarificationMarkers(content) && !hasOpenQuestions(content);
}

function ensureSpecStatusField(specPath, language) {
  if (!fs.existsSync(specPath)) {
    return false;
  }

  const content = fs.readFileSync(specPath, "utf8");
  if (/^(Status|Állapot)\s*:/m.test(content) || /^##\s*(Status|Állapot)\b/m.test(content)) {
    return false;
  }

  const statusHeader = language === "EN" ? "## Status\n\nDRAFT\n\n" : "## Állapot\n\nDRAFT\n\n";
  const updated = content.startsWith("# ")
    ? content.replace(/^# [^\n]*\n+/, (title) => `${title}${statusHeader}`)
    : `${statusHeader}${content}`;

  fs.writeFileSync(specPath, updated, "utf8");
  return true;
}

function ensureCodexAvailable(command) {
  const result = spawnSync(command, ["--version"], { stdio: "ignore" });
  if (result.error || result.status !== 0) {
    throw new Error("Codex CLI nem elérhető. Telepítsd és futtasd külön: codex login");
  }
}

async function askSpecIterationInput(rl, language) {
  if (language === "EN") {
    output.write("Add clarifications. Use /done to send to Codex, /finish to close spec phase.\n\n");
  } else {
    output.write("Adj pontosításokat. /done: küldés a Codexnek, /finish: spec fázis lezárása.\n\n");
  }

  const lines = [];

  while (true) {
    const line = await ask(rl, "> ");
    const command = line.trim();

    if (command === "/finish") {
      return { type: "finish", text: lines.join("\n").trim() };
    }

    if (command === "/done") {
      return { type: "done", text: lines.join("\n").trim() };
    }

    lines.push(line);
  }
}

function buildCyclePrompt({ phase, cycle, language }) {
  const promptName = phases.find((item) => item.id === phase)?.promptName;
  const promptFile = projectPromptReference(promptName);
  const base = `specs/${cycle}`;

  if (language === "EN") {
    const phaseText = {
      plan: `Use the ${promptFile} prompt.

Create an implementation plan for this cycle:

${base}/spec.md

The plan location:

${base}/plan.md`,
      tasks: `Use the ${promptFile} prompt.

Create an execution task list for this cycle:

${base}/spec.md
${base}/plan.md

The task list location:

${base}/tasks.md`,
      implement: `Use the ${promptFile} prompt.

Execute this cycle:

${base}/spec.md
${base}/plan.md
${base}/tasks.md`,
      validate: `Use the ${promptFile} prompt.

Validate the closure of this cycle:

${base}/spec.md
${base}/plan.md
${base}/tasks.md`
    };

    return phaseText[phase];
  }

  const phaseText = {
    plan: `Használd a ${promptFile} promptot.

Készíts implementációs tervet ehhez a ciklushoz:

${base}/spec.md

A terv helye:

${base}/plan.md`,
    tasks: `Használd a ${promptFile} promptot.

Készíts végrehajtási task listát ehhez a ciklushoz:

${base}/spec.md
${base}/plan.md

A task lista helye:

${base}/tasks.md`,
    implement: `Használd a ${promptFile} promptot.

Hajtsd végre ezt a ciklust:

${base}/spec.md
${base}/plan.md
${base}/tasks.md`,
    validate: `Használd a ${promptFile} promptot.

Validáld ennek a ciklusnak a lezárását:

${base}/spec.md
${base}/plan.md
${base}/tasks.md`
  };

  return phaseText[phase];
}

function printNextStep(phase, cycle = "") {
  const nextByPhase = {
    init: "berkispec project",
    project: "berkispec spec",
    spec: `berkispec plan ${cycle}`,
    plan: `berkispec tasks ${cycle}`,
    tasks: `berkispec implement ${cycle}`,
    implement: `berkispec validate ${cycle}`,
    validate: "No next phase. Cycle is ready for review."
  };

  output.write(`Next step: ${nextByPhase[phase]}\n`);
}

function printProjectDesc({ summary, files }) {
  output.write("\nCurrent project description:\n\n");
  output.write(summary.length > 0 ? `${summary}\n\n` : "(No summary yet)\n\n");
  output.write("Reference files:\n");

  if (files.length === 0) {
    output.write("(No files yet)\n\n");
    return;
  }

  files.forEach((file) => {
    output.write(`- ${file}\n`);
  });
  output.write("\n");
}

async function chooseProjectAction(rl) {
  output.write("Project action:\n");
  output.write("  1. add description\n");
  output.write("  2. add files\n");
  output.write("  3. show current\n");
  output.write("  4. finish\n");

  while (true) {
    const value = (await ask(rl, "\nAction: ")).trim().toLowerCase();
    const actions = {
      "1": "add-description",
      "2": "add-files",
      "3": "show-current",
      "4": "finish",
      "add description": "add-description",
      "add files": "add-files",
      "show current": "show-current",
      finish: "finish"
    };

    if (actions[value]) {
      return actions[value];
    }

    output.write(`Unknown action: ${value}\n`);
  }
}

async function promptForFiles(rl) {
  output.write("Add project files. Type /done on its own line to finish.\n");
  output.write("Tab completion is available for paths inside the current working directory.\n\n");

  const files = [];
  completerState.mode = "file";

  try {
    while (true) {
      const value = (await ask(rl, "File path: ")).trim();

      if (value === "/done") {
        break;
      }

      if (value.length === 0) {
        continue;
      }

      let absolutePath;
      try {
        absolutePath = normalizeProjectPath(value);
      } catch (error) {
        output.write(`${error.message}\n`);
        continue;
      }

      if (!fs.existsSync(absolutePath)) {
        output.write("Path does not exist.\n");
        continue;
      }

      if (!fs.statSync(absolutePath).isFile()) {
        output.write("Please choose a file, not a directory.\n");
        continue;
      }

      const relativePath = relativeToWorkDir(absolutePath);
      files.push(relativePath);
      output.write(`Added: ${relativePath}\n`);
    }
  } finally {
    completerState.mode = "none";
  }

  return files;
}

async function runInit(rl) {
  ensureProjectDescTemplate();

  while (true) {
    const currentLanguage = getProjectLanguage();

    if (currentLanguage) {
      const copied = copyProjectPrompts(currentLanguage);
      output.write(`Current project language: ${currentLanguage}\n`);
      output.write(`Prompt directory: ${relativeToWorkDir(projectPromptsDir)}\n`);
      output.write(copied > 0 ? `Copied ${copied} prompt file(s).\n` : "Prompt files already prepared.\n");
    }

    const action = await chooseInitAction(rl);

    if (action === "finish") {
      if (!getProjectLanguage()) {
        output.write("Project language is required before init can finish.\n");
        continue;
      }

      output.write(`Created or verified: ${relativeToWorkDir(stateDir)}\n`);
      output.write(`Config file: ${relativeToWorkDir(configPath)}\n`);
      output.write(`Project description file: ${relativeToWorkDir(projectDescPath)}\n`);
      output.write(`Project prompts: ${relativeToWorkDir(projectPromptsDir)}\n`);
      printNextStep("init");
      return;
    }

    if (action === "select-language") {
      if (currentLanguage) {
        output.write(`Project language is already locked: ${currentLanguage}\n`);
        output.write("Changing the project language is not supported.\n");
        continue;
      }

      const projectLanguage = await chooseProjectLanguage(rl);
      writeConfig({ ...readConfig(), projectLanguage });
      const copied = copyProjectPrompts(projectLanguage);

      output.write(`Project language selected: ${projectLanguage}\n`);
      output.write(`Copied ${copied} prompt file(s) to ${relativeToWorkDir(projectPromptsDir)}.\n`);
    }
  }
}

async function runProject(rl) {
  ensureProjectDescTemplate();

  const state = readProjectDesc();

  while (true) {
    const action = await chooseProjectAction(rl);

    if (action === "finish") {
      writeProjectDesc(state);
      output.write(`Updated: ${relativeToWorkDir(projectDescPath)}\n`);
      printNextStep("project");
      return;
    }

    if (action === "show-current") {
      printProjectDesc(state);
      continue;
    }

    if (action === "add-description") {
      const description = await askMultiline(rl, "Project description", { required: false });

      if (description.length === 0) {
        output.write("No description added.\n");
        continue;
      }

      state.summary = state.summary.length > 0 ? `${state.summary}\n\n${description}` : description;
      writeProjectDesc(state);
      output.write("Description updated.\n");
      continue;
    }

    if (action === "add-files") {
      const files = await promptForFiles(rl);

      if (files.length === 0) {
        output.write("No files added.\n");
        continue;
      }

      state.files = [...new Set([...state.files, ...files])];
      writeProjectDesc(state);
      output.write(`Added ${files.length} file(s).\n`);
    }
  }
}

async function runSpec(rl, language) {
  if (!hasProjectContext()) {
    throw new Error("Validacios hiba: a spec fazis elott kotelezo lefuttatni a `berkispec project` parancsot.");
  }

  const codexConfig = getCodexConfig();
  if (!codexConfig.enabled) {
    throw new Error("Validation error: codex.enabled=false, ezért a spec fázis nem futtatható.");
  }

  ensureCodexAvailable(codexConfig.command);

  const name = await askRequired(rl, "Name");
  const goal = await askMultiline(rl, "Goal", { required: true });
  const result = buildSpecPrompt({ name, goal, language });
  const target = createSpecTarget({ targetPath: result.targetPath });

  output.write(`\nRunning Codex for initial spec draft: ${result.cycle}\n\n`);
  const firstResult = await runCodex(result.prompt, {
    command: codexConfig.command,
    mode: codexConfig.mode,
    cwd: workDir,
    sandbox: codexConfig.sandbox,
    approval: codexConfig.approval
  });

  if (fs.existsSync(target.path) && ensureSpecStatusField(target.path, language)) {
    output.write("Megjegyzés: a spec fájlból hiányzott a státusz mező, ezért automatikusan hozzáadtam: DRAFT.\n");
  } else if (!fs.existsSync(target.path)) {
    output.write(`Megjegyzés: a spec fájl még nem jött létre: ${relativeToWorkDir(target.path)}\n`);
    output.write("A spec fázis interaktív módban marad, így válaszolhatsz a modell kérdéseire.\n");
  }

  let lastCodexResponse = firstResult.stdout.trim() || firstResult.stderr.trim();

  while (true) {
    const inputResult = await askSpecIterationInput(rl, language);

    if (inputResult.type === "finish") {
      if (!fs.existsSync(target.path)) {
        output.write(`Figyelem: a spec fájl nem jött létre: ${relativeToWorkDir(target.path)}\n`);
        output.write("A spec fázis lezárult, de a plan fázis nem indítható, amíg nincs spec.md.\n");
        return;
      }

      const ready = isSpecReadyForPlan(target.path);
      output.write(`Spec file: ${relativeToWorkDir(target.path)}\n`);
      if (!ready) {
        output.write("Figyelem: a spec még nem READY_FOR_PLAN, ezért a plan fázis blokkolva lesz.\n");
      }
      printNextStep("spec", result.cycle);
      return;
    }

    if (inputResult.text.length === 0) {
      output.write("No clarification provided. Add details before /done, or use /finish.\n");
      continue;
    }

    const modifyPrompt = buildSpecModifyPrompt({
      specPath: result.targetPath,
      lastCodexResponse,
      userInput: inputResult.text,
      language
    });

    output.write("\nRunning Codex to update spec...\n\n");
    const modifyResult = await runCodex(modifyPrompt, {
      command: codexConfig.command,
      mode: codexConfig.mode,
      cwd: workDir,
      sandbox: codexConfig.sandbox,
      approval: codexConfig.approval
    });
    lastCodexResponse = modifyResult.stdout.trim() || modifyResult.stderr.trim();

    if (fs.existsSync(target.path) && ensureSpecStatusField(target.path, language)) {
      output.write("Megjegyzés: a spec módosítás után hiányzott a státusz mező, ezért automatikusan hozzáadtam: DRAFT.\n");
    } else if (!fs.existsSync(target.path)) {
      output.write(`Megjegyzés: a spec fájl még nem jött létre: ${relativeToWorkDir(target.path)}\n`);
    }
  }
}

async function runCyclePhase(rl, phase, cycleArg, language) {
  const cycle = cycleArg ?? (await chooseCycle(rl));
  if (phase === "plan") {
    const specPath = path.join(workDir, "specs", cycle, "spec.md");
    validateSpecReadyForPlan(specPath);
  }
  const prompt = buildCyclePrompt({ phase, cycle, language });

  printPrompt(prompt);
  printNextStep(phase, cycle);
}

function printHelp() {
  output.write(`berkispec

Interactive:
  ./berkispec
  Choose 8. exit to quit.
  Run init first and select HU or EN once for the project.

Non-interactive:
  ./berkispec init
  ./berkispec project
  ./berkispec spec
  ./berkispec plan <cycle>
  ./berkispec tasks <cycle>
  ./berkispec implement <cycle>
  ./berkispec validate <cycle>

Current working directory:
  ${workDir}

Multiline input ends with:
  /done
`);
}

async function runPhase(rl, phase, cycleArg) {
  if (!phases.some((item) => item.id === phase)) {
    throw new Error(`Unknown phase: ${phase}`);
  }

  if (phase === "init") {
    await runInit(rl);
    return;
  }

  const projectLanguage = ensureInitialized();

  if (phase === "project") {
    await runProject(rl);
    return;
  }

  if (phase === "spec") {
    await runSpec(rl, projectLanguage);
    return;
  }

  await runCyclePhase(rl, phase, cycleArg, projectLanguage);
}

async function main() {
  const [, , phaseArg, cycleArg] = process.argv;

  if (phaseArg === "--help" || phaseArg === "-h") {
    printHelp();
    return;
  }

  const rl = readline.createInterface({ input, output, completer });

  try {
    if (phaseArg) {
      await runPhase(rl, phaseArg, cycleArg);
      return;
    }

    while (true) {
      const phase = await choosePhase(rl);

      if (phase === "exit") {
        output.write("Exiting berkispec.\n");
        return;
      }

      try {
        await runPhase(rl, phase);
      } catch (error) {
        output.write(`berkispec error: ${error.message}\n`);
      }

      output.write("\n");
    }
  } finally {
    rl.close();
  }
}

main().catch((error) => {
  console.error(`berkispec error: ${error.message}`);
  process.exitCode = 1;
});
