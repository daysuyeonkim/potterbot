import json
import os
import asyncio
from datetime import datetime
from discord.ext import commands

# JSON 파일 경로
data_file = '../potterEase/user_assets.json'

# 자산 정보를 저장할 파일이 없으면 생성
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f, indent=4)

# 자산 정보를 로드하는 함수
def load_assets():
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# 자산 정보를 저장하는 함수
def save_assets(assets):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False, indent=4)

# 자산 정보를 업데이트하는 함수
def update_assets(user_id, amount):
    assets = load_assets()
    
    if user_id not in assets:
        assets[user_id] = {'크렛': 0, 'last_attendance': None, '가구': {}}
    
    assets[user_id]['크렛'] += amount
    assets[user_id]['last_attendance'] = datetime.now().strftime('%Y-%m-%d')
    save_assets(assets)

# 유저의 크렛을 조회하는 함수
def get_크렛(user_id):
    assets = load_assets()
    return assets.get(user_id, {'크렛': 0})['크렛']

# 유저의 가구 정보를 조회하는 함수
def get_furniture(user_id):
    assets = load_assets()
    return assets.get(user_id, {}).get('가구', {})

# 출석 가능한지 확인하는 함수
def can_attend_today(user_id):
    assets = load_assets()
    
    if user_id not in assets:
        return True  # 처음 출석하는 경우
    
    last_attendance = assets[user_id].get('last_attendance')
    if last_attendance is None:
        return True  # 출석 기록이 없는 경우
    
    last_attendance_date = datetime.strptime(last_attendance, '%Y-%m-%d')
    today = datetime.now()
    
    return last_attendance_date.date() < today.date()

# '%ㅊㅊ' 또는 '%출석' 명령어 처리
async def handle_attendance(ctx):
    user_id = str(ctx.author.id)
    
    if not can_attend_today(user_id):
        await ctx.send(f'**{ctx.author.display_name}**님, 오늘은 이미 크렛을 획득했습니다. 내일 다시 시도해 주세요!')
        return
    
    update_assets(user_id, 1)  # 1크렛을 획득
    await ctx.send(f'**{ctx.author.display_name}**님, 출석 완료! **1크렛**을 획득하였습니다!')

# '%크렛' 명령어 처리
async def handle_check_크렛(ctx):
    user_id = str(ctx.author.id)
    크렛_amount = get_크렛(user_id)
    await ctx.send(f'**{ctx.author.display_name}**의 크렛: **{크렛_amount}**')

# '%가구구매' 명령어 처리
async def handle_buy_furniture(ctx, furniture_name=None):
    user_id = str(ctx.author.id)
    
    if furniture_name is None:
        await ctx.send('구매할 가구의 이름을 입력해 주세요. 예: `%가구구매 가구이름`')
        return
    
    await ctx.send(f'가구 `{furniture_name}`의 가격을 입력해 주세요.')

    def check_price(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        price_msg = await ctx.bot.wait_for('message', check=check_price, timeout=30)
        price = int(price_msg.content)  # 가격을 정수로 변환

        크렛_amount = get_크렛(user_id)
        
        if 크렛_amount >= price:
            # 크렛 차감 및 가구 정보 저장
            update_assets(user_id, -price)  # 크렛 차감
            assets = load_assets()
            if '가구' not in assets[user_id]:  # 가구 키 초기화
                assets[user_id]['가구'] = {}
            assets[user_id]['가구'][furniture_name] = price
            save_assets(assets)
            await ctx.send(f'**{ctx.author.display_name}**님, 가구 `{furniture_name}`를 **{price}**크렛에 구매하셨습니다!')
        else:
            await ctx.send(f'크렛이 부족합니다. 현재 보유 중인 크렛: **{크렛_amount}**크렛입니다.')
    
    except ValueError:
        await ctx.send('가격은 숫자로 입력해 주세요. 다시 입력해 주시기 바랍니다.')
        await handle_buy_furniture(ctx, furniture_name)  # 다시 가격 입력 요청
    except asyncio.TimeoutError:
        await ctx.send('가격 입력이 시간 초과되었습니다. 다시 시도해 주세요.')
    except Exception as e:
        await ctx.send(f'문제가 발생했습니다: {str(e)}')

# '%가구' 명령어 처리
async def handle_check_furniture(ctx):
    user_id = str(ctx.author.id)
    furniture = get_furniture(user_id)
    
    if not furniture:
        await ctx.send(f'구매한 가구가 없습니다.')
    else:
        furniture_list = "\n".join([f"• {name} - {price}크렛" for name, price in furniture.items()])  # 기호 추가
        await ctx.send(f'구매한 가구 목록:\n{furniture_list}')

# '%가구삭제' 명령어 처리
async def handle_delete_furniture(ctx):
    user_id = str(ctx.author.id)
    furniture = get_furniture(user_id)
    
    if not furniture:
        await ctx.send(f'삭제할 가구가 없습니다.')
        return
    
    # 가구 목록 생성
    furniture_list = "\n".join([f"• {name}" for name in furniture.keys()])
    await ctx.send(f'삭제할 가구를 선택해 주세요:\n{furniture_list}')

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in furniture.keys()

    try:
        # 유저의 입력 대기
        msg = await ctx.bot.wait_for('message', check=check, timeout=30)
        selected_furniture = msg.content  # 사용자가 선택한 가구 이름
        
        # 선택한 가구 삭제
        del furniture[selected_furniture]
        
        # 업데이트된 가구 정보 저장
        assets = load_assets()
        assets[user_id]['가구'] = furniture  # 수정된 가구 정보 저장
        save_assets(assets)

        await ctx.send(f'**{ctx.author.display_name}**님, 가구 `{selected_furniture}`가 삭제되었습니다.')
    
    except asyncio.TimeoutError:
        await ctx.send('시간 초과되었습니다. 가구 삭제를 취소합니다.')
    except Exception as e:
        await ctx.send(f'문제가 발생했습니다: {str(e)}')

# 봇의 명령어 등록
def setup(bot):
    @bot.command(name='ㅊㅊ')
    async def attendance_command(ctx):
        await handle_attendance(ctx)

    @bot.command(name='출석')
    async def attendance_command_alt(ctx):
        await handle_attendance(ctx)

    @bot.command(name='크렛')
    async def check_크렛_command(ctx):
        await handle_check_크렛(ctx)

    @bot.command(name='가구구매')
    async def buy_furniture_command(ctx, *, furniture_name=None):
        await handle_buy_furniture(ctx, furniture_name)

    @bot.command(name='가구')
    async def check_furniture_command(ctx):
        await handle_check_furniture(ctx)

    @bot.command(name='가구삭제')  # 가구 삭제 명령어 추가
    async def delete_furniture_command(ctx):
        await handle_delete_furniture(ctx)  # 삭제 처리 함수 호출
