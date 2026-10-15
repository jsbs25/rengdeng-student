#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成历史库：回族历史 + 穆斯林历史 + 中国穆斯林历史（大量内容）"""
import json, os, re, sys, time, urllib.request
from pathlib import Path

DIR = Path(__file__).parent
KEY_FILE = DIR / 'data' / 'ai_key.txt'

def get_key():
    k = ''
    if KEY_FILE.exists():
        k = open(KEY_FILE, encoding='utf-8').read().strip()
    if not k:
        k = os.environ.get('DEEPSEEK_API_KEY') or os.environ.get('LOBSTER_APIKEY_DEEPSEEK') or ''
    return k

def chat(prompt, key, retries=3):
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3500,
        "temperature": 0.7,
    }, ensure_ascii=False).encode('utf-8')
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions", data=body,
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
                method="POST")
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            return d['choices'][0]['message']['content']
        except Exception as e:
            print(f'  重试 {attempt+1}: {e}')
            time.sleep(4)
    return None

# 主题列表：(分类, 分类中文, 图标, 标题)
TOPICS = [
    # ===== 回族历史（16 篇）=====
    ('huihui', '回族历史', '🌙', '回族的起源与形成'),
    ('huihui', '回族历史', '🌙', '唐宋时期的蕃客与海上丝绸之路'),
    ('huihui', '回族历史', '🌙', '元代回回人的崛起（赛典赤·赡思丁）'),
    ('huihui', '回族历史', '🌙', '明代回族与郑和下西洋'),
    ('huihui', '回族历史', '🌙', '清代回族：起义与抗争（杜文秀·苏四十三）'),
    ('huihui', '回族历史', '🌙', '近代回族与抗日战争（马本斋·回民支队）'),
    ('huihui', '回族历史', '🌙', '回族的饮食文化'),
    ('huihui', '回族历史', '🌙', '回族的服饰与婚俗'),
    ('huihui', '回族历史', '🌙', '回族节日：开斋节·古尔邦节·圣纪节'),
    ('huihui', '回族历史', '🌙', '经堂教育与现代回族教育'),
    ('huihui', '回族历史', '🌙', '回族著名人物（海瑞·李贽·马坚）'),
    ('huihui', '回族历史', '🌙', '回族聚居区：宁夏·甘肃·云南'),
    ('huihui', '回族历史', '🌙', '中国清真寺建筑艺术'),
    ('huihui', '回族历史', '🌙', '回族武术与摔跤文化'),
    ('huihui', '回族历史', '🌙', '回族与中华文化的交融'),
    ('huihui', '回族历史', '🌙', '回族人口分布与当代发展'),
    # ===== 穆斯林历史（16 篇）=====
    ('muslim', '穆斯林历史', '🕌', '先知穆罕默德生平'),
    ('muslim', '穆斯林历史', '🕌', '四大哈里发时期'),
    ('muslim', '穆斯林历史', '🕌', '伍麦叶王朝与伊斯兰扩张'),
    ('muslim', '穆斯林历史', '🕌', '阿拔斯王朝：伊斯兰黄金时代'),
    ('muslim', '穆斯林历史', '🕌', '安达卢斯：西班牙的伊斯兰文明'),
    ('muslim', '穆斯林历史', '🕌', '法蒂玛王朝与开罗'),
    ('muslim', '穆斯林历史', '🕌', '塞尔柱帝国与十字军时代'),
    ('muslim', '穆斯林历史', '🕌', '奥斯曼帝国：六百年的辉煌'),
    ('muslim', '穆斯林历史', '🕌', '萨法维王朝与波斯'),
    ('muslim', '穆斯林历史', '🕌', '莫卧儿帝国与泰姬陵'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰医学的黄金成就'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰天文学与数学'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰哲学：伊本·西那与安萨里'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰建筑与艺术'),
    ('muslim', '穆斯林历史', '🕌', '苏菲主义与精神传承'),
    ('muslim', '穆斯林历史', '🕌', '圣训学与教法学的发展'),
    # ===== 第二批补充主题（22 篇）=====
    ('huihui', '回族历史', '🌙', '回族语言与经堂语'),
    ('huihui', '回族历史', '🌙', '回族文学与诗歌'),
    ('huihui', '回族历史', '🌙', '回族音乐与花儿'),
    ('huihui', '回族历史', '🌙', '回族的传统手工艺'),
    ('huihui', '回族历史', '🌙', '回族商业传统'),
    ('huihui', '回族历史', '🌙', '回族与运河驿站'),
    ('huihui', '回族历史', '🌙', '回族海外侨胞'),
    ('huihui', '回族历史', '🌙', '回族妇女与家庭'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰教历与节日'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰经济思想'),
    ('muslim', '穆斯林历史', '🕌', '翻译运动与知识传承'),
    ('muslim', '穆斯林历史', '🕌', '伊本·赫勒敦与历史学'),
    ('muslim', '穆斯林历史', '🕌', '伊本·白图泰与地理大旅行'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰军事技术与火器'),
    ('muslim', '穆斯林历史', '🕌', '清真寺建筑的千年演变'),
    ('muslim', '穆斯林历史', '🕌', '当代伊斯兰世界概览'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林与一带一路'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国伊斯兰经学院教育'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林的慈善传统'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国清真食品产业'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林社区与清真寺服务'),
    ('cnmuslim', '中国穆斯林', '🕋', '港澳台地区的穆斯林'),
    # ===== 第三批补充主题（20 篇）=====
    ('huihui', '回族历史', '🌙', '回族传统医学与香药'),
    ('huihui', '回族历史', '🌙', '回族与科举制度'),
    ('huihui', '回族历史', '🌙', '回族村落与清真寺社区'),
    ('huihui', '回族历史', '🌙', '回族书画与阿文书法'),
    ('huihui', '回族历史', '🌙', '回族口述史与家族记忆'),
    ('huihui', '回族历史', '🌙', '回族武术的门派与传承'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰法律（沙里亚）的演变'),
    ('muslim', '穆斯林历史', '🕌', '穆斯林世界的女性学者'),
    ('muslim', '穆斯林历史', '🕌', '阿拉伯马与骑兵传统'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰金融的现代发展'),
    ('muslim', '穆斯林历史', '🕌', '穆斯林世界与印刷术'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰园林艺术'),
    ('muslim', '穆斯林历史', '🕌', '麦加朝觐的千年历史'),
    ('muslim', '穆斯林历史', '🕌', '清真寺在现代穆斯林社会的角色'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林人口与分布'),
    ('cnmuslim', '中国穆斯林', '🕋', '云南回族的历史与复兴'),
    ('cnmuslim', '中国穆斯林', '🕋', '清真八大碗与穆斯林菜系'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林书法艺术'),
    ('cnmuslim', '中国穆斯林', '🕋', '回族教育世家与文脉'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林与国际交流'),
    # ===== 第四批补充主题（20 篇）=====
    ('huihui', '回族历史', '🌙', '回族商贸集市与赶集'),
    ('huihui', '回族历史', '🌙', '回族婚俗详解'),
    ('huihui', '回族历史', '🌙', '回族丧葬礼仪'),
    ('huihui', '回族历史', '🌙', '回族剪纸与民间艺术'),
    ('huihui', '回族历史', '🌙', '回族方言与谚语'),
    ('huihui', '回族历史', '🌙', '回族传统节日详解'),
    ('muslim', '穆斯林历史', '🕌', '天房黑石的传说'),
    ('muslim', '穆斯林历史', '🕌', '耶路撒冷与阿克萨清真寺'),
    ('muslim', '穆斯林历史', '🕌', '马德拉萨：伊斯兰学校体系'),
    ('muslim', '穆斯林历史', '🕌', '阿拉伯医学家：拉齐与宰赫拉维'),
    ('muslim', '穆斯林历史', '🕌', '花拉子米与代数学'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰黄金时代的女性'),
    ('muslim', '穆斯林历史', '🕌', '伊本·朱拜尔与朝觐游记'),
    ('muslim', '穆斯林历史', '🕌', '现代伊斯兰复兴运动'),
    ('cnmuslim', '中国穆斯林', '🕋', '西北门宦的形成与发展'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林与盖碗茶文化'),
    ('cnmuslim', '中国穆斯林', '🕋', '穆斯林聚居区的特色市场'),
    ('cnmuslim', '中国穆斯林', '🕋', '从经堂到学堂：中国穆斯林教育史'),
    ('cnmuslim', '中国穆斯林', '🕋', '回族杰出科学家'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国清真寺的现代保护'),
    # ===== 第五批补充主题（10 篇）=====
    ('huihui', '回族历史', '🌙', '回族建筑特色'),
    ('huihui', '回族历史', '🌙', '回族体育竞技'),
    ('huihui', '回族历史', '🌙', '回族与茶马古道'),
    ('huihui', '回族历史', '🌙', '回族传统节日的地方差异'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰书法艺术'),
    ('muslim', '穆斯林历史', '🕌', '穆斯林世界的音乐传统'),
    ('muslim', '穆斯林历史', '🕌', '阿德布：伊斯兰教育理念'),
    ('muslim', '穆斯林历史', '🕌', '中东地理与文明交流'),
    ('cnmuslim', '中国穆斯林', '🕋', '当代著名中国穆斯林人物'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国清真寺文化遗产保护'),
    # ===== 第六批补充主题（6 篇）=====
    ('huihui', '回族历史', '🌙', '回族传统医药典籍'),
    ('huihui', '回族历史', '🌙', '回族马帮与驮队'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰陶瓷与玻璃工艺'),
    ('muslim', '穆斯林历史', '🕌', '穆斯林世界的名城：巴格达·开罗·科尔多瓦'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林碑刻文献'),
    ('cnmuslim', '中国穆斯林', '🕋', '清真寺楹联文化'),
    # ===== 第七批补充主题（4 篇）=====
    ('huihui', '回族历史', '🌙', '回族传统节庆市集'),
    ('muslim', '穆斯林历史', '🕌', '伊斯兰历法的科学基础'),
    ('muslim', '穆斯林历史', '🕌', '穆斯林世界的商路与驿站'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林的生态传统'),
    # ===== 中国穆斯林历史（10 篇）=====
    ('cnmuslim', '中国穆斯林', '🕋', '伊斯兰教传入中国（唐永徽二年）'),
    ('cnmuslim', '中国穆斯林', '🕋', '唐宋蕃坊与穆斯林商人'),
    ('cnmuslim', '中国穆斯林', '🕋', '元朝回回与色目人'),
    ('cnmuslim', '中国穆斯林', '🕋', '明代穆斯林：郑和与航海'),
    ('cnmuslim', '中国穆斯林', '🕋', '清代中国穆斯林'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国伊斯兰教派与门宦'),
    ('cnmuslim', '中国穆斯林', '🕋', '西安化觉巷清真大寺'),
    ('cnmuslim', '中国穆斯林', '🕋', '北京牛街礼拜寺'),
    ('cnmuslim', '中国穆斯林', '🕋', '泉州清净寺与海上丝路'),
    ('cnmuslim', '中国穆斯林', '🕋', '中国穆斯林学者与翻译事业'),
]

PROMPT_TMPL = """你是中国穆斯林文化研究者。请写一篇关于「{title}」的历史文章（约500-600字），要求：
1. 内容准确、有历史细节（人名、地名、年代）
2. 涉及阿拉伯语术语时附中文解释
3. 客观、尊重历史事实
4. 只输出文章正文（不要标题，不要markdown格式符号，不要空行分段——用自然段落连续输出）

文章内容："""

def main():
    key = get_key()
    if not key:
        print('没有 API key')
        sys.exit(1)
    out_file = DIR / 'data' / 'history.json'
    all_data = []
    if out_file.exists():
        all_data = json.load(open(out_file, encoding='utf-8'))
    done_titles = {d['title'] for d in all_data}
    for i, (cat, cat_cn, icon, title) in enumerate(TOPICS):
        if title in done_titles:
            print(f'跳过已完成: {title}')
            continue
        print(f'[{i+1}/{len(TOPICS)}] 生成: {title}...')
        body = None
        for _ in range(3):
            body = chat(PROMPT_TMPL.format(title=title), key)
            if body and len(body) > 300:
                break
            print('  重试...')
            time.sleep(3)
        if body and len(body) > 300:
            # 清理 markdown 符号
            body = body.replace('**', '').replace('##', '').replace('#', '').strip()
            all_data.append({'cat': cat, 'cat_cn': cat_cn, 'icon': icon, 'title': title, 'body': body})
            json.dump(all_data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f'  ✓ {len(body)} 字')
        else:
            print(f'  ✗ 失败，跳过')
        time.sleep(1.5)
    print(f'完成：{len(all_data)} 篇')
    json.dump(all_data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
