import discord
from discord.ext import commands
import json
import random
import os
import sys
import subprocess  # subprocess 모듈 추가

# 환경 변수 로드
from dotenv import load_dotenv

# 사용자 데이터 및 명령어 처리 모듈
from stats import (
    나,
    save_user_data,
    handle_나_command,
    handle_능력치_command,
)

# 기타 기능 모듈
import group_maker  # 그룹 생성 기능
import shortcuts  # 단축 명령어 기능
import money  # 금전 관련 기능

# 현재 파일의 디렉토리 경로를 가져옴
current_dir = os.path.dirname(os.path.abspath(__file__))
# member_selection_dormitory_score.py의 상대 경로
module_path = os.path.join(current_dir, 'member Selection_Dormitory Score')

# 모듈 경로 추가
sys.path.append(module_path)

# 모듈 임포트
import member_selection_dormitory_score

# oshimagic_bot.py를 서브 프로세스로 실행
subprocess.Popen(['python', '../potter_oshimagic/oshimagic_bot.py'])

# Intents 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# 디스코드 봇의 기본 설정
bot = commands.Bot(command_prefix='%', intents=intents)

# member_selection_dormitory_score.py의 setup 함수 호출
member_selection_dormitory_score.setup(bot)  # 명령어 등록

# ------------------------------------------------------------------------------------------

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    print(f'{bot.user}로 로그인했습니다.')

    # group_maker.py의 setup 함수 호출
    group_maker.setup(bot)

    # shortcuts.py의 setup 함수 호출
    shortcuts.setup(bot)  

    # money.py의 setup 함수 호출
    money.setup(bot)  # money.py의 setup 함수를 호출하여 명령어 등록

ITEMS_FOLDER = 'Hogsmeade_item'

# 아이템 목록을 자동으로 가져오는 함수
def get_item_list():
    items = []
    for file in os.listdir(ITEMS_FOLDER):
        if os.path.isfile(os.path.join(ITEMS_FOLDER, file)):
            item_name, _ = os.path.splitext(file)  # 파일 이름과 확장자 분리
            items.append(item_name)  # 이름만 추가
    return items

# 추첨 테스트 커맨드
@bot.command(name='추첨')
async def 추첨(ctx):
    items = get_item_list()
    if not items:
        await ctx.send("아이템이 없습니다.")
        return

    nickname = ctx.author.display_name
    selected_item = random.choice(items)
    await ctx.send(f'**{nickname}**이(가) 뽑은 오늘의 아이템은... 두구두구두구\n### 🎉  {selected_item}  🎉')

    # 아이템 이미지 전송
    item_image_path = os.path.join(ITEMS_FOLDER, f"{selected_item}.png")  # 확장자에 맞게 수정
    if os.path.exists(item_image_path):
        await ctx.send(file=discord.File(item_image_path))
    else:
        await ctx.send("아이템 이미지를 찾을 수 없습니다.")

@bot.command()
async def 미연시(ctx, *, name1=None):
    if name1 is None:
        await ctx.send('사용법: %미연시 [이름]')
        return

    await ctx.reply('{} 닮은꼴미연시..'.format(name1))

    ran = random.randint(1, 5)

    endings = ["해피엔딩", "배드엔딩", "메리배드엔딩", "진엔딩", "노말엔딩"]
    await ctx.channel.send(f'## "{endings[ran - 1]}"')

@bot.listen('on_message')
async def on_message(message):
    if message.author == bot.user:
        return

    # '!디체스머스'에 반응
    if message.content == '!디체스머스':
        random_number = random.randint(1, 6)  # 1부터 6까지의 랜덤 숫자 생성
        await message.channel.send(f'🎲 {random_number} ')
        return  # 다른 핸들러로 넘어가지 않도록 종료

    # '!나' 명령어 처리
    if message.content.startswith('!나'):
        await handle_나_command(bot, message)
        return  # 명령어 처리를 완료했으므로 종료

    # '!공격'이나 '!방어'와 같은 명령어 처리
    elif message.content.startswith('!'):
        능력치 = message.content[1:]  # '!'를 제거한 부분
        await handle_능력치_command(bot, message, 능력치)
        return  # 명령어 처리를 완료했으므로 종료

# JSON 파일 경로
data_file = 'user_stats.json'

# JSON 파일이 없으면 생성
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f, indent=4)

# ------------------------------------------------------------------------------------------
# 토큰을 입력하세요.
bot.run('TOKEN')
