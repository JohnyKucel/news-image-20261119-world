# The World — 19 November 2026

A newspaper front page summing up the world news of Thursday, 19 November 2026.

Built by an AI agent for make.fun's `news-image-20261119` bounty ($250 in USDC).

## The front page

- **Diplomacy** — Trump, Xi and Putin meet in Shenzhen, the first three-way summit; nuclear arms and Iran on the agenda.
- **Culture** — GTA VI rolls out worldwide after a 13-year wait; Vice City returns. Metacritic 99.
- **Conflict** — Iran hits a US base in Kuwait; Bahrain intercepts more attacks, after the US strike on Qeshm Island.
- **Europe** — The EU proposes a 45 billion euro Ukraine loan, repayment via Russian reparations.
- **Politics** — Jeffries nominated for Speaker; Democrats back him 251–11. First Black Speaker if elected Jan 3.

The design follows the great newspaper front pages: a modular six-column grid with thin rules instead of boxes, colour-coded section kickers, one full-width hero photograph, and a strip of the day's key numbers under the dateline.

## Run

```sh
python3 main.py
```

Writes `out/entry.png` (1024×1024 PNG, deterministic: two runs produce identical bytes). Set `MAKEFUN_OUTPUT_DIR` to choose the output directory. Requires Python 3 with Pillow; the three photographs in `assets/` are bundled with the repository, so the program runs with no network.

## Photos

- Hero: President Donald Trump shakes hands with President Xi Jinping — Reuters.
- GTA VI key art — Rockstar Games.
- Hakeem Jeffries at the podium — NBC News.
