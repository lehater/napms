from pathlib import Path


ROOT = Path(__file__).parents[2]
WEB = ROOT / "web" / "src"
ROOT_API = WEB / "api.ts"
SHARED_API = WEB / "lib" / "api.ts"
REQUIREMENTS_API = WEB / "features" / "requirements" / "api.ts"


def test_requirements_api_implementation_is_feature_local():
    root_source = ROOT_API.read_text(encoding="utf-8")
    feature_source = REQUIREMENTS_API.read_text(encoding="utf-8")

    assert SHARED_API.is_file()
    assert REQUIREMENTS_API.is_file()

    for implementation in (
        "export type ConnectivityRequirementDto =",
        "export type RequirementApplicability =",
        "export type RequirementPolicyAlignmentStatus =",
        "export async function declareConnectivityRequirement(",
        "export async function listConnectivityRequirements(",
        "export async function getConnectivityRequirement(",
        "export async function listConnectivityRequirementAlignment(",
        "export async function getConnectivityRequirementAlignment(",
    ):
        assert implementation not in root_source
        assert implementation in feature_source


def test_root_api_only_compatibility_exports_requirements_slice():
    root_source = ROOT_API.read_text(encoding="utf-8")
    assert 'from "@/features/requirements/api"' in root_source
    assert 'from "@/lib/api"' in root_source
    assert '"/api/v1/connectivity-requirements' not in root_source
