# Qimen Dunjia Paipan (奇门遁甲排盘)

Pure Python Qi Men Dun Jia (时家奇门) chart calculator. Zero dependencies — works on any Python 3.8+.

阴阳遁全支持：冬至→夏至阳遁，夏至→冬至阴遁，全年可用。

## Quick Start

```bash
python qimen.py "2026-07-02 19:00"
```

Outputs a complete chart with 四柱, 地盘, 天盘(九星), 人盘(八门), 神盘(八神), and day/hour stem relationship.

## Features

- **全年覆盖**: 阳遁 + 阴遁, all 24 solar terms
- **零依赖**: Pure Python stdlib, no pip install needed
- **完整输出**: 4 pillars, earth/ heaven/ human/ spirit plates, 9-palace grid
- **日时生克**: Automatic day-stem vs hour-stem relationship analysis
- **吉门方位**: Open/Rest/Life gate locations

## Usage

```bash
# Single chart
python qimen.py "2026-07-03 18:00"

# JSON output (for programmatic use)
python qimen.py "2026-07-03 18:00" --json

# Batch mode
python qimen.py --batch "2026-07-02 12:00" "2026-07-02 19:00" "2026-07-03 13:00"
```

## Example Output

```
═══════════════════════════════════════
  奇门遁甲时家排盘
═══════════════════════════════════════
  公历: 2026-07-02 19:00
  四柱: 丙午年 丙申月 丁丑日 己酉时
  节气: 夏至 (下元) → 阴遁6局
  旬首: 甲辰 (遁壬)
  值符: 天芮  值使: 死门

  日干丁落兑七  时干己落中五  日时:事生你(土→金)

  ┌──────────┬──────────┬──────────┐
  │ 巽四 庚天蓬景腾 │ 离九 乙天心中玄 │ 坤二 壬天任惊六 │
  ├──────────┼──────────┼──────────┤
  │ 震三 辛天英死太 │ 中五 己天芮休值 │ 兑七 丁天辅伤九 │
  ├──────────┼──────────┼──────────┤
  │ 艮八 丙天禽杜九 │ 坎一 癸天柱生白 │ 乾六 戊天冲开- │
  └──────────┴──────────┴──────────┘
```

## How It Works

1. **定局**: 节气 → 阴阳遁 + 局数 (上/中/下元)
2. **地盘**: 阳遁顺布六仪逆布三奇, 阴遁逆布六仪顺布三奇
3. **旬首→值符值使**: 时柱旬首 → 六甲遁干 → 原始星门
4. **天盘**: 值符星随时干飞 (阳顺阴逆)
5. **人盘**: 值使门随时支飞 (阳顺阴逆)
6. **神盘**: 八神随值符 (阳顺阴逆)

## Interpretation (断事)

The key signal is the **日时生克** (day-stem vs hour-stem relationship):

| Relationship | Meaning |
|:---|:---|
| 同宫 | Same palace — depends on palace config |
| 你克事 | You overcome the matter — favorable |
| 事克你 | Matter overcomes you — resistance |
| 你生事 | You generate matter — draining |
| 事生你 | Matter generates you — nourishing |

For sports predictions: day-stem = home/favorite, hour-stem = away/underdog.

## Limitations

- Simplified Ganzhi calendar (1900-2100), not precise astronomical ephemeris
- Solar term dates are approximate (±1 day from actual 交节)
- 中五寄坤二 handling needs further verification
- Has not been validated against professional Qimen software

## License

MIT
