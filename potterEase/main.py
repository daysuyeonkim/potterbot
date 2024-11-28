import discord
from discord.ext import commands
import json
import random
import os
import subprocess  # subprocess 모듈 추가
from stats import 나, save_user_data, handle_나_command, handle_능력치_command  # commands 모듈 임포트
import group_maker  # group_maker 모듈 임포트
import shortcuts 
import money  # money.py 모듈 임포트
import subprocess

# oshimagic_bot.py를 서브 프로세스로 실행
subprocess.Popen(['python', '../potter_oshimagic/oshimagic_bot.py'])

# Intents 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# 디스코드 봇의 기본 설정
bot = commands.Bot(command_prefix='%', intents=intents)

# ------------------------------------------------------------------------------------------

# Hogsmeade_item.txt 파일에서 아이템 읽기
def read_items():
    items = []
    with open('Hogsmeade_item.txt', 'r', encoding='utf-8') as file:
        items = [line.strip() for line in file.readlines()]
    return items

# 아이템을 JSON 파일로 저장하기
def save_to_json():
    items = read_items()
    with open('items.json', 'w', encoding='utf-8') as json_file:
        json.dump(items, json_file, ensure_ascii=False, indent=4)

# 아이템 로드하기
def load_items():
    with open('items.json', 'r', encoding='utf-8') as json_file:
        return json.load(json_file)

# 특정 폴더에서 검색어를 포함한 파일 찾기
def search_in_folder(search_term, folder_path):
    matched_files = []
    exact_matches = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_name, file_extension = os.path.splitext(file)

            if search_term.lower() == file_name.lower():  # 완전히 일치하는 경우
                exact_matches.append(os.path.join(root, file))
                return exact_matches, matched_files  # 즉시 반환
            elif search_term.lower() in file_name.lower():  # 포함된 경우
                matched_files.append(os.path.join(root, file))

    return exact_matches, matched_files

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

# 추첨 커맨드
@bot.command()
async def 추첨(ctx):
    items = load_items()
    selected_item = random.choice(items)
    
    nickname = ctx.author.display_name
    await ctx.send(f'**{nickname}**이(가) 뽑은 오늘의 아이템은... 두구두구두구\n### 🎉  {selected_item}  🎉')

    folder_path = 'Hogsmeade_item'
    exact_matches, matched_files = search_in_folder(selected_item, folder_path)

    if exact_matches:
        for file_path in exact_matches:
            await ctx.send(file=discord.File(file_path))
    elif matched_files:
        for file_path in matched_files:
            await ctx.send(file=discord.File(file_path))
    else:
        await ctx.send('파일을 찾을 수 없습니다.')

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

# JSON 파일 생성 (한 번만 실행)
if not os.path.exists('items.json'):
    save_to_json()

# JSON 파일 경로
data_file = 'user_stats.json'

# JSON 파일이 없으면 생성
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f, indent=4)

# ------------------------------------------------------------------------------------------
# 토큰을 입력하세요.
bot.run('MTI5MDg2NDAyNDE3NDcyNzE2OA.GhbLjj.RgO8ooWhDs8XTx4WP4v1nczxClP-kSRmZVmbCY')
