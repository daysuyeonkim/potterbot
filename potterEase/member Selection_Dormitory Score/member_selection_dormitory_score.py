import sys
import os
import discord
from discord.ext import commands
import json
import random
from discord.ui import Button, View

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 나머지 코드...
def setup(bot):
    bot.add_command(show_scores_rankings)
    bot.add_command(add_points)
    bot.add_command(subtract_points)
    bot.add_command(gacha_command)  # gacha_command를 등록

# 파일 경로
SCORES_FILE = os.path.join(os.path.dirname(__file__), "scores.txt")

# 점수 데이터 초기화
points = {}

# 이미지 폴더 및 저장 폴더
image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'friend_dolls')

# 랜덤 메시지 리스트
random_messages = [
    " ㅡ 어때. 마음에 들어?",
    " ㅡ 재미있는 추억이 되었길 바라",
    " ㅡ 이건 어떨까?",
]

# 이미지 설명 딕셔너리
image_descriptions = {
    "헬리오스 데 아르덴스": "선글라스... 벗겨지지 않는다...",
    "에이셔 오포드": "어쩐지 내 보석을 탐내고 있는 것 같다.",
    "이든 힉스": "지팡이를 들고 있다. 위협이라도 하려고? ",
    "라난시 애링턴": "왜... 눈물을 흘리는 거야?.",
    "세라피아스 아퀴노": "내제된 장난꾸러기의 기질이 엿보인다.",
    "알리샤 리든": "상냥한 말투에 뼈가 느껴진다.",
    "트윌리 오스만투스": "당장 내리지 않으면 몰락시켜버리겠어",
    "키릴 데 바벨": "나는 연습용 목각이 아니야.",
}

# 점수 데이터를 파일에 저장
def save_scores_to_file(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as file:
        for name, score in scores.items():
            file.write(f"{name}:{score}\n")
    print(f"점수가 {SCORES_FILE}에 저장되었습니다.")

# 점수 데이터를 파일에서 불러오기
def load_scores():
    global points
    if not os.path.exists(SCORES_FILE):
        print(f"{SCORES_FILE} 파일이 없어서 기본 점수를 설정합니다.")
        points = {}
        save_scores_to_file(points)
        return

    with open(SCORES_FILE, "r", encoding="utf-8") as file:
        for line in file:
            try:
                name, score = line.strip().split(":")
                points[name] = int(score)
            except ValueError:
                print(f"잘못된 데이터 형식: {line.strip()}")

# 초기 점수 로드
load_scores()

### 점수 관련 명령어 ###
@commands.command(name="기숙사점수")
async def show_scores_rankings(ctx, page: int = 1):
    if not points:
        await ctx.send("현재 점수가 없습니다. 점수를 추가해주세요!")
        return

    scores_per_page = 10
    sorted_scores = sorted(points.items(), key=lambda x: x[1], reverse=True)

    total_pages = (len(sorted_scores) - 1) // scores_per_page + 1  # scores_per_page 변수 사용
    if page < 1 or page > total_pages:
        await ctx.send(f"페이지 번호는 1에서 {total_pages} 사이여야 합니다.")
        return

    start_index = (page - 1) * scores_per_page
    end_index = start_index + scores_per_page
    selected_scores = sorted_scores[start_index:end_index]

    leaderboard = ""
    for idx, (name, score) in enumerate(selected_scores, start=start_index + 1):
        leaderboard += f"{idx}. {name} - {score}점\n"

    embed = discord.Embed(
        title=f"현재 순위 (페이지 {page}/{total_pages})",
        description=leaderboard,
        color=discord.Color.gold(),
    )
    await ctx.send(embed=embed)

    if page < total_pages:
        await ctx.send(f"⚠️ 다음 페이지는 `%기숙사점수 {page + 1}` 명령어로 확인하세요.")

@commands.command(name="점수추가")
@commands.has_permissions(administrator=True)
async def add_points(ctx, scores_name: str, score_to_add: int):
    if scores_name not in points:
        valid_names = ", ".join(points.keys())  # 기숙사 목록을 가져옴
        await ctx.send(f"{scores_name}은(는) 존재하지 않는 기숙사입니다. 현재 입력 가능한 기숙사 목록: {valid_names}")
        return

    points[scores_name] += score_to_add
    save_scores_to_file(points)

    embed = discord.Embed(
        title=f"{scores_name}에 {score_to_add}점 추가!",
        description=f"현재 점수: {points[scores_name]}점",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)

@commands.command(name="점수감점")
@commands.has_permissions(administrator=True)
async def subtract_points(ctx, scores_name: str, score_to_subtract: int):
    if scores_name not in points:
        valid_names = ", ".join(points.keys())
        await ctx.send(f"{scores_name}은(는) 존재하지 않는 기숙사입니다. 현재 입력 가능한 기숙사 목록: {valid_names}")
        return

    points[scores_name] -= score_to_subtract
    save_scores_to_file(points)

    embed = discord.Embed(
        title=f"{scores_name}에서 {score_to_subtract}점 감점!",
        description=f"현재 점수: {points[scores_name]}점",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed)

### 아이템 추첨 로직 ###
class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.clicked_users = set()

    @discord.ui.button(label="아이템 뽑기", style=discord.ButtonStyle.danger)
    async def gacha_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        from money import update_assets, save_assets, load_assets  # 지연 임포트

        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message("인형은 하루에 한 명만 뽑을 수 있습니다!", ephemeral=True)
            return

        self.clicked_users.add(interaction.user.id)

        # 크렛 10 차감
        user_id = str(interaction.user.id)  # 유저 ID
        update_assets(user_id, -10)  # 크렛 차감

        # 유저에게 인형뽑기 시작 메시지 전송
        await interaction.response.send_message(f'달각···달각···  **{interaction.user.display_name}**님, 인형뽑기를 시작합니다!')

        try:
            images = os.listdir(image_folder)
            if not images:
                await interaction.followup.send("이미지 폴더에 이미지가 없습니다.", ephemeral=True)
                return

            random_image = random.choice(images)
            image_path = os.path.join(image_folder, random_image)
            random_message = random.choice(random_messages)

            file_name, _ = os.path.splitext(random_image)
            image_description = image_descriptions.get(file_name, "이 이미지는 특별한 설명이 없습니다!")

            # 인형 이름에 ' 인형' 추가
            doll_name = f"{file_name} 인형"

            # 유저 자산에 추가
            assets = load_assets()
            if user_id not in assets:
                assets[user_id] = {'크렛': 0, 'last_attendance': None, '가구': {}}
            assets[user_id]['가구'][doll_name] = 100  # 가격 100 크렛

            save_assets(assets)  # 변경된 자산 저장

            embed = discord.Embed(
                title=file_name,
                description=f"{random_message}\n\n아이템 설명: {image_description}",
                color=discord.Color.green(),
            )
            embed.set_image(url=f"attachment://{random_image}")

            file = discord.File(image_path, filename=random_image)
            await interaction.followup.send(embed=embed, file=file)
        except Exception as e:
            await interaction.followup.send(f"에러가 발생했습니다: {e}", ephemeral=True)

@commands.command(name="인형뽑기")
async def gacha_command(ctx):
    # GachaView 생성 및 메시지 전송
    view = GachaView()
    await ctx.send("스폐셜한 인형을 뽑아보세요!", view=view)

# 쿠폰 사용 처리
async def handle_coupon_use(interaction, command):
    await interaction.response.defer()
    
    if command == "%인형뽑기":
        ctx = interaction.channel
        await gacha_command(ctx)  # gacha_command 호출
    else:
        await interaction.response.send_message(f"{command} 명령어가 실행되었습니다.")

### 에러 핸들러 ###
@add_points.error
@subtract_points.error
async def handle_errors(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("이 명령어는 관리자만 사용할 수 있습니다.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("올바른 사용법: `%점수추가 [점수 부여자 이름] [점수]` 또는 `%점수감점 [점수 부여자 이름] [점수]`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("점수는 숫자로 입력해야 합니다.")
    else:
        await ctx.send("알 수 없는 에러가 발생했습니다.")
