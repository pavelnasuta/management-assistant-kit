from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackageContractTests(unittest.TestCase):
    def test_required_portable_package_files_exist(self):
        required = [
            "README.md",
            "AGENTS.md",
            "LICENSE",
            "docs/quick-start.md",
            "docs/methodology.md",
            "docs/installation.md",
            "skills/management-assistant/SKILL.md",
            "skills/management-assistant/references/shared-contract.md",
            "skills/management-assistant/references/onboarding.md",
            "skills/management-assistant/references/templates.md",
            "skills/management-assistant/references/evaluation.md",
            "skills/management-assistant/references/integrations.md",
            "skills/management-assistant/templates/leader-profile.md",
            "agents/codex/AGENTS.md",
            "agents/claude-code/SKILL.md",
            "agents/hermes/README.md",
            "agents/opencode/AGENTS.md",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_core_skill_has_portable_frontmatter_and_safety_contract(self):
        skill = (ROOT / "skills/management-assistant/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        self.assertRegex(skill, r"(?m)^name: management-assistant$")
        self.assertRegex(skill, r"(?m)^version: 0\.1\.0$")
        self.assertRegex(skill, r"(?m)^license: LicenseRef-Private-Pilot$")
        self.assertIn("явное подтверждение", skill)
        self.assertIn("чтение результата обратно", skill)
        self.assertIn("чувствительные персональные данные", skill)
        for relative_path in [
            "references/onboarding.md",
            "references/templates.md",
            "references/evaluation.md",
            "references/integrations.md",
            "templates/leader-profile.md",
        ]:
            self.assertIn(relative_path, skill)

    def test_agent_adapters_keep_shared_contract(self):
        root_contract = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("skills/management-assistant", root_contract)
        for adapter in [
            "agents/codex/AGENTS.md",
            "agents/claude-code/SKILL.md",
            "agents/hermes/README.md",
            "agents/opencode/AGENTS.md",
        ]:
            content = (ROOT / adapter).read_text(encoding="utf-8")
            self.assertIn("skills/management-assistant", content)
            self.assertIn("external actions", content)
            self.assertTrue(
                "AGENTS.md" in content or "references/shared-contract.md" in content,
                adapter,
            )

    def test_no_private_context_or_absolute_paths_in_shippable_text(self):
        forbidden = ["ОМАИС", "ЦИП", "/root/", "GITHUB_TOKEN=", "Pavel Nasuta"]
        files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts and "tests" not in path.parts]
        findings = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    findings.append(f"{path.relative_to(ROOT)}: {token}")
        self.assertEqual(findings, [])

    def test_required_package_files_are_not_gitignored(self):
        required = [
            "skills/management-assistant/SKILL.md",
            "skills/management-assistant/references/shared-contract.md",
            "skills/management-assistant/templates/leader-profile.md",
        ]
        for relative_path in required:
            result = subprocess.run(
                ["git", "check-ignore", "-q", relative_path],
                cwd=ROOT,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, relative_path)

    def test_shippable_files_have_no_private_identity_or_bytecode(self):
        forbidden = ["Pavel Nasuta", "__pycache__", ".pyc"]
        candidates = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        findings = [path for path in candidates if any(token in path for token in forbidden)]
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
