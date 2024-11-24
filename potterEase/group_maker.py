import discord
from discord.ext import commands
import random
import asyncio

# Intents 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# bot 인스턴스를 외부에서 주입받기 위한 함수
def setup(bot):
    @bot.command(name='그룹')  # 커맨드 이름을 '%그룹'으로 설정
    async def group_maker(ctx):
        members = ['알리샤', '에이셔', '이든', '키릴', '헬리오스', '필릭스', '시엘', '트윌리']
        
        # Ask for members not participating
        await ctx.send('참여하지 않는 멤버는 누구? (이름만 적음, 띄어쓰기로 구분, 없으면 "x" 입력)')

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            # Wait for user response
            response = await bot.wait_for('message', check=check, timeout=30.0)
            excluded_members = response.content.split()  # Convert input to list
            
            # Check for 'x' input
            if response.content.strip().lower() == "x":
                excluded_members = []  # No members excluded

            # Check valid and invalid excluded members
            valid_excluded = [member for member in excluded_members if member in members]
            invalid_excluded = [member for member in excluded_members if member not in members]

            # Create available members list
            available_members = [member for member in members if member not in valid_excluded]

            # Print invalid members
            if invalid_excluded:
                await ctx.send(f'다음 멤버는 리스트에 없습니다: {", ".join(invalid_excluded)}')

            await ctx.send(f'사다리에 사용할 멤버: {", ".join(available_members)}')

            # Ask for group size
            await ctx.send('몇 명씩 그룹 지을까?')
            response = await bot.wait_for('message', check=check, timeout=30.0)
            group_size = int(response.content)

            # Create groups
            random.shuffle(available_members)
            groups = [available_members[i:i + group_size] for i in range(0, len(available_members), group_size)]
            
            # Handle remaining members
            remaining_members_count = len(available_members) % group_size
            if remaining_members_count != 0:
                remaining_members = available_members[-remaining_members_count:]  # Remaining members
                for member in remaining_members:
                    random.choice(groups).append(member)  # Add to a random group
                await ctx.send('남는 멤버를 추가로 배정하였습니다.')

            # Print results
            for i, group in enumerate(groups):
                await ctx.send(f'그룹 {i + 1}: {", ".join(group)}')

        except asyncio.TimeoutError:
            await ctx.send('시간이 초과되었습니다. 다시 시도하세요.')
