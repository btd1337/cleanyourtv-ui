"""CleanYourTV UI's config.json: every key the app reads is documented, and the example uses only those.

One release APK serves every TV, so config.json is the only way a TV's settings reach it from a computer. A key that
TvConfig.java reads but launcher-ui/README.md does not list is one nobody can find; a key in config.example.json that
TvConfig does not read is silently ignored on the TV. This reads the keys straight from TvConfig.apply's source.

Run from the repository root: python3 -m unittest discover -s tests -p test_ui_config_keys.py -v
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "launcher-ui"
TV_CONFIG = UI / "app/src/io/cleanyourtv/ui/TvConfig.java"


def keys_read():
    """The top-level keys TvConfig.apply reads from config.json (calls on the parsed object `o`)."""
    source = TV_CONFIG.read_text(encoding="utf-8")
    body = source[source.index("static boolean apply("):source.index("static boolean validTmdbKey(")]
    return set(re.findall(r'\bo\.(?:has|opt\w*|get\w*)\("([a-z_]+)"', body))


def keys_documented():
    """The keys in the first column of the README's config.json table."""
    text = (UI / "README.md").read_text(encoding="utf-8")
    section = text[text.index("## config.json"):]
    section = section[:section.index("\n## ", 1)]
    return set(re.findall(r"^\| `([a-z_]+)` \|", section, re.M))


class UiConfigKeys(unittest.TestCase):
    def test_every_key_read_is_documented(self):
        missing = sorted(keys_read() - keys_documented())
        self.assertEqual(missing, [], "read by TvConfig.java but not in launcher-ui/README.md: " + ", ".join(missing))

    def test_every_key_documented_is_read(self):
        extra = sorted(keys_documented() - keys_read())
        self.assertEqual(extra, [], "in launcher-ui/README.md but never read by TvConfig.java: " + ", ".join(extra))

    def test_the_example_uses_only_keys_the_app_reads(self):
        example = json.loads((UI / "config.example.json").read_text(encoding="utf-8"))
        unknown = sorted(set(example) - keys_read())
        self.assertEqual(unknown, [], "config.example.json keys the app ignores: " + ", ".join(unknown))

    def test_the_readers_are_found(self):
        # A refactor that moves the parsing away from `o.` would empty the set and pass the checks above.
        self.assertTrue({"tmdb_key", "shelf", "dock_apps", "buttons", "app_keys", "remote"} <= keys_read())


if __name__ == "__main__":
    unittest.main()
