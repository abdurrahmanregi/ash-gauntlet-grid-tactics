"""Launch Ash-Gauntlet Tactics."""

from __future__ import annotations

import traceback

from ashgauntlet.app import run
from ashgauntlet.paths import user_root


def main() -> None:
    try:
        run()
    except Exception:
        log = user_root() / "crash.log"
        log.write_text(traceback.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
