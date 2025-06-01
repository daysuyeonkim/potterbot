import discord
import random
import json
import os
import asyncio
from datetime import datetime
import pytz  # pytz 임포트 추가
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

# KST 시간대 가져오기
kst = pytz.timezone('Asia/Seoul')  # KST 정의 추가

# Intent 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

# 데이터 파일 경로 설정
base_path = '../potter_oshimagic/'
data_file = os.path.join(base_path, 'user_data.json')
before_data_file = os.path.join(base_path, 'before_user_data.json')
count_file = os.path.join(base_path, 'ohaa_count.json')
appeal_file = os.path.join(base_path, 'user_appeal_scores.json') 
before_appeal_file = os.path.join(base_path, 'before_appeal_scores.json')  
ohaa_usage_file = os.path.join(base_path, 'ohaa_usage.json')

# user_assets.json 파일 경로
assets_file_path = '../potterEase/user_assets.json'

# 전역 변수
server_user_data = {}
user_appeal_scores = {}
ohaa_usage = {}
ohaa_count = 0  # 초기화

# 데이터 초기화
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f)

if not os.path.exists(count_file):
    count_data = {'count': 0}
    with open(count_file, 'w') as f:
        json.dump(count_data, f)

if not os.path.exists(appeal_file):
    with open(appeal_file, 'w') as f:
        json.dump({}, f)

# 데이터 로드
with open(data_file, 'r') as f:
    server_user_data = json.load(f)

with open(count_file, 'r') as f:
    count_data = json.load(f)
    ohaa_count = count_data['count']

with open(appeal_file, 'r') as f:
    user_appeal_scores = json.load(f)

def load_assets():
    """user_assets.json에서 유저 자산 로드"""
    if not os.path.exists(assets_file_path):
        with open(assets_file_path, 'w') as f:
            json.dump({}, f)  # 빈 딕셔너리로 초기화
    with open(assets_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_assets(assets):
    """user_assets.json에 유저 자산 저장"""
    with open(assets_file_path, 'w', encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user.name}으로 로그인했습니다.')

@bot.command()
async def 공략(ctx, 기본점수: int = None):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # 기본점수가 None일 경우 메시지 출력
    if 기본점수 is None:
        await ctx.send("기본점수를 입력해주세요. (보너스 5 또는 보너스 10)")
        return

    # 서버 단위로 LOVE POINT 초기화
    if guild_id not in server_user_data:
        server_user_data[guild_id] = {}
    
    if user_id not in server_user_data[guild_id]:
        server_user_data[guild_id][user_id] = {
            'love_points': 0,
            'emotions': {}
        }

    # 기본점수 유효성 검사
    if 기본점수 not in [5, 10]:
        await ctx.send("기본점수는 5 또는 10이어야 합니다.")
        return
    
    # 랜덤한 값 생성 (1~20)
    random_value = random.randint(1, 20)
    total = 기본점수 + random_value
    
    # 유저의 LOVE POINT 업데이트
    server_user_data[guild_id][user_id]['love_points'] += total
    
    # 감정 획득 로직
    if random_value <= 5:
        emotions = ["공포", "모멸", "질투", "분노", "무시", "실망", "불신", "불쾌", "열등", "증오", "집착", "의존", "살의"]
        emotion = random.choice(emotions)
    else:
        emotions = ["충성", "애정", "우정", "공감", "흥미", "신뢰", "안락", "동경", "존경", "광신", "보호", "유쾌", "응원"]
        emotion = random.choice(emotions)

    # 유저의 감정 업데이트
    if 'emotions' not in server_user_data[guild_id][user_id]:
        server_user_data[guild_id][user_id]['emotions'] = {}

    if emotion in server_user_data[guild_id][user_id]['emotions']:
        server_user_data[guild_id][user_id]['emotions'][emotion] += 1
    else:
        server_user_data[guild_id][user_id]['emotions'][emotion] = 1

    # 포인트 데이터 저장
    with open(data_file, 'w') as f:
        json.dump(server_user_data, f)

    # 크렛 추가 (3크렛 획득)
    assets = load_assets()  # 유저 자산 로드
    if user_id not in assets:
        assets[user_id] = {'크렛': 0}  # 유저 자산 초기화
    assets[user_id]['크렛'] += 3  # 3크렛 추가
    save_assets(assets)  # 업데이트된 자산 저장

    # 결과 메시지 출력
    await ctx.send(f'기본점수 {기본점수} + 어필점수 {random_value} = 총합 {total} 💗LOVE POINT💗\n플레이어에게 **{emotion}**을(를) 느낀다······.\n**3크렛**을 획득하였습니다!')

    # 어필점수 저장
    if guild_id not in user_appeal_scores:
        user_appeal_scores[guild_id] = {}

    if user_id not in user_appeal_scores[guild_id]:
        user_appeal_scores[guild_id][user_id] = {'total_score': 0, 'count': 0}

    user_appeal_scores[guild_id][user_id]['total_score'] += random_value
    user_appeal_scores[guild_id][user_id]['count'] += 1

    # 어필 데이터 저장
    with open(appeal_file, 'w') as f:
        json.dump(user_appeal_scores, f)

@bot.command()
async def 예상엔딩(ctx):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # 어필 점수 가져오기
    with open(appeal_file, 'r') as f:
        user_appeal_scores = json.load(f)

    # 서버별 어필 점수 확인
    if guild_id not in user_appeal_scores or user_id not in user_appeal_scores[guild_id] or user_appeal_scores[guild_id][user_id]['count'] == 0:
        await ctx.send("어필점수가 없습니다.")
        return

    total_appeal_score = user_appeal_scores[guild_id][user_id]['total_score']
    count = user_appeal_scores[guild_id][user_id]['count']
    average_appeal_score = total_appeal_score / count  # 어필점수 평균 계산
    await ctx.send(f"### 당신의 엔딩은 아마도······\n💕어필점수 평균: {average_appeal_score:.2f}💕")

    # 평균에 따른 문장 출력
    if average_appeal_score <= 3:
        await ctx.send("🖤 **배드엔드 (Bad End)**: 0점 ~ 3점")
    elif average_appeal_score <= 7:
        await ctx.send("💙 **노멀엔드 (Normal End)**: 4점 ~ 7점")
    elif average_appeal_score <= 11:
        await ctx.send("💔 **메리배드엔드 (Merry Bad End)**: 8점 ~ 11점")
    elif average_appeal_score <= 16:
        await ctx.send("💛 **해피엔드 (Happy End)**: 12점 ~ 16점")
    else:
        await ctx.send("💖 **진엔드 (True End)**: 17점 ~ 20점")

@bot.command()
async def 러브포인트(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)

    # user_data.json에서 LOVE POINT 가져오기
    with open(data_file, 'r') as f:
        server_user_data = json.load(f)

    # 유저의 LOVE POINT 가져오기
    user_data = server_user_data.get(guild_id, {}).get(user_id, {})
    user_love_points = user_data.get('love_points', 0)

    # [ 사랑을 먹는 자··· ] 결과 출력
    love_rank_message = f"### 내가 지금까지 모은 LOVE POINT: {user_love_points}\n"
    love_rank_message += "\n**[ 사랑을 먹는 자··· ]**\n"

    # 모든 유저의 LOVE POINT 가져오기 (user_data.json 기준)
    all_users = server_user_data.get(guild_id, {})
    sorted_users = sorted(all_users.items(), key=lambda x: x[1].get('love_points', 0), reverse=True)
    top_users = sorted_users[:3]

    for rank, (uid, data) in enumerate(top_users, start=1):
        member = ctx.guild.get_member(int(uid))
        ranking_name = member.display_name if member else "Unknown User"
        love_rank_message += f"💘  **{rank}위** {ranking_name}: {data['love_points']} 포인트\n"

    await ctx.send(love_rank_message)

    # [ Normal 클리어 결과 ] 고정된 메시지 출력
    normal_rank_message = "\n**[ Normal 클리어 결과 ]**\n"
    normal_rank_message += "💘  **1위** 어부 키릴 데 바벨: 216 포인트\n"
    normal_rank_message += "💘  **2위** 떨어진 천사 에이셔 오포드: 132 포인트\n"
    normal_rank_message += "💘  **3위** 트윌리 오스만투스: 101 포인트\n"

    await ctx.send(normal_rank_message)

@bot.command()
async def 공략현황(ctx):
    guild_id = str(ctx.guild.id)  # 서버 ID
    total_love_points = sum(user.get('love_points', 0) for user in server_user_data.get(guild_id, {}).values())  # 모든 유저의 LOVE POINT 총합 계산
    철벽HP = 3000 - total_love_points  # 철벽HP 계산
    철벽HP = max(철벽HP, 0)  # 철벽HP가 0 이하일 경우 0으로 설정
    
    # 결과 출력
    response = f'플레이어의 철벽······  {철벽HP}/3000'
    
    if 철벽HP == 0:
        response += "\n절박하고 걱정어린 목소리가 들려온다······"
    
    await ctx.send(response)

@bot.command()
async def 나의감정(ctx):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)  # 서버 ID

    if guild_id not in server_user_data or user_id not in server_user_data[guild_id] or not server_user_data[guild_id][user_id]['emotions']:
        await ctx.send("획득한 감정이 없습니다.")
        return

    response = "플레이어에 대한 감정을 제어할 수 없다······.\n"
    for emotion, count in server_user_data[guild_id][user_id]['emotions'].items():
        if count >= 3:
            response += f"{emotion} X {count} **(충동적)**\n"
        else:
            response += f"{emotion} X {count}\n"
    
    await ctx.send(response)

@bot.command()
async def 포인트초기화(ctx):
    await ctx.send("정말로 리셋 할거야? (y/n)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if msg.content.lower() == 'y':
            guild_id = str(ctx.guild.id)  # 서버 ID
            if guild_id in server_user_data:
                for user_id in server_user_data[guild_id]:
                    server_user_data[guild_id][user_id]['love_points'] = 0  # 포인트 초기화
                    # 어필 포인트 초기화
                    if user_id in user_appeal_scores:
                        del user_appeal_scores[user_id]  # 어필 포인트 삭제
            await ctx.send("모든 유저의 LOVE POINT와 어필 포인트가 초기화되었습니다.")
            
            # 데이터 저장
            with open(data_file, 'w') as f:
                json.dump(server_user_data, f)
            with open(appeal_file, 'w') as f:
                json.dump(user_appeal_scores, f)  # 어필 포인트 데이터 저장
        else:
            await ctx.send("포인트 초기화를 취소했습니다.")
    except asyncio.TimeoutError:
        await ctx.send("시간이 초과되었습니다. 포인트 초기화가 취소되었습니다.")

@bot.command()
async def 감정초기화(ctx):
    await ctx.send("정말로 잊어버릴거야? (y/n)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if msg.content.lower() == 'y':
            guild_id = str(ctx.guild.id)  # 서버 ID
            if guild_id in server_user_data:
                for user_id in server_user_data[guild_id]:
                    server_user_data[guild_id][user_id]['emotions'] = {}  # 감정 초기화
            await ctx.send("모든 유저의 감정 리스트가 초기화되었습니다.")
            
            # 데이터 저장
            with open(data_file, 'w') as f:
                json.dump(server_user_data, f)
        else:
            await ctx.send("감정 초기화를 취소했습니다.")
    except asyncio.TimeoutError:
        await ctx.send("시간이 초과되었습니다. 감정 초기화가 취소되었습니다.")

# 오늘의 날씨
weather_list = [
"차가운 오후, 하얀 눈송이가 공중에서 춤추며 온도가 내려간다.",
"눈보라, 바람에 휘날리는 눈이 세상을 하얗게 덮는다.",
"겨울 비, 차가운 비가 내리며 세상을 더욱 쓸쓸하게 만든다.",
"안개 낀 아침, 신비로운 안개가 세상을 부드럽게 감싸고 있다.",
"상쾌한 날, 맑은 공기가 코를 찌르며 겨울의 청량함을 느낀다.",
"변덕, 갑자기 내리는 폭설이 세상을 하얗게 물들인다.",
"시려운 날씨, 공기가 무겁고 손끝이 얼어붙는다.",
"맑은 하늘, 구름 한 점 없이 파란 하늘이 겨울의 차가움을 드러낸다.",
"눈 오는 날, 소복이 쌓인 눈 위를 걸으며 자박이는 발자국 소리가 울린다.",
"시원한 날, 차가운 바람이 얼굴을 스치며 겨울의 무색 내음을 느끼게 한다.",
"눈발, 학교가 끝나자마자 하얀 눈이 땅을 덮는다.",
"겨울밤, 기온이 급격히 떨어져 따뜻한 이불이 그리워진다.",
"해질녘, 붉은 노을이 하늘을 물들이며 장작타는 내음이 스친다.",
"차가운 공기 속에서 겨울 간식 내음이 코를 간지럽힌다.",
"우박, 창문을 후둑이며 두드린다."
]

# 오늘의 장소
location_list = [
"눈 덮인 운동장이 겨울의 정취를 더하며 조용히 펼쳐진다.",
"칠판 앞에 서 있는 선생님의 목소리가 교실 가득 울려 퍼지며, 학생들은 집중한 눈빛으로 필기를 한다.",
"고요한 분위기 속에서 책장을 넘기는 소리와 함께, 학생들이 지식을 쌓아가는 아늑한 공간.",
"친구들과 함께 눈싸움을 하며 즐거운 소리가 끊이지 않는 운동장.",
"색색의 물감과 도화지가 널려 있는 미술실, 겨울을 주제로 한 학생들의 작품이 벽을 장식한다.",
"따뜻한 음료가 진열된 카페테리아, 학생들이 친구들과 함께 따뜻한 점심을 나누는 곳.",
"실험실, 화학 약품이 가득한 실험실에서 학생들이 안전 고글을 쓰고 실험에 몰두하는 모습이 인상적이다.",
"체육 수업 중 열띤 경쟁이 벌어지는 체육관, 땀방울이 흐르고 에너지가 넘치는 현장.",
"수업 사이사이에 학생들의 떠드는 소리가 가득한 복도, 친구들과의 짧은 대화가 이어진다.",
"자율학습시간, 조용한 분위기 속에서 각자 집중하며 공부하는 학생들, 서로의 열정이 느껴지는 공간.",
"햇살이 따뜻하게 비추는 옥상에서 친구들과 소소한 이야기를 나누며 여유를 즐긴다.",
"활동과 열정으로 가득한 동아리방, 꿈을 나누는 학생들의 열기가 느껴진다.",
"따뜻한 간식과 음료가 가득한 매점, 학생들의 발길이 끊이지 않는 인기 장소.",
"한가로운 교내 벤치. 눈이 쌓인 정원에서 학생들이 자연을 느끼며 잠시 쉬어가는 공간."
]

# Bonus 메시지
bonus_list = [
"눈 내리는 날, 하얀 눈밭에서 친구들과 함께 눈사람을 만든다.",
"아이들의 웃음소리, 겨울 방학을 만끽하는 아이들이 눈 속에서 뛰어놀고 있다.",
"겨울철 나무, 나뭇가지 끝 꽃위로 쌓인 눈이 아름답게 반짝인다.",
"따뜻한 음료의 향기, 핫초코와 생강차 따위의 달콤한 향기가 겨울을 알린다.",
"캠핑의 밤, 별빛 아래 모닥불과 함께하는 따뜻한 시간.",
"따뜻한 음료수, 스팀이 나는 음료가 손을 녹여준다."
"겨울 캠핑, 두텁게 챙겨입곤 함께 앉아 이야기를 나눈다."
"겨울 편의점, 시즌마다 불티나게 팔리는 것들이 많다."
]

@bot.command()
async def 오하아사(ctx):
    guild_id = str(ctx.guild.id)
    today = datetime.now(kst).date()  # 오늘 날짜를 KST로 가져오기

    # 서버가 오늘 이미 사용했는지 확인
    if guild_id in ohaa_usage and ohaa_usage[guild_id] == str(today):  # 문자열로 비교
        await ctx.send("오늘은 이미 %오하아사를 사용하셨습니다. 내일 다시 시도해 주세요!")
        return

    # 호출 횟수 증가
    global ohaa_count
    ohaa_count += 1

    # 호출 횟수 저장
    with open(count_file, 'w') as f:
        json.dump({'count': ohaa_count}, f)

    # 오늘 날짜 저장
    ohaa_usage[guild_id] = str(today)

    # 데이터 저장
    with open(ohaa_usage_file, 'w') as f:
        json.dump(ohaa_usage, f)

    # 현재 날짜 가져오기
    today_str = today.strftime("%d/%m/%Y")  # 원하는 형식으로 날짜 포맷팅

    # 오늘의 날씨와 장소 랜덤 선택
    weather = random.choice(weather_list)
    location = random.choice(location_list)

    # 메세지 포맷팅
    response = f"# {today_str}, 갇힌지 {ohaa_count}일째\n### 🍀오늘의 행운을 따르면 항목당 어필 보너스 5점🍀\n(**%공략**을 입력 후 **%보너스**를 사용하세요!)\n\n* **오늘의 날씨**\n{weather}\n* **행운의 장소**\n{location}"

    # 20% 확률로 Bonus 추가
    if random.random() < 0.2:  # 20% 확률
        bonus = random.choice(bonus_list)
        response += f"\n### +Bonus!!\n{bonus}"

    await ctx.send(response)

@bot.command()
async def 보너스(ctx):
    await ctx.send("🍀행운이 온다...! 5, 10, 15 중 몇 점 보너스? 숫자만 입력하세요!")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content in ['5', '10', '15']

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        bonus_value = int(msg.content)  # 유저가 선택한 값을 정수로 변환
        
        # 유저의 LOVE POINT 업데이트
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # 사용자 LOVE POINT 가져오기
        current_points = server_user_data.get(guild_id, {}).get(user_id, {}).get('love_points', 0)

        # 보너스 추가
        new_points = current_points + bonus_value
        server_user_data[guild_id][user_id]['love_points'] = new_points

        # 데이터 저장
        with open(data_file, 'w') as f:
            json.dump(server_user_data, f)

        # 결과 출력
        await ctx.send(f"+행운 점수 {bonus_value}💗LOVE POINT💗\n총 LOVE POINT: {new_points}")

    except asyncio.TimeoutError:
        await ctx.send("시간이 초과되었습니다. 보너스 선택이 취소되었습니다.")

@bot.command()
async def 오하아사초기화(ctx):
    global ohaa_count  # 전역 변수로 호출 횟수 사용

    # 호출 횟수 초기화
    ohaa_count = 0

    # 호출 횟수 저장
    with open(count_file, 'w') as f:
        json.dump({'count': ohaa_count}, f)

    # 서버의 날짜 기록 초기화
    ohaa_usage.clear()  # 모든 서버 기록 삭제

    # 데이터 저장
    with open(ohaa_usage_file, 'w') as f:
        json.dump(ohaa_usage, f)

    await ctx.send("`%오하아사` 호출 횟수가 초기화되었습니다. 사용 제한이 해제되었습니다.")

@bot.command()
async def 오시매직(ctx):
    # 커맨드 설명서
    command_help = """
    **%공략 [5or10]** : 기본점수를 입력하여 LOVE POINT를 획득합니다. 기본점수는 5 또는 10이어야 합니다.
**%보너스** : 이벤트씬 연출시 적용한 오하아사 보너스를 획득합니다.
**%공략현황** : 해피포터의 철벽 지수를 보여줍니다.
**%러브포인트** : 나의 누적 LOVE POINT와 상위 3명의 랭킹을 출력합니다.
**%나의감정** : 나의 감정들을 보여줍니다.
**%예상엔딩** : 나의 어필 점수들을 바탕으로 예상 엔딩을 출력합니다.
**%오하아사** : 오늘의 행운을 확인합니다.
    """
    await ctx.send(command_help)

# 봇 토큰으로 봇 실행
bot.run(TOKEN)
