from pathlib import Path


ROOT = Path(__file__).parents[3]
WEB = ROOT / "web" / "src"
ROOT_API = WEB / "api.ts"
SHARED_API = WEB / "lib" / "api.ts"
REQUIREMENTS_API = WEB / "features" / "requirements" / "api" / "index.ts"
DECISIONS_API = WEB / "features" / "decisions" / "api" / "index.ts"
RULES_API = WEB / "features" / "rules" / "api" / "index.ts"
POLICY_API = WEB / "features" / "policy" / "api" / "index.ts"
CONNECTIVITY_API = WEB / "features" / "connectivity" / "api" / "index.ts"


def _assert_feature_local(feature_api: Path, implementations: tuple[str, ...]) -> None:
    feature_source = feature_api.read_text(encoding="utf-8")
    assert feature_api.is_file()
    for implementation in implementations:
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


def test_policy_api_implementation_is_feature_local():
    _assert_feature_local(
        POLICY_API,
        (
            "export type EffectivePolicyResponse =",
            "export type NormalizedPolicyResponse =",
            "export async function listPolicyViewScopes(",
            "export async function getEffectiveDesiredPolicy(",
            "export async function getNormalizedPolicy(",
        ),
    )


def test_scoped_connectivity_api_implementation_is_feature_local():
    _assert_feature_local(
        CONNECTIVITY_API,
        (
            "export type ScopedConnectivityInventoryPage =",
            "export type ScopedConnectivityRelationship =",
            "export async function listScopedConnectivityScopes(",
            "export async function getScopedConnectivityInventory(",
        ),
    )


def test_root_api_compatibility_facade_is_absent():
    assert not ROOT_API.exists()
