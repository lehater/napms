from io import BytesIO

from PIL import Image
from playwright.sync_api import Page


APPLICATION_SCREEN_BASELINES: dict[str, str] = {
    "definitions-list": "0001800e902e100ea00180061921c682c2422db42db4cc4b0493810301030000",
    "definition-interactions": "90008c008002c1028480b080820e4601802c932c33099107130b130781030001",
    "deployment-connectivity": "90008530c2ca928199914b11806c802c489b9241946a942a1c261c6281030001",
}
RESOURCE_SCREEN_BASELINES: dict[str, str] = {
    "resource-catalogue": "",
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


def assert_application_screen_fingerprints(actual: dict[str, str]) -> None:
    missing = [name for name, value in APPLICATION_SCREEN_BASELINES.items() if not value]
    if missing:
        generated = ", ".join(f"{name}={actual[name]}" for name in APPLICATION_SCREEN_BASELINES)
        raise AssertionError(f"Set Application screenshot baselines: {generated}")

    for name, expected in APPLICATION_SCREEN_BASELINES.items():
        observed = actual[name]
        distance = (int(expected, 16) ^ int(observed, 16)).bit_count()
        assert distance <= MAX_HAMMING_DISTANCE, (
            f"Application screenshot regression for {name}: "
            f"distance={distance}, expected={expected}, observed={observed}"
        )


def assert_resource_screen_fingerprints(actual: dict[str, str]) -> None:
    missing = [name for name, value in RESOURCE_SCREEN_BASELINES.items() if not value]
    if missing:
        generated = ", ".join(f"{name}={actual[name]}" for name in RESOURCE_SCREEN_BASELINES)
        raise AssertionError(f"Set Resource screenshot baselines: {generated}")

    for name, expected in RESOURCE_SCREEN_BASELINES.items():
        observed = actual[name]
        distance = (int(expected, 16) ^ int(observed, 16)).bit_count()
        assert distance <= MAX_HAMMING_DISTANCE, (
            f"Resource screenshot regression for {name}: "
            f"distance={distance}, expected={expected}, observed={observed}"
        )
