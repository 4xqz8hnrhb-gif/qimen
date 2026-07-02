#!/usr/bin/env python3
"""
奇门遁甲 时家排盘 (阳遁+阴遁完整版)
用法: python qimen_pai_pan.py "2026-07-02 12:00"

输出: 完整时家奇门盘面 (地盘/天盘/人盘/神盘四层叠加)
      标记日干宫(你)和时干宫(事), 以及日时五行生克关系

依赖: 纯 Python stdlib, 无外部依赖
"""

import sys
from datetime import datetime

# ============================================================
# 基础数据
# ============================================================

LIUSHIIAZI = [
    "甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
    "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
    "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
    "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
    "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
    "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥",
]

TZ_INDEX = {"子":1,"丑":2,"寅":3,"卯":4,"辰":5,"巳":6,"午":7,"未":8,"申":9,"酉":10,"戌":11,"亥":12}
XING_LIST = ["天蓬","天芮","天冲","天辅","天禽","天心","天柱","天任","天英"]
XING_GONG = {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7, 9:8}
MEN_LIST = ["休门","死门","伤门","杜门","中门","开门","惊门","生门","景门"]
MEN_GONG = {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7, 9:8}
LIUJIA_DUN = {"甲子":"戊","甲戌":"己","甲申":"庚","甲午":"辛","甲辰":"壬","甲寅":"癸"}
GONG_NAME = {1:"坎一",2:"坤二",3:"震三",4:"巽四",5:"中五",6:"乾六",7:"兑七",8:"艮八",9:"离九"}
WUXING = {1:"水",2:"土",3:"木",4:"木",5:"土",6:"金",7:"金",8:"土",9:"火"}

# 节气三元用局表 (阳遁: 冬至→夏至, 含冬至不含夏至)
JIEQI_YANG = {
    (1, (5,19)): ("小寒", [2,8,5]),
    (1, (20,31)): ("大寒", [3,9,6]),
    (2, (1,3)): ("大寒", [3,9,6]),
    (2, (4,18)): ("立春", [8,5,2]),
    (2, (19,28)): ("雨水", [9,6,3]),
    (3, (1,4)): ("雨水", [9,6,3]),
    (3, (5,20)): ("惊蛰", [1,7,4]),
    (3, (21,31)): ("春分", [3,9,6]),
    (4, (1,4)): ("春分", [3,9,6]),
    (4, (5,19)): ("清明", [4,1,7]),
    (4, (20,30)): ("谷雨", [5,2,8]),
    (5, (1,3)): ("谷雨", [5,2,8]),
    (5, (5,20)): ("立夏", [4,1,7]),
    (5, (21,31)): ("小满", [5,2,8]),
    (6, (1,4)): ("小满", [5,2,8]),
    (6, (5,20)): ("芒种", [6,3,9]),
    (12, (22,31)): ("冬至", [1,7,4]),
}

# 节气三元用局表 (阴遁: 夏至→冬至, 含夏至不含冬至)
JIEQI_YIN = {
    (6, (21,30)): ("夏至", [9,3,6]),
    (7, (1,6)): ("夏至", [9,3,6]),
    (7, (7,22)): ("小暑", [8,2,5]),
    (7, (23,31)): ("大暑", [7,1,4]),
    (8, (1,5)): ("大暑", [7,1,4]),
    (8, (6,22)): ("立秋", [2,5,8]),
    (8, (23,31)): ("处暑", [1,4,7]),
    (9, (1,6)): ("处暑", [1,4,7]),
    (9, (7,22)): ("白露", [9,3,6]),
    (9, (23,30)): ("秋分", [7,1,4]),
    (10, (1,7)): ("秋分", [7,1,4]),
    (10, (8,22)): ("寒露", [6,9,3]),
    (10, (23,31)): ("霜降", [5,8,2]),
    (11, (1,6)): ("霜降", [5,8,2]),
    (11, (7,21)): ("立冬", [6,9,3]),
    (11, (22,30)): ("小雪", [5,8,2]),
    (12, (1,7)): ("小雪", [5,8,2]),
    (12, (7,21)): ("大雪", [4,7,1]),
}

FUTOU_RULE = {
    "子":"上元","午":"上元","卯":"上元","酉":"上元",
    "寅":"中元","申":"中元","巳":"中元","亥":"中元",
    "辰":"下元","戌":"下元","丑":"下元","未":"下元",
}

# ============================================================
# 四柱推算 (简化, 1900-2100)
# ============================================================

TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

def _ganzhi_year(year):
    base = 4
    idx = (year - base) % 60
    return TIANGAN[idx % 10] + DIZHI[idx % 12]

def _ganzhi_month(year, month):
    nian_gan = _ganzhi_year(year)[0]
    yue_gan_start = {"甲":"丙","己":"丙", "乙":"戊","庚":"戊",
                     "丙":"庚","辛":"庚", "丁":"壬","壬":"壬", "戊":"甲","癸":"甲"}
    start = TIANGAN.index(yue_gan_start[nian_gan])
    gan = TIANGAN[(start + month - 1) % 10]
    zhi = DIZHI[(month + 1) % 12]
    return gan + zhi

def _days_in_year(y):
    return 366 if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0) else 365

def _days_before_month(y, m):
    days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    d = days[m-1]
    if m > 2 and (_days_in_year(y) == 366):
        d += 1
    return d

def _ganzhi_day(year, month, day):
    total = 0
    for y in range(1900, year):
        total += _days_in_year(y)
    total += _days_before_month(year, month) + day - 1
    base = 10
    idx = (base + total) % 60
    return LIUSHIIAZI[idx]

def _ganzhi_hour(day_gan, hour):
    shichen = (hour + 1) // 2
    if shichen == 0: shichen = 12
    zhi = DIZHI[shichen - 1]
    start_map = {"甲":"甲","己":"甲", "乙":"丙","庚":"丙",
                 "丙":"戊","辛":"戊", "丁":"庚","壬":"庚", "戊":"壬","癸":"壬"}
    gan_start = TIANGAN.index(start_map[day_gan])
    gan = TIANGAN[(gan_start + shichen - 1) % 10]
    return gan + zhi

# ============================================================
# 奇门排盘核心
# ============================================================

def find_xunshou(shigan_zhu):
    idx = LIUSHIIAZI.index(shigan_zhu)
    while not LIUSHIIAZI[idx].startswith("甲"):
        idx -= 1
    return LIUSHIIAZI[idx]

def get_jushu(year, month, day):
    """根据公历日期确定用局, 返回 (局数, 节气, 元, 符头, 遁式)"""
    ri_zhu = _ganzhi_day(year, month, day)
    idx = LIUSHIIAZI.index(ri_zhu)
    futou = ri_zhu
    # 找符头(往前最近的甲日或己日)
    while True:
        gz = LIUSHIIAZI[idx]
        if gz[0] in ("甲","己"):
            futou = gz
            break
        idx -= 1
    dz = futou[1]
    yuan = FUTOU_RULE[dz]

    # 先查阳遁
    for (m, (d1, d2)), (qi, ju) in JIEQI_YANG.items():
        if month == m and d1 <= day <= d2:
            if yuan == "上元": n = ju[0]
            elif yuan == "中元": n = ju[1]
            else: n = ju[2]
            return n, qi, yuan, futou, "阳遁"

    # 再查阴遁
    for (m, (d1, d2)), (qi, ju) in JIEQI_YIN.items():
        if month == m and d1 <= day <= d2:
            if yuan == "上元": n = ju[0]
            elif yuan == "中元": n = ju[1]
            else: n = ju[2]
            return n, qi, yuan, futou, "阴遁"

    return None, None, None, None, None

def dipan_yang(jushu):
    """阳遁地盘: 顺布六仪, 逆布三奇"""
    jishu = jushu % 9 or 9
    dp = {}
    pos = jishu
    for gan in ["戊","己","庚","辛","壬","癸"]:
        dp[pos] = gan
        pos = (pos % 9) + 1
    remaining = sorted([i for i in range(1,10) if i not in dp], reverse=True)
    for i, gan in enumerate(["丁","丙","乙"]):
        dp[remaining[i]] = gan
    return dp

def dipan_yin(jushu):
    """阴遁地盘: 逆布六仪, 顺布三奇"""
    jishu = jushu % 9 or 9
    dp = {}
    pos = jishu
    for gan in ["戊","己","庚","辛","壬","癸"]:
        dp[pos] = gan
        pos = ((pos - 2) % 9) + 1  # 逆排: 1→9→8→7...
    remaining = sorted([i for i in range(1,10) if i not in dp])
    for i, gan in enumerate(["丁","丙","乙"]):
        dp[remaining[i]] = gan
    return dp

def pai_tianpan(dp, zf_orig_gong, shigan_gong, yin_dun=False):
    """排天盘: 值符星随时干飞。阳遁顺飞, 阴遁逆飞"""
    order = list(range(1,10))
    og2xing = {g: XING_LIST[XING_GONG[g]] for g in order}

    if yin_dun:
        # 阴遁逆飞: 值符到目标宫, 其余星逆排
        offset = shigan_gong - zf_orig_gong
        if offset > 0: offset -= 9  # 逆方向
    else:
        offset = shigan_gong - zf_orig_gong
        if offset < 0: offset += 9

    tp = {}
    for g in order:
        new_g = ((g + offset - 1) % 9) + 1
        tp[new_g] = og2xing[g]
    return tp

def pai_renpan(zf_orig_gong, xunshou, shigan_zhu, yin_dun=False):
    """排人盘(八门): 值使门随时支飞。阳遁顺数, 阴遁逆数"""
    xun_dz = xunshou[1]
    shi_dz = shigan_zhu[1]
    xs_tz = TZ_INDEX[xun_dz]
    sz_tz = TZ_INDEX[shi_dz]
    current_pos = zf_orig_gong
    current_tz = xs_tz

    if yin_dun:
        # 阴遁: 逆数时支
        while current_tz != sz_tz:
            current_pos = ((current_pos - 2) % 9) + 1  # 逆排
            current_tz = (current_tz % 12) + 1  # 时辰增加, 但宫位逆走
        # 八门逆排
        men_seq = [0, 7, 2, 3, 8, 1, 6, 5, 4]  # 原始宫序
        men_names = ["休","生","伤","杜","景","死","惊","开","中"]
        offset = current_pos - zf_orig_gong
        if offset > 0: offset -= 9  # 逆
    else:
        # 阳遁: 顺数时支
        while current_tz != sz_tz:
            current_pos = (current_pos % 9) + 1
            current_tz = (current_tz % 12) + 1
        men_seq = [0, 7, 2, 3, 8, 1, 6, 5, 4]
        men_names = ["休","生","伤","杜","景","死","惊","开","中"]
        offset = current_pos - zf_orig_gong
        if offset < 0: offset += 9

    rp = {}
    for gi in range(9):
        g = gi + 1
        new_g = ((g + offset - 1) % 9) + 1
        rp[new_g] = men_names[men_seq[g-1]]
    return rp

def pai_shenpan(zf_tp_gong, yin_dun=False):
    """排神盘: 值符随天盘值符星。阳遁顺排, 阴遁逆排"""
    sp = {}
    if yin_dun:
        # 阴遁: 值符→螣蛇→太阴→六合→白虎→玄武→九地→九天 → 逆排(1→9→8...)
        ba_shen = ["值符","腾蛇","太阴","六合","白虎","玄武","九地","九天"]
        pos = zf_tp_gong
        for shen in ba_shen:
            sp[pos] = shen
            pos = ((pos - 2) % 9) + 1  # 逆排
    else:
        ba_shen = ["值符","腾蛇","太阴","六合","白虎","玄武","九地","九天"]
        pos = zf_tp_gong
        for shen in ba_shen:
            sp[pos] = shen
            pos = (pos % 9) + 1
    return sp

# ============================================================
# 主函数
# ============================================================

def qimen_pai_pan_dict(dt_str):
    """返回奇门盘数据的 dict, 供编程调用"""
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    year, month, day, hour = dt.year, dt.month, dt.day, dt.hour

    nian = _ganzhi_year(year)
    yue = _ganzhi_month(year, month)
    ri = _ganzhi_day(year, month, day)
    shi = _ganzhi_hour(ri[0], hour)

    jushu, qi, yuan, futou, dun_type = get_jushu(year, month, day)
    if jushu is None:
        return {"error": "无法确定用局", "datetime": dt_str}

    yin_dun = (dun_type == "阴遁")
    dp = dipan_yin(jushu) if yin_dun else dipan_yang(jushu)

    xunshou = find_xunshou(shi)
    dun_gan = LIUJIA_DUN[xunshou]
    zf_orig_gong = None
    for g, gan in dp.items():
        if gan == dun_gan:
            zf_orig_gong = g
            break
    zf_xing_idx = XING_GONG[zf_orig_gong]

    shigan_raw = shi[0]
    shigan_actual = dun_gan if shigan_raw == "甲" else shigan_raw
    shigan_gong = None
    for g, gan in dp.items():
        if gan == shigan_actual:
            shigan_gong = g
            break

    rigan_gong = None
    for g, gan in dp.items():
        if gan == ri[0]:
            rigan_gong = g
            break

    tp = pai_tianpan(dp, zf_orig_gong, shigan_gong, yin_dun)
    rp = pai_renpan(zf_orig_gong, xunshou, shi, yin_dun)

    zf_tp_gong = None
    for g, x_name in tp.items():
        if x_name == XING_LIST[zf_xing_idx]:
            zf_tp_gong = g
            break
    sp = pai_shenpan(zf_tp_gong, yin_dun)

    ke = {"水":"火","火":"金","金":"木","木":"土","土":"水"}
    sheng = {"水":"木","木":"火","火":"土","土":"金","金":"水"}
    rw = WUXING[rigan_gong]
    sw = WUXING[shigan_gong]

    if rigan_gong == shigan_gong:
        rel = f"同宫({rw})"
    elif ke[rw] == sw:
        rel = f"你克事({rw}克{sw})"
    elif ke[sw] == rw:
        rel = f"事克你({sw}克{rw})"
    elif sheng[rw] == sw:
        rel = f"你生事({rw}→{sw})"
    elif sheng[sw] == rw:
        rel = f"事生你({sw}→{rw})"
    else:
        rel = "比和"

    grid = {}
    for g in range(1, 10):
        grid[GONG_NAME[g]] = {
            "dipan": dp.get(g, '-'),
            "tianpan": tp.get(g, '-'),
            "renpan": rp.get(g, '-'),
            "shenpan": sp.get(g, '-'),
            "wuxing": WUXING[g],
        }

    jimen = []
    for g in range(1, 10):
        m = rp.get(g, '')
        if m in ['开门', '休门', '生门']:
            jimen.append({"gate": m, "palace": GONG_NAME[g]})

    return {
        "datetime": dt_str,
        "pillars": {"year": nian, "month": yue, "day": ri, "hour": shi},
        "dun_type": dun_type,
        "jushu": jushu,
        "jieqi": qi,
        "yuan": yuan,
        "futou": futou,
        "xunshou": xunshou,
        "dun_gan": dun_gan,
        "zhifu": XING_LIST[zf_xing_idx],
        "zhishi": MEN_LIST[MEN_GONG[zf_orig_gong]],
        "rigan_gong": GONG_NAME[rigan_gong],
        "shigan_gong": GONG_NAME[shigan_gong],
        "rigan_stem": ri[0],
        "shigan_stem": shi[0] if shigan_raw != '甲' else f'甲(遁{dun_gan})',
        "day_hour_relation": rel,
        "grid": grid,
        "jimen": jimen,
    }


def qimen_pai_pan(dt_str):
    """输入 'YYYY-MM-DD HH:MM', 输出完整奇门盘"""
    import json as _json
    result = qimen_pai_pan_dict(dt_str)
    if "error" in result:
        print(f"错误: {result['error']}")
        return

    dt = result["datetime"]
    nian, yue, ri, shi = result["pillars"]["year"], result["pillars"]["month"], result["pillars"]["day"], result["pillars"]["hour"]
    qi, yuan, dun_type, jushu = result["jieqi"], result["yuan"], result["dun_type"], result["jushu"]
    xunshou, dun_gan = result["xunshou"], result["dun_gan"]
    zf, zs = result["zhifu"], result["zhishi"]
    rigan_gong = result["rigan_gong"]
    shigan_gong = result["shigan_gong"]
    rel = result["day_hour_relation"]
    rigan_stem = result["rigan_stem"]
    shigan_stem = result["shigan_stem"]

    rn = int(rigan_gong[1]) if len(rigan_gong) > 1 and rigan_gong[1].isdigit() else list(GONG_NAME.keys())[list(GONG_NAME.values()).index(rigan_gong)]
    sn = int(shigan_gong[1]) if len(shigan_gong) > 1 and shigan_gong[1].isdigit() else list(GONG_NAME.keys())[list(GONG_NAME.values()).index(shigan_gong)]

    dp = {list(GONG_NAME.keys())[list(GONG_NAME.values()).index(k)]: v["dipan"] for k, v in result["grid"].items()}
    tp = {list(GONG_NAME.keys())[list(GONG_NAME.values()).index(k)]: v["tianpan"] for k, v in result["grid"].items()}
    rp = {list(GONG_NAME.keys())[list(GONG_NAME.values()).index(k)]: v["renpan"] for k, v in result["grid"].items()}
    sp = {list(GONG_NAME.keys())[list(GONG_NAME.values()).index(k)]: v["shenpan"] for k, v in result["grid"].items()}

    print(f"═══════════════════════════════════════")
    print(f"  奇门遁甲时家排盘")
    print(f"═══════════════════════════════════════")
    print(f"  公历: {dt}")
    print(f"  四柱: {nian}年 {yue}月 {ri}日 {shi}时")
    print(f"  节气: {qi} ({yuan}) → {dun_type}{jushu}局")
    print(f"  旬首: {xunshou} (遁{dun_gan})")
    print(f"  值符: {zf}  值使: {zs}")
    print()
    print(f"  日干{rigan_stem}落{rigan_gong}  时干{shigan_stem}落{shigan_gong}  日时:{rel}")

    print()
    print(f"  {'宫位':<12} {'地盘':<6} {'天盘':<8} {'八门':<6} {'八神':<6}")
    print(f"  {'─'*48}")
    for g in [rn, sn]:
        d = dp.get(g,'-')
        t = tp.get(g,'-')
        r = rp.get(g,'-')
        s = sp.get(g,'-')
        tag = "★你" if g == rn else "☆事"
        print(f"  {GONG_NAME[g]+tag:<12} {d:<6} {t:<8} {r:<6} {s:<6}")

    print()
    print(f"  吉门方位:")
    for jm in result["jimen"]:
        print(f"    {jm['gate']} → {jm['palace']}")

    print()
    print(f"  ┌──────────┬──────────┬──────────┐")
    for row in [(4,9,2),(3,5,7),(8,1,6)]:
        cells = []
        for g in row:
            d = dp.get(g,'-')
            t = tp.get(g,'-')
            r = rp.get(g,'-')[:1] if rp.get(g,'-') else '-'
            s = sp.get(g,'-')[:1] if sp.get(g,'-') else '-'
            cells.append(f"{GONG_NAME[g][:2]} {d}{t[:2]}{r}{s}")
        print(f"  │ {cells[0]:<8} │ {cells[1]:<8} │ {cells[2]:<8} │")
        if row != (8,1,6):
            print(f"  ├──────────┼──────────┼──────────┤")
    print(f"  └──────────┴──────────┴──────────┘")
    print(f"  (宫位 地盘干+天盘星首字+门首字+神首字)")


if __name__ == "__main__":
    import json
    args = sys.argv[1:]

    if not args:
        print("qimen — 奇门遁甲时家排盘 (阳遁+阴遁)")
        print("用法: python qimen.py '2026-07-02 12:00'")
        print("      python qimen.py '2026-07-02 12:00' --json")
        print("      python qimen.py --batch '2026-07-02 12:00' '2026-07-03 18:00'")
        print("支持阳遁(冬至→夏至)和阴遁(夏至→冬至)")
        sys.exit(0)

    if args[0] == "--batch":
        dates = [a for a in args[1:] if not a.startswith("--")]
        json_out = "--json" in args
        results = []
        for dt_str in dates:
            r = qimen_pai_pan_dict(dt_str)
            results.append(r)
        if json_out:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for r in results:
                if "error" in r:
                    print(f"⚠ {r.get('datetime','?')}: {r['error']}")
                else:
                    rel = r['day_hour_relation']
                    eng = {"你克事":"favor","事克你":"resist","事生你":"nourish","你生事":"drain","同宫":"equal","比和":"equal"}
                    e = eng.get(rel.split('(')[0] if '(' in rel else rel, '?')
                    print(f"{r['datetime']} | {r['dun_type']}{r['jushu']}局 | {r['jieqi']}({r['yuan']}) | 日{r['rigan_stem']}落{r['rigan_gong']} 时{r['shigan_stem']}落{r['shigan_gong']} | {rel} ({e})")
    elif args[-1] == "--json" or "--json" in args:
        dt_str = next((a for a in args if not a.startswith("--")), None)
        if dt_str:
            print(json.dumps(qimen_pai_pan_dict(dt_str), ensure_ascii=False, indent=2))
    else:
        qimen_pai_pan(args[0])
