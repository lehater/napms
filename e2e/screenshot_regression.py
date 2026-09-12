from io import BytesIO

from PIL import Image
from playwright.sync_api import Page


APPLICATION_SCREEN_BASELINES: dict[str, str] = {
    "definitions-list": "8c06900ef006ac0088068001e0012c034ccb35243526900931360b8901814060",
    "definition-interactions": "8800a003c3035400908002042003a12e800e1b0d9b2c93029b0a912003810181",
    "deployment-connectivity": "9ac0852b812b8095999889ae802ec0008027244ad6609c729c72be7201890011",
}
MAX_HAMMING_DISTANCE = 6


def application_main_fingerprint(page: Page) -> str:
    png = page.locator("main").screenshot(animations="disabled", caret="hide")
    with Image.open(BytesIO(png)) as image:
        grayscale = image.convert("L").resize((17, 16), Image.Resampling.LANCZOS)
        pixels = list(grayscale.getdata())

    bits = 0
    for y in range(16):
        row = pixels[y * 17 : (y + 1) * 17]
        for x in range(16):
            bits = (bits << 1) | int(row[x] > row[x + 1])
    return f"{bits:064x}"


def _assert_screen_fingerprints(
    *,
    family: str,
    expected: dict[str, str],
    actual: dict[str, str],
) -> None:
    missing = [name for name, value in expected.items() if not value]
    if missing:
        generated = ", ".join(f"{name}={actual[name]}" for name in expected)
        raise AssertionError(f"Set {family} screenshot baselines: {generated}")

    regressions: list[str] = []
    for name, baseline in expected.items():
        observed = actual[name]
        distance = (int(baseline, 16) ^ int(observed, 16)).bit_count()
        if distance > MAX_HAMMING_DISTANCE:
            regressions.append(
                f"{name}: distance={distance}, expected={baseline}, observed={observed}"
            )

    if regressions:
        raise AssertionError(f"{family} screenshot regressions: " + " | ".join(regressions))


def assert_application_screen_fingerprints(actual: dict[str, str]) -> None:
    _assert_screen_fingerprints(
        family="Application",
        expected=APPLICATION_SCREEN_BASELINES,
        actual=actual,
    )
