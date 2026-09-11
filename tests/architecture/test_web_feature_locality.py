from pathlib import Path


ROOT = Path(__file__).parents[2]
WEB = ROOT / "web" / "src"
ROOT_API = WEB / "api.ts"
SHARED_API = WEB / "lib" / "api.ts"
REQUIREMENTS_API = WEB / "features" / "requirements" / "api.ts"
DECISIONS_API = WEB / "features" / "decisions" / "api.ts"
RULES_API = WEB / "features" / "rules" / "api.ts"


def _assert_feature_local(feature_api: Path, implementations: tuple[str, ...]) -> None:
    root_source = ROOT_API.read_text(encoding="utf-8")
    feature_source = feature_api.read_text(encoding="utf-8")
    assert feature_api.is_file()
    for implementation in implementations:
        assert implementation not in root_source
        assert implementation in feature_source


def test_requirements_api_implementation_is_feature_local():
    assert SHARED_API.is_file()
    _assert_feature_local(
        REQUIREMENTS_API,
        (
            "export type ConnectivityRequirementDto =",
            "export type RequirementApplicability =",
            "export type RequirementPolicyAlignmentStatus =",
            "export async function declareConnectivityRequirement(",
            "export async function listConnectivityRequirements(",
            "export async function getConnectivityRequirement(",
            "export async function listConnectivityRequirementAlignment(",
            "export async function getConnectivityRequirementAlignment(",
        ),
    )


def test_decisions_api_implementation_is_feature_local():
    _assert_feature_local(
        DECISIONS_API,
        (
            "export type ConnectivityDecisionDto =",
            "export type ConnectivityDecisionOutcome =",
            "export async function listConnectivityDecisionScopes(",
            "export async function listConnectivityDecisionInteractions(",
            "export async function listConnectivityDecisions(",
            "export async function getConnectivityDecision(",
            "export async function recordConnectivityDecision(",
        ),
    )


def test_rules_api_implementation_is_feature_local():
    _assert_feature_local(
        RULES_API,
        (
            "export type RuleDetailResponse =",
            "export type RuleListPage =",
            "export async function listAccessRules(",
            "export async function getAccessRule(",
            "export async function setAccessRuleOperationalState(",
            "export async function setAccessRuleEffectiveWindow(",
        ),
    )


def test_root_api_only_compatibility_exports_localized_slices():
    root_source = ROOT_API.read_text(encoding="utf-8")
    assert 'from "@/features/requirements/api"' in root_source
    assert 'from "@/features/decisions/api"' in root_source
    assert 'from "@/features/rules/api"' in root_source
    assert 'from "@/lib/api"' in root_source
    assert '"/api/v1/connectivity-requirements' not in root_source
    assert '"/api/v1/connectivity-decisions' not in root_source
    assert '"/api/v1/access-rules' not in root_source
