#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  AOS Package Validator v1.0
  Generic validation tool for Cowork development packages
═══════════════════════════════════════════════════════════════════

Usage:
  python3 aos_package_validator.py <config.json>

The config JSON defines the package scope and references.
The validator runs all checks and produces a structured report.

Schema: see VALIDATOR_SCHEMA below or the companion config template.
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# ─── Schema Documentation ───────────────────────────────────────

VALIDATOR_SCHEMA = """
{
  "package_id":       "(required) str — unique package identifier, e.g. S005-P004",
  "version":          "(required) str — package version, e.g. v4",
  "package_root":     "(required) str — absolute path to package root on disk",
  "source_root_label":"(required) str — the label used in docs to reference assets, e.g. SOURCE_ROOT",
  "source_root_rel":  "(required) str — relative path from package_root to assets, e.g. assets",
  "output_rel":       "(optional) str — relative output dir under source_root, e.g. output",

  "instruction_file": "(required) str — path to Instructions file relative to package_root",
  "prompt_file":      "(required) str — path to Activation Prompt file relative to package_root",
  "doc_files":        "(optional) [str] — other doc files to scan, relative to package_root",

  "manifest": {
    "(required) dict — expected files, keys are relative paths from source_root": {
      "role": "(required) str — one of: modify, create, read-only",
      "wp":   "(optional) str — which work package, e.g. WP001"
    }
  },

  "work_packages": [
    {
      "id":          "(required) str — e.g. WP001",
      "spec_file":   "(required) str — LOD400 spec path relative to source_root",
      "mandate_file":"(required) str — Mandate path relative to source_root",
      "modify_files":"(required) [str] — files this WP modifies, relative to source_root",
      "create_files":"(optional) [str] — new files this WP creates"
    }
  ],

  "shell_variables": {
    "(optional) dict — variables that must be resolved (not literal) in shell commands": {
      "VARNAME": "expected_value_or_pattern"
    }
  },

  "field_renames": {
    "(optional) dict — old field names that should NOT appear in output (except fallbacks)": {
      "old_name": {"new_name": "str", "fallback_pattern": "optional regex for allowed uses"}
    }
  },

  "path_references": {
    "(optional) dict — paths referenced in mandates/specs that should resolve": {
      "referenced_path": "expected_actual_path_relative_to_source_root_or_INVALID"
    }
  },

  "cowork_capabilities": [
    "(optional) [str] — capabilities the Instructions file should declare, e.g. Shell, Python, Edit"
  ]
}
"""


# ─── Data Structures ────────────────────────────────────────────

@dataclass
class Finding:
    """A single validation finding."""
    check_id: str
    severity: str      # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str      # FILE, PATH, COMMAND, FIELD, COWORK, CROSS_REF, STRUCTURE
    title: str
    detail: str
    file: str = ""
    line: int = 0
    suggestion: str = ""

@dataclass
class CheckResult:
    """Result of a single check category."""
    category: str
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    findings: list = field(default_factory=list)

@dataclass
class ValidationReport:
    """Full validation report."""
    package_id: str
    version: str
    timestamp: str
    overall_pass: bool = True
    score: float = 0.0
    results: list = field(default_factory=list)  # list[CheckResult]
    summary: dict = field(default_factory=dict)


# ─── Validator Engine ────────────────────────────────────────────

class PackageValidator:
    """Generic AOS package validator."""

    def __init__(self, config: dict):
        self.config = config
        self.pkg_root = Path(config["package_root"])
        self.src_root = self.pkg_root / config.get("source_root_rel", "assets")
        self.src_label = config.get("source_root_label", "SOURCE_ROOT")
        self.output_rel = config.get("output_rel", "output")
        self.findings: list[Finding] = []
        self.check_counts = {"total": 0, "passed": 0, "failed": 0}

    def _add_finding(self, **kwargs):
        f = Finding(**kwargs)
        self.findings.append(f)

    def _pass(self):
        self.check_counts["total"] += 1
        self.check_counts["passed"] += 1

    def _fail(self):
        self.check_counts["total"] += 1
        self.check_counts["failed"] += 1

    # ── CHECK 1: File Existence ──────────────────────────────────

    def check_manifest_files(self) -> CheckResult:
        """Verify all manifest files exist on disk."""
        result = CheckResult(category="FILE_EXISTS")
        manifest = self.config.get("manifest", {})

        for rel_path, meta in manifest.items():
            result.total_checks += 1
            full_path = self.src_root / rel_path
            if full_path.exists():
                result.passed += 1
            else:
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="FILE_EXISTS",
                    severity="CRITICAL" if meta.get("role") in ("modify", "create") else "MEDIUM",
                    category="FILE",
                    title=f"Missing manifest file: {rel_path}",
                    detail=f"Expected at: {full_path}",
                    file=rel_path,
                    suggestion="Verify the file path in the manifest matches the actual package structure."
                )
                continue
            self._pass()

        # Check instruction and prompt files
        for label, key in [("Instructions", "instruction_file"), ("Activation Prompt", "prompt_file")]:
            result.total_checks += 1
            rel = self.config.get(key, "")
            if rel and (self.pkg_root / rel).exists():
                result.passed += 1
                self._pass()
            else:
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="FILE_EXISTS",
                    severity="CRITICAL",
                    category="FILE",
                    title=f"Missing {label} file: {rel}",
                    detail=f"Expected at: {self.pkg_root / rel}",
                    file=rel,
                    suggestion=f"Ensure {label} file exists at the specified path."
                )

        return result

    # ── CHECK 2: Path Resolution in Commands ─────────────────────

    def check_path_resolution(self) -> CheckResult:
        """Verify shell commands don't use unresolved variable labels."""
        result = CheckResult(category="PATH_RESOLUTION")
        label = self.src_label

        files_to_scan = []
        for key in ["instruction_file", "prompt_file"]:
            rel = self.config.get(key, "")
            if rel:
                files_to_scan.append((key, self.pkg_root / rel))
        for doc in self.config.get("doc_files", []):
            files_to_scan.append(("doc", self.pkg_root / doc))

        # Patterns that indicate unresolved variable usage in shell context
        shell_command_prefixes = [
            r'^\s*(grep|python3?|bash|sh|cd|cat|ls|mkdir|find|diff|pytest)\s',
            r'^\s*\$\s',
            r'import\s+json.*open\(',
            r'sys\.path\.insert',
        ]
        shell_pattern = re.compile('|'.join(shell_command_prefixes))

        for file_label, fpath in files_to_scan:
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding="utf-8", errors="replace")
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                # Check if line looks like a shell command or python one-liner
                stripped = line.strip()
                is_shell_context = bool(shell_pattern.search(stripped))
                # Also catch: paths used as string arguments like open('SOURCE_ROOT/...')
                # But exclude resolved variable references: $SOURCE_ROOT, ${SOURCE_ROOT}
                has_quoted_label = re.search(
                    rf"""['"](?<!\$)({re.escape(label)}/[^'"]+)['"]""", stripped
                )
                # Exclude $VAR and ${VAR} — those are properly resolved
                if has_quoted_label:
                    # Double-check: is the label preceded by $ inside the quotes?
                    match_start = has_quoted_label.start(1)
                    if match_start > 0 and stripped[match_start - 1] == '$':
                        has_quoted_label = None
                has_unquoted_label = re.search(
                    rf'(?<![$"\'])\b{re.escape(label)}/\S+', stripped
                )

                if is_shell_context and has_unquoted_label:
                    result.total_checks += 1
                    result.failed += 1
                    self._fail()
                    self._add_finding(
                        check_id="PATH_LITERAL_IN_SHELL",
                        severity="CRITICAL",
                        category="COMMAND",
                        title=f"Unresolved '{label}' in shell command",
                        detail=f"Line {i}: {stripped[:120]}",
                        file=str(fpath.relative_to(self.pkg_root)),
                        line=i,
                        suggestion=f"Replace literal '{label}' with a resolved shell variable: ${label} (defined via export at session start), or use absolute paths."
                    )
                elif has_quoted_label:
                    result.total_checks += 1
                    result.failed += 1
                    self._fail()
                    self._add_finding(
                        check_id="PATH_LITERAL_IN_STRING",
                        severity="CRITICAL",
                        category="COMMAND",
                        title=f"Unresolved '{label}' in string literal",
                        detail=f"Line {i}: {stripped[:120]}",
                        file=str(fpath.relative_to(self.pkg_root)),
                        line=i,
                        suggestion=f"Use f-string or variable expansion instead of literal '{label}' in Python strings."
                    )
                elif is_shell_context and label not in stripped:
                    result.total_checks += 1
                    result.passed += 1
                    self._pass()

        # If no shell commands found at all, note it
        if result.total_checks == 0:
            result.total_checks = 1
            result.passed = 1
            self._pass()

        return result

    # ── CHECK 3: SOURCE_ROOT Definition Consistency ──────────────

    def check_source_root_definition(self) -> CheckResult:
        """Verify SOURCE_ROOT is defined consistently across documents."""
        result = CheckResult(category="SOURCE_ROOT_CONSISTENCY")
        label = self.src_label
        expected_rel = self.config.get("source_root_rel", "assets")
        definitions_found = []

        files_to_scan = []
        for key in ["instruction_file", "prompt_file"]:
            rel = self.config.get(key, "")
            if rel:
                files_to_scan.append((key, self.pkg_root / rel))

        for file_label, fpath in files_to_scan:
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding="utf-8", errors="replace")
            # Look for definition patterns like: SOURCE_ROOT = "mnt/S005-P004/assets"
            defs = re.findall(
                rf'{re.escape(label)}\s*=\s*["\']?([^"\'\n]+)["\']?',
                content
            )
            for d in defs:
                definitions_found.append((file_label, d.strip()))

        result.total_checks += 1
        if not definitions_found:
            result.failed += 1
            self._fail()
            self._add_finding(
                check_id="SOURCE_ROOT_UNDEFINED",
                severity="HIGH",
                category="PATH",
                title=f"No definition of {label} found",
                detail=f"Neither Instructions nor Activation Prompt defines {label}.",
                suggestion=f"Add a clear definition: {label} = \"<absolute_or_mount_path>\""
            )
        else:
            # Check consistency
            values = set(d[1] for d in definitions_found)
            if len(values) > 1:
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="SOURCE_ROOT_INCONSISTENT",
                    severity="HIGH",
                    category="PATH",
                    title=f"Inconsistent {label} definitions",
                    detail=f"Found different values: {definitions_found}",
                    suggestion=f"Use identical definition in all files."
                )
            else:
                result.passed += 1
                self._pass()

        # Check if defined value is a conceptual label vs actionable path
        result.total_checks += 1
        for file_label, val in definitions_found:
            if not val.startswith("/") and not val.startswith("$"):
                # Relative path — check if prompt file uses it in commands without export
                prompt_rel = self.config.get("prompt_file", "")
                if prompt_rel:
                    prompt_path = self.pkg_root / prompt_rel
                    if prompt_path.exists():
                        prompt_content = prompt_path.read_text(encoding="utf-8", errors="replace")
                        # Check if there's an actual export/variable assignment
                        has_export = bool(re.search(
                            rf'(export\s+{re.escape(label)}|{re.escape(label)}=.*\n.*(?:grep|python|mkdir))',
                            prompt_content
                        ))
                        if not has_export:
                            result.failed += 1
                            self._fail()
                            self._add_finding(
                                check_id="SOURCE_ROOT_NOT_EXPORTED",
                                severity="CRITICAL",
                                category="COMMAND",
                                title=f"{label} defined conceptually but never exported as shell variable",
                                detail=f"Value '{val}' in {file_label} is a relative path shown as documentation, but shell commands use it literally. No 'export {label}=...' or equivalent found in activation prompt.",
                                suggestion=f"Add at the start of the activation prompt:\n  First, set up your working root:\n    export {label}=\"/sessions/*/mnt/.../{expected_rel}\"\n  Then all subsequent commands can use ${label}/..."
                            )
                            break
            else:
                result.passed += 1
                self._pass()
                break
        else:
            if not definitions_found:
                pass  # already flagged above

        return result

    # ── CHECK 4: Cross-Reference Integrity ───────────────────────

    def check_cross_references(self) -> CheckResult:
        """Verify paths referenced in mandates/specs actually exist."""
        result = CheckResult(category="CROSS_REFERENCE")
        path_refs = self.config.get("path_references", {})

        for ref_path, expected in path_refs.items():
            result.total_checks += 1
            if expected == "INVALID":
                result.passed += 1
                self._pass()
                self._add_finding(
                    check_id="CROSS_REF_INVALID",
                    severity="INFO",
                    category="CROSS_REF",
                    title=f"Known invalid path reference: {ref_path}",
                    detail=f"This path is referenced in spec/mandate documents but does not exist in the package (marked INVALID in config).",
                    suggestion=f"Update the reference to match actual package structure if this is unintentional."
                )
            else:
                actual = self.src_root / expected
                if actual.exists():
                    result.passed += 1
                    self._pass()
                else:
                    result.failed += 1
                    self._fail()
                    self._add_finding(
                        check_id="CROSS_REF_MISSING",
                        severity="MEDIUM",
                        category="CROSS_REF",
                        title=f"Referenced path does not exist: {expected}",
                        detail=f"Original ref: {ref_path} → mapped to: {actual}",
                        suggestion="Either create the file or update the reference."
                    )

        if result.total_checks == 0:
            result.total_checks = 1
            result.passed = 1
            self._pass()

        return result

    # ── CHECK 5: Work Package Completeness ───────────────────────

    def check_work_packages(self) -> CheckResult:
        """Verify WP specs and mandates exist and reference valid files."""
        result = CheckResult(category="WORK_PACKAGE_COMPLETENESS")
        wps = self.config.get("work_packages", [])

        for wp in wps:
            wp_id = wp["id"]

            # Check spec file
            result.total_checks += 1
            spec = self.src_root / wp["spec_file"]
            if spec.exists():
                result.passed += 1
                self._pass()
            else:
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="WP_SPEC_MISSING",
                    severity="CRITICAL",
                    category="FILE",
                    title=f"{wp_id}: LOD400 spec missing",
                    detail=f"Expected: {spec}",
                    file=wp["spec_file"]
                )

            # Check mandate file
            result.total_checks += 1
            mandate = self.src_root / wp["mandate_file"]
            if mandate.exists():
                result.passed += 1
                self._pass()
            else:
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="WP_MANDATE_MISSING",
                    severity="CRITICAL",
                    category="FILE",
                    title=f"{wp_id}: Mandate missing",
                    detail=f"Expected: {mandate}",
                    file=wp["mandate_file"]
                )

            # Check all modify targets exist
            for mf in wp.get("modify_files", []):
                result.total_checks += 1
                target = self.src_root / mf
                if target.exists():
                    result.passed += 1
                    self._pass()
                else:
                    result.failed += 1
                    self._fail()
                    self._add_finding(
                        check_id="WP_TARGET_MISSING",
                        severity="HIGH",
                        category="FILE",
                        title=f"{wp_id}: Modify target missing: {mf}",
                        detail=f"Expected: {target}",
                        file=mf,
                        suggestion="File listed for modification does not exist in source."
                    )

        return result

    # ── CHECK 6: Output Directory Setup ──────────────────────────

    def check_output_structure(self) -> CheckResult:
        """Verify output directory instructions exist."""
        result = CheckResult(category="OUTPUT_STRUCTURE")

        # Check if instructions mention creating output dirs
        prompt_rel = self.config.get("prompt_file", "")
        instr_rel = self.config.get("instruction_file", "")
        found_mkdir = False
        found_output_ref = False

        for rel in [instr_rel, prompt_rel]:
            if not rel:
                continue
            fpath = self.pkg_root / rel
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding="utf-8", errors="replace")
            if "mkdir" in content:
                found_mkdir = True
            if self.output_rel in content:
                found_output_ref = True

        result.total_checks += 1
        if found_output_ref:
            result.passed += 1
            self._pass()
        else:
            result.failed += 1
            self._fail()
            self._add_finding(
                check_id="OUTPUT_DIR_NO_REF",
                severity="HIGH",
                category="STRUCTURE",
                title="No reference to output directory in instructions",
                detail=f"Expected mention of '{self.output_rel}/' directory.",
                suggestion=f"Add clear instruction: 'Write modified files to {self.src_label}/{self.output_rel}/ preserving directory structure.'"
            )

        result.total_checks += 1
        if found_mkdir:
            result.passed += 1
            self._pass()
        else:
            result.failed += 1
            self._fail()
            self._add_finding(
                check_id="OUTPUT_DIR_NO_MKDIR",
                severity="LOW",
                category="STRUCTURE",
                title="No explicit mkdir instruction for output directory",
                detail="Agent may fail if output subdirectories don't exist.",
                suggestion=f"Add: mkdir -p ${self.src_label}/{self.output_rel}/src/shaked_wg_agent/{{scrapers,notifier,api,publisher}} ${self.src_label}/{self.output_rel}/data/profiles ${self.src_label}/{self.output_rel}/tests"
            )

        return result

    # ── CHECK 7: Cowork Capability Declaration ───────────────────

    def check_cowork_capabilities(self) -> CheckResult:
        """Verify Instructions declares required Cowork capabilities."""
        result = CheckResult(category="COWORK_CAPABILITIES")
        expected_caps = self.config.get("cowork_capabilities", [])

        if not expected_caps:
            result.total_checks = 1
            result.passed = 1
            self._pass()
            return result

        instr_rel = self.config.get("instruction_file", "")
        if not instr_rel:
            return result
        fpath = self.pkg_root / instr_rel
        if not fpath.exists():
            return result

        content = fpath.read_text(encoding="utf-8", errors="replace").lower()

        for cap in expected_caps:
            result.total_checks += 1
            if cap.lower() in content:
                result.passed += 1
                self._pass()
            else:
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="COWORK_CAP_MISSING",
                    severity="MEDIUM",
                    category="COWORK",
                    title=f"Capability not declared: {cap}",
                    detail=f"Instructions file does not mention '{cap}'.",
                    file=instr_rel,
                    suggestion=f"Add '{cap}' to the environment capabilities section."
                )

        # Check for contradictory statements
        result.total_checks += 1
        contradictions = [
            (r'cannot\s+run\s+shell', "Says shell cannot be run"),
            (r'cannot\s+execute\s+python', "Says Python cannot be executed"),
            (r'no\s+shell\s+access', "Says no shell access"),
            (r'isolated\s+environment.*cannot', "Describes overly restrictive environment"),
        ]
        found_contradiction = False
        for pattern, desc in contradictions:
            if re.search(pattern, content):
                found_contradiction = True
                result.failed += 1
                self._fail()
                self._add_finding(
                    check_id="COWORK_CONTRADICTION",
                    severity="CRITICAL",
                    category="COWORK",
                    title=f"Contradictory capability statement: {desc}",
                    detail="Instructions contain language that disables Cowork capabilities.",
                    file=instr_rel,
                    suggestion="Remove or correct the statement. Cowork has full Shell, Python, and file tool access."
                )
                break
        if not found_contradiction:
            result.passed += 1
            self._pass()

        return result

    # ── CHECK 8: Field Rename Consistency ────────────────────────

    def check_field_renames(self) -> CheckResult:
        """Verify old field names are documented for rename, and specs mention new names."""
        result = CheckResult(category="FIELD_RENAMES")
        renames = self.config.get("field_renames", {})

        if not renames:
            result.total_checks = 1
            result.passed = 1
            self._pass()
            return result

        # Scan source files for old field names (should exist = proves they need renaming)
        src_dir = self.src_root / "src"
        if src_dir.exists():
            py_files = list(src_dir.rglob("*.py"))
            for old_name, meta in renames.items():
                result.total_checks += 1
                new_name = meta.get("new_name", "")
                found_old = False
                for pyf in py_files:
                    content = pyf.read_text(encoding="utf-8", errors="replace")
                    if old_name in content:
                        found_old = True
                        break
                if found_old:
                    result.passed += 1  # Good — confirms rename is needed
                    self._pass()
                else:
                    # Old name not found — might already be renamed or wrong
                    result.passed += 1
                    self._pass()
                    self._add_finding(
                        check_id="FIELD_RENAME_INFO",
                        severity="INFO",
                        category="FIELD",
                        title=f"Old field '{old_name}' not found in source",
                        detail=f"May already be renamed to '{new_name}' or spec references wrong name."
                    )

        # Check that specs mention the new names
        specs_dir = self.src_root / "specs"
        if specs_dir.exists():
            spec_files = list(specs_dir.glob("LOD400*.md"))
            for old_name, meta in renames.items():
                new_name = meta.get("new_name", "")
                if not new_name:
                    continue
                result.total_checks += 1
                found_new_in_spec = False
                for sf in spec_files:
                    content = sf.read_text(encoding="utf-8", errors="replace")
                    if new_name in content:
                        found_new_in_spec = True
                        break
                if found_new_in_spec:
                    result.passed += 1
                    self._pass()
                else:
                    result.failed += 1
                    self._fail()
                    self._add_finding(
                        check_id="FIELD_NEW_NAME_NOT_IN_SPEC",
                        severity="HIGH",
                        category="FIELD",
                        title=f"New field name '{new_name}' not found in any LOD400 spec",
                        detail=f"Rename {old_name}→{new_name} specified in config but '{new_name}' absent from specs."
                    )

        return result

    # ── CHECK 9: Verification Gate Commands ──────────────────────

    def check_verification_gates(self) -> CheckResult:
        """Analyze verification gate commands for correctness."""
        result = CheckResult(category="VERIFICATION_GATES")

        prompt_rel = self.config.get("prompt_file", "")
        if not prompt_rel:
            return result
        fpath = self.pkg_root / prompt_rel
        if not fpath.exists():
            return result

        content = fpath.read_text(encoding="utf-8", errors="replace")
        lines = content.split('\n')

        grep_commands = []
        python_commands = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("grep "):
                grep_commands.append((i, stripped))
            elif stripped.startswith("python3 ") or stripped.startswith("python "):
                python_commands.append((i, stripped))

        # Count total verification commands
        result.total_checks += 1
        total_cmds = len(grep_commands) + len(python_commands)
        if total_cmds > 0:
            result.passed += 1
            self._pass()
            self._add_finding(
                check_id="VERIFY_GATE_COUNT",
                severity="INFO",
                category="COMMAND",
                title=f"Found {total_cmds} verification commands ({len(grep_commands)} grep, {len(python_commands)} python)",
                detail="Verification gates are present in the activation prompt."
            )
        else:
            result.failed += 1
            self._fail()
            self._add_finding(
                check_id="VERIFY_GATE_MISSING",
                severity="HIGH",
                category="COMMAND",
                title="No verification gate commands found in activation prompt",
                detail="Activation prompt should contain grep/python verification commands between WP phases."
            )

        # Check each grep command for common issues
        for line_num, cmd in grep_commands:
            result.total_checks += 1
            issues = []

            # Unescaped regex chars
            if '\\(' in cmd and '--include' not in cmd.split('\\(')[0]:
                pass  # escape is intentional in pattern
            # Missing --include for broad searches on directories (not single files)
            if '-rn' in cmd and '--include' not in cmd and '/src/' in cmd:
                # Check if the path target looks like a directory (ends with /)
                # or a file (has an extension like .py). Single-file grep doesn't need --include.
                path_parts = re.findall(r'(?:^|\s)(?:\$?\w+/\S+)', cmd)
                targets_dir = any(p.rstrip().endswith('/') for p in path_parts)
                if targets_dir:
                    issues.append("Recursive grep without --include filter")

            if issues:
                result.failed += 1
                self._fail()
                for issue in issues:
                    self._add_finding(
                        check_id="VERIFY_GATE_CMD_ISSUE",
                        severity="MEDIUM",
                        category="COMMAND",
                        title=f"Grep command issue: {issue}",
                        detail=f"Line {line_num}: {cmd[:100]}",
                        line=line_num,
                        suggestion="Add --include='*.py' for recursive Python source searches."
                    )
            else:
                result.passed += 1
                self._pass()

        return result

    # ── CHECK 10: WP Dependency Chain ────────────────────────────

    def check_wp_dependency_chain(self) -> CheckResult:
        """Verify activation prompt enforces correct WP execution order."""
        result = CheckResult(category="WP_DEPENDENCY_CHAIN")

        prompt_rel = self.config.get("prompt_file", "")
        if not prompt_rel:
            return result
        fpath = self.pkg_root / prompt_rel
        if not fpath.exists():
            return result

        content = fpath.read_text(encoding="utf-8", errors="replace")
        wps = self.config.get("work_packages", [])
        wp_ids = [wp["id"] for wp in wps]

        # Check linear order enforcement
        result.total_checks += 1
        order_patterns = [
            r'linear\s+execution',
            r'strict\s+(?:linear\s+)?order',
            r'WP001\s*→\s*WP002\s*→\s*WP003',
            r'no\s+skip',
        ]
        found_order = any(re.search(p, content, re.IGNORECASE) for p in order_patterns)
        if found_order:
            result.passed += 1
            self._pass()
        else:
            result.failed += 1
            self._fail()
            self._add_finding(
                check_id="WP_ORDER_NOT_ENFORCED",
                severity="HIGH",
                category="STRUCTURE",
                title="WP linear execution order not explicitly enforced",
                detail="Activation prompt should state strict linear execution order.",
                suggestion="Add: 'IRON RULE: Linear execution WP001 → WP002 → WP003. No skipping.'"
            )

        # Check that WP002/WP003 instructions mention reading from output/ (chaining)
        result.total_checks += 1
        chaining_patterns = [
            r'(?:read|start)\s+from\s+(?:WP001\s+)?output',
            r'output/.*already\s+modified',
            r'read\s+from\s+output/',
        ]
        found_chain = any(re.search(p, content, re.IGNORECASE) for p in chaining_patterns)
        if found_chain:
            result.passed += 1
            self._pass()
        else:
            result.failed += 1
            self._fail()
            self._add_finding(
                check_id="WP_CHAIN_NOT_DOCUMENTED",
                severity="HIGH",
                category="STRUCTURE",
                title="WP output chaining not documented",
                detail="Later WPs should read from output/ of previous WPs, not from original source.",
                suggestion="Add explicit instruction: 'WP002 reads config.py from output/ (modified by WP001).'"
            )

        return result

    # ── ORCHESTRATOR ─────────────────────────────────────────────

    def validate(self) -> ValidationReport:
        """Run all validation checks and produce report."""
        report = ValidationReport(
            package_id=self.config["package_id"],
            version=self.config.get("version", "unknown"),
            timestamp=datetime.now().isoformat(),
        )

        checks = [
            self.check_manifest_files,
            self.check_path_resolution,
            self.check_source_root_definition,
            self.check_cross_references,
            self.check_work_packages,
            self.check_output_structure,
            self.check_cowork_capabilities,
            self.check_field_renames,
            self.check_verification_gates,
            self.check_wp_dependency_chain,
        ]

        for check_fn in checks:
            try:
                result = check_fn()
                report.results.append(result)
            except Exception as e:
                cat_name = getattr(check_fn, '__name__', 'UNKNOWN').replace('check_', '').upper()
                report.results.append(CheckResult(
                    category=cat_name,
                    total_checks=1,
                    failed=1,
                    findings=[Finding(
                        check_id="CHECK_ERROR",
                        severity="HIGH",
                        category="SYSTEM",
                        title=f"Check failed with error: {check_fn.__name__}",
                        detail=str(e)
                    )]
                ))

        # Calculate overall score
        total = sum(r.total_checks for r in report.results)
        passed = sum(r.passed for r in report.results)
        report.score = (passed / total * 100) if total > 0 else 0

        # Overall pass: no CRITICAL findings
        critical = [f for f in self.findings if f.severity == "CRITICAL"]
        report.overall_pass = len(critical) == 0

        # Summary
        severity_counts = {}
        for f in self.findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        report.summary = {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "score_pct": round(report.score, 1),
            "overall_verdict": "PASS" if report.overall_pass else "FAIL",
            "findings_by_severity": severity_counts,
            "total_findings": len(self.findings),
        }

        return report


# ─── Report Formatter ────────────────────────────────────────────

def format_report(report: ValidationReport, findings: list[Finding]) -> str:
    """Format validation report as readable text."""
    lines = []
    lines.append("=" * 72)
    lines.append("  AOS PACKAGE VALIDATION REPORT")
    lines.append("=" * 72)
    lines.append(f"  Package:   {report.package_id} ({report.version})")
    lines.append(f"  Timestamp: {report.timestamp}")
    lines.append(f"  Verdict:   {report.summary['overall_verdict']}")
    lines.append(f"  Score:     {report.summary['score_pct']}% ({report.summary['passed']}/{report.summary['total_checks']} checks passed)")
    lines.append("")

    # Severity summary
    sev = report.summary.get("findings_by_severity", {})
    sev_line = " | ".join(f"{k}: {v}" for k, v in sorted(sev.items(), key=lambda x: ["CRITICAL","HIGH","MEDIUM","LOW","INFO"].index(x[0]) if x[0] in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"] else 99))
    lines.append(f"  Findings:  {report.summary['total_findings']} ({sev_line})")
    lines.append("=" * 72)
    lines.append("")

    # Group findings by severity
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        sev_findings = [f for f in findings if f.severity == severity]
        if not sev_findings:
            continue

        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "ℹ️"}.get(severity, "•")
        lines.append(f"{'─' * 72}")
        lines.append(f"  {icon} {severity} ({len(sev_findings)})")
        lines.append(f"{'─' * 72}")

        for i, f in enumerate(sev_findings, 1):
            lines.append(f"")
            lines.append(f"  [{f.check_id}] {f.title}")
            if f.file:
                loc = f"    File: {f.file}"
                if f.line:
                    loc += f" (line {f.line})"
                lines.append(loc)
            if f.detail:
                lines.append(f"    Detail: {f.detail}")
            if f.suggestion:
                lines.append(f"    Fix: {f.suggestion}")

    lines.append("")
    lines.append("=" * 72)

    # Check results table
    lines.append("")
    lines.append("  CHECK RESULTS BY CATEGORY")
    lines.append(f"  {'Category':<35} {'Pass':>5} {'Fail':>5} {'Total':>6}")
    lines.append(f"  {'─'*35} {'─'*5} {'─'*5} {'─'*6}")
    for r in report.results:
        lines.append(f"  {r.category:<35} {r.passed:>5} {r.failed:>5} {r.total_checks:>6}")
    lines.append(f"  {'─'*35} {'─'*5} {'─'*5} {'─'*6}")
    lines.append(f"  {'TOTAL':<35} {report.summary['passed']:>5} {report.summary['failed']:>5} {report.summary['total_checks']:>6}")

    lines.append("")
    lines.append("=" * 72)
    lines.append(f"  End of report — {report.package_id} {report.version}")
    lines.append("=" * 72)

    return '\n'.join(lines)


# ─── JSON Report ─────────────────────────────────────────────────

def report_to_json(report: ValidationReport, findings: list[Finding]) -> dict:
    """Convert report to JSON-serializable dict."""
    return {
        "package_id": report.package_id,
        "version": report.version,
        "timestamp": report.timestamp,
        "summary": report.summary,
        "results": [
            {
                "category": r.category,
                "total_checks": r.total_checks,
                "passed": r.passed,
                "failed": r.failed,
            }
            for r in report.results
        ],
        "findings": [
            {
                "check_id": f.check_id,
                "severity": f.severity,
                "category": f.category,
                "title": f.title,
                "detail": f.detail,
                "file": f.file,
                "line": f.line,
                "suggestion": f.suggestion,
            }
            for f in findings
        ],
    }


# ─── CLI Entry Point ────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 aos_package_validator.py <config.json>")
        print("\nSchema:")
        print(VALIDATOR_SCHEMA)
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Validate required fields
    required = ["package_id", "package_root", "instruction_file", "prompt_file"]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"ERROR: Missing required config fields: {missing}")
        sys.exit(1)

    validator = PackageValidator(config)
    report = validator.validate()

    # Output text report
    text_report = format_report(report, validator.findings)
    print(text_report)

    # Write JSON report
    json_report = report_to_json(report, validator.findings)
    json_path = config_path.replace('.json', '_report.json')
    if json_path == config_path:
        json_path = config_path + ".report.json"
    with open(json_path, 'w') as f:
        json.dump(json_report, f, indent=2)
    print(f"\nJSON report written to: {json_path}")

    # Exit code
    sys.exit(0 if report.overall_pass else 1)


if __name__ == "__main__":
    main()
