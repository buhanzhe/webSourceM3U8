"""Keep national groups first, then administrative-code groups and plate-code cities.

Only ordering/group membership changes. Channel records and URLs are preserved.
Within a city, the existing order is stable. Counties use their parent city's code.
Plate reference: https://www.icauto.com.cn/baike/67/672051.html
https://config.net.cn/tools/ChePai.html
"""
import argparse
from collections import Counter
from pathlib import Path

TOP = ['央视频道', '卫视频道', '教育频道', '少儿频道', '4K频道']
PROVINCES = ('北京 天津 河北 山西 内蒙古 辽宁 吉林 黑龙江 上海 江苏 浙江 安徽 福建 江西 '
             '山东 河南 湖北 湖南 广东 深圳 广西 海南 重庆 四川 贵州 云南 西藏 陕西 '
             '甘肃 青海 宁夏 新疆').split()

# Letters are the city plate code, not administrative codes or phone area codes.
# Multiple prefixes on one letter belong to the same city and retain their order.
CITY_CODES = {
    '河北': 'G:张家口 J:沧州',
    '山西': 'A:太原 B:大同 C:阳泉 D:长治 E:晋城 F:朔州 H:忻州 J:吕梁 K:晋中 L:临汾 M:运城',
    '内蒙古': 'A:呼和浩特 B:包头 C:乌海 D:赤峰 E:呼伦贝尔 F:兴安盟 G:通辽 H:锡林郭勒 J:乌兰察布 K:鄂尔多斯 L:巴彦淖尔 M:阿拉善',
    '辽宁': 'B:金普',
    '吉林': 'B:吉林市 C:四平 H:延边',
    '黑龙江': 'A:哈尔滨 B:齐齐哈尔 E:大庆 M:绥化',
    '江苏': 'A:南京,江宁 B:无锡 E:苏州,张家港 F:南通 G:连云港 J:盐城 K:扬州 M:泰州 N:宿迁',
    '浙江': 'A:杭州,西湖明珠 B:宁波,奉化 D:绍兴',
    '安徽': 'A:合肥 B:芜湖 F:淮北 G:铜陵 J:黄山 K:阜阳 L:宿州 S:亳州',
    '福建': 'A:福州 C:泉州,晋江,石狮 D:厦门 E:漳州 F:龙岩 G:三明 H:南平 J:宁德 K:平潭',
    '江西': 'A:南昌 C:宜春',
    '山东': 'B:青岛,崂山 D:枣庄 E:东营,广饶 G:潍坊 H:济宁 J:泰安 K:威海 P:聊城 Q:沂水',
    '河南': 'A:郑州 B:开封 C:洛阳 D:平顶山 E:安阳 F:鹤壁 G:新乡 H:焦作 J:濮阳 K:许昌 L:漯河 M:三门峡 N:商丘 P:周口 Q:驻马店 R:南阳 S:信阳 U:济源',
    '湖北': 'B:黄石,直播黄石 C:十堰 D:荆州 E:宜昌 F:襄阳 H:荆门 K:孝感 L:咸宁 Q:恩施 S:随州',
    '湖南': 'A:长沙 F:岳阳 K:娄底 L:郴州,资兴 U:湘西',
    '广东': 'A:广州 B:深圳 F:韶关 H:肇庆 J:江门,开平 K:信宜 M:五华 P:河源 R:清远 S:东莞 W:云浮',
    '广西': 'A:南宁 B:柳州 C:桂林 E:北海 G:来宾 K:玉林 P:防城港',
    '海南': 'A:海口 F:儋州',
    '四川': 'A:成都,简阳,彭州,青白江,蒲江,大邑,金堂,邛崃,郫都,双流,新都,成华,武侯,金牛,温江,锦江,青羊,高新 B:绵阳 E:泸州,泸县 F:绵竹 H:广元 J:遂宁,射洪 K:内江 M:资阳 T:雅安 V:甘孜 Y:南江',
    '贵州': 'G:安顺 J:黔南',
    '云南': 'G:红河 J:普洱 K:西双版纳 P:丽江 S:临沧',
    '西藏': 'A:拉萨 D:日喀则',
    '陕西': 'A:西安 B:铜川 D:咸阳 H:商洛 J:延安 K:榆林',
    '甘肃': 'A:兰州 D:白银 J:定西 K:陇南 L:平凉',
    '青海': 'A:西宁',
    '宁夏': 'A:银川 B:石嘴山',
    '新疆': 'J:克拉玛依 L:哈密',
}

# Regional/national broadcasters whose names do not begin with the group name.
REGIONAL = {
    '山西': ('黄河',),
    '江苏': ('优漫卡通',),
    '福建': ('东南卫视', '海峡卫视'),
    '湖南': ('金鹰', '国际频道', '先锋乒羽', '茶频道', '快乐垂钓'),
    '广东': ('大湾区', '嘉佳卡通', '南方购物', '岭南戏曲', '荔枝台', '纪录片', 'GRTN'),
    '广西': ('CETV',),
    '海南': ('三沙卫视',),
    '四川': ('康巴卫视', '每经 AI'),
    '云南': ('澜湄国际',),
}


def city_key(province, row):
    name = row.split(',', 1)[0]
    prefixes = []
    for item in CITY_CODES.get(province, '').split():
        letter, names = item.split(':', 1)
        prefixes.extend((prefix, letter) for prefix in names.split(','))
    for prefix, letter in sorted(prefixes, key=lambda pair: -len(pair[0])):
        if name.startswith(prefix):
            return letter
    if (province in ('北京', '上海', '深圳', '重庆')
            or name.startswith(province)
            or name.startswith(REGIONAL.get(province, ()))):
        return ''
    raise ValueError(f'未配置城市归属，停止排序以免误排：{province} / {name}')


def arrange(text):
    groups = {}
    current = None
    for line in text.splitlines():
        if line.endswith(',#genre#'):
            current = line.split(',', 1)[0]
            if current in groups:
                raise ValueError(f'分组重复：{current}')
            groups[current] = []
        elif line.strip():
            if current is None or ',' not in line:
                raise ValueError(f'频道格式错误：{line}')
            groups[current].append(line)
    original = Counter(row for rows in groups.values() for row in rows)
    # Correct legacy province misclassifications without changing any record.
    for source, prefix, destination in [('江苏频道', '铜川', '陕西频道'),
                                        ('贵州频道', '肇庆', '广东频道'),
                                        ('四川频道', '重庆', '重庆频道')]:
        moved = [row for row in groups.get(source, []) if row.startswith(prefix)]
        if moved:
            groups[source] = [row for row in groups[source] if not row.startswith(prefix)]
            groups.setdefault(destination, []).extend(moved)
    four_k = groups.setdefault('4K频道', [])
    for group, rows in groups.items():
        if group == '4K频道':
            continue
        moved = [row for row in rows if '4K' in row.split(',', 1)[0].upper()
                 and not row.split(',', 1)[0].upper().startswith('CCTV')]
        if moved:
            groups[group] = [row for row in rows if row not in moved]
            four_k.extend(moved)
    order = TOP + [province + '频道' for province in PROVINCES if province + '频道' in groups]
    if set(order) != set(groups):
        raise ValueError(f'未知分组：{set(groups) - set(order)}')
    for group in order[len(TOP):]:
        groups[group].sort(key=lambda row: city_key(group[:-2], row))
    assert original == Counter(row for rows in groups.values() for row in rows)
    return '\n\n'.join('\n'.join([group + ',#genre#'] + groups[group]) for group in order) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--playlist', type=Path, default=Path(__file__).resolve().parent.parent / 'webview.txt')
    parser.add_argument('--check', action='store_true', help='Only verify the configured order.')
    args = parser.parse_args()
    current = args.playlist.read_text(encoding='utf-8-sig')
    expected = arrange(current)
    if args.check:
        if current != expected:
            raise SystemExit('频道排序与约定不一致，请运行此脚本恢复。')
        print('频道分组、车牌顺序检查通过。')
    else:
        args.playlist.write_bytes(expected.encode('utf8'))
        print('已按省级行政区划代码及省内车牌代码排序。')
