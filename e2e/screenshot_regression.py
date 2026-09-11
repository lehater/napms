from io import BytesIO

from PIL import Image
from playwright.sync_api import Page


APPLICATION_SCREEN_BASELINES: dict[str, str] = {
    "definitions-list": "2000900e900e7006a80180021921c6c2c2432db63db6cc49cc91810381034000",
    "definition-interactions": "90008400c203c2014480708082064601802c932c33089106330b330781039102",
    "deployment-connectivity": "90008521c28b929199994911802c802ec09b9641946a9c2a1c2a1c2281038102",
}
RESOURCE_SCREEN_BASELINES: dict[str, str] = {
    "resource-catalogue": "c816c416b00068062b2bb091a968a96ed01e900ed15e989a911a811ac88c4004",
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


def assert_resource_screen_fingerprints(actual: dict[str, str]) -> None:
    _assert_screen_fingerprints(
        family="Resource",
        expected=RESOURCE_SCREEN_BASELINES,
        actual=actual,
    )
