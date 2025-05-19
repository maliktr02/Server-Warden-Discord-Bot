import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime
import json
import asyncio
import random
from database import Database

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Database initialization
db = Database()

class ServerWarden(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warned_users = {}
        self.muted_users = {}
        self.flood_protection = {}
        self.banned_words = set()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{bot.user} has connected to Discord!')
        await db.init()
        await self.load_configurations()

    async def load_configurations(self):
        # Load banned words for all guilds
        for guild in self.bot.guilds:
            banned_words = await db.get_banned_words(guild.id)
            self.banned_words.update(banned_words)

    @commands.command(name='çekiliş')
    async def giveaway(self, ctx, time: str, *, prize: str):
        """Basit çekiliş başlatır"""
        try:
            # Convert time to seconds
            time_seconds = self.parse_time(time)
            if not time_seconds:
                await ctx.send("Geçersiz zaman formatı! Örnek: 1h, 30m, 1d")
                return

            embed = discord.Embed(
                title="🎉 Çekiliş",
                description=f"**Ödül:** {prize}\n\n"
                           f"**Kazanan Sayısı:** 1\n"
                           f"**Bitiş:** {time}\n\n"
                           f"Katılmak için 🎉 emojisine tıklayın!",
                color=discord.Color.blue()
            )
            message = await ctx.send(embed=embed)
            await message.add_reaction("🎉")

            await asyncio.sleep(time_seconds)
            message = await message.channel.fetch_message(message.id)
            users = [user async for user in message.reactions[0].users()]
            users.remove(self.bot.user)

            if not users:
                await ctx.send("Kimse katılmadı! 😢")
                return

            winner = random.choice(users)
            await ctx.send(f"🎉 Tebrikler {winner.mention}! {prize} kazandınız!")

        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='mute')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, time: str = None, *, reason: str = "Sebep belirtilmedi"):
        """Kullanıcıyı mute atar"""
        if time:
            duration = self.parse_time(time)
            if not duration:
                await ctx.send("Geçersiz zaman formatı! Örnek: 1h, 30m, 1d")
                return
        else:
            duration = None

        try:
            await member.timeout(datetime.timedelta(seconds=duration) if duration else None, reason=reason)
            embed = discord.Embed(
                title="🔇 Kullanıcı Mute Edildi",
                description=f"**Kullanıcı:** {member.mention}\n"
                           f"**Sebep:** {reason}\n"
                           f"**Süre:** {time if time else 'Süresiz'}\n"
                           f"**Moderatör:** {ctx.author.mention}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

            if duration:
                self.muted_users[member.id] = {
                    'end_time': datetime.datetime.now() + datetime.timedelta(seconds=duration),
                    'guild_id': ctx.guild.id
                }

        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Sebep belirtilmedi"):
        """Kullanıcıyı banlar"""
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Kullanıcı Banlandı",
                description=f"**Kullanıcı:** {member.mention}\n"
                           f"**Sebep:** {reason}\n"
                           f"**Moderatör:** {ctx.author.mention}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Sebep belirtilmedi"):
        """Kullanıcıyı sunucudan atar"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Kullanıcı Atıldı",
                description=f"**Kullanıcı:** {member.mention}\n"
                           f"**Sebep:** {reason}\n"
                           f"**Moderatör:** {ctx.author.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='uyarı')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Sebep belirtilmedi"):
        """Kullanıcıya uyarı verir"""
        try:
            await db.add_warning(member.id, ctx.guild.id, reason, ctx.author.id)
            embed = discord.Embed(
                title="⚠️ Uyarı Verildi",
                description=f"**Kullanıcı:** {member.mention}\n"
                           f"**Sebep:** {reason}\n"
                           f"**Moderatör:** {ctx.author.mention}",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='uyarılar')
    async def warnings(self, ctx, member: discord.Member = None):
        """Kullanıcının uyarılarını gösterir"""
        member = member or ctx.author
        warnings = await db.get_warnings(member.id, ctx.guild.id)

        if not warnings:
            await ctx.send(f"{member.mention} kullanıcısının hiç uyarısı yok!")
            return

        embed = discord.Embed(
            title=f"⚠️ {member.name}'in Uyarıları",
            color=discord.Color.yellow()
        )

        for i, warn in enumerate(warnings, 1):
            moderator = ctx.guild.get_member(warn['moderator_id'])
            embed.add_field(
                name=f"Uyarı #{i}",
                value=f"**Sebep:** {warn['reason']}\n"
                      f"**Moderatör:** {moderator.mention if moderator else 'Bilinmiyor'}\n"
                      f"**Tarih:** {warn['timestamp']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='avatar')
    async def avatar(self, ctx, member: discord.Member = None):
        """Kullanıcının avatarını gösterir"""
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member.name}'in Avatarı",
            color=discord.Color.blue()
        )
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='yazıtura')
    async def coinflip(self, ctx):
        """Yazı tura atar"""
        result = random.choice(['Yazı', 'Tura'])
        embed = discord.Embed(
            title="🪙 Yazı Tura",
            description=f"Sonuç: **{result}**",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(name='oylama')
    async def poll(self, ctx, *, question):
        """Oylama başlatır"""
        embed = discord.Embed(
            title="📊 Oylama",
            description=question,
            color=discord.Color.blue()
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await message.add_reaction("🤷")

    def parse_time(self, time_str):
        """Zaman string'ini saniyeye çevirir"""
        try:
            unit = time_str[-1].lower()
            value = int(time_str[:-1])
            
            if unit == 's':
                return value
            elif unit == 'm':
                return value * 60
            elif unit == 'h':
                return value * 3600
            elif unit == 'd':
                return value * 86400
            else:
                return None
        except:
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Caps lock kontrolü
        if len(message.content) > 10 and message.content.isupper():
            await message.delete()
            await message.channel.send(f"{message.author.mention}, lütfen büyük harf kullanımını azaltın!")

        # Flood kontrolü
        if message.author.id in self.flood_protection:
            if (datetime.datetime.now() - self.flood_protection[message.author.id]['last_message']).total_seconds() < 2:
                self.flood_protection[message.author.id]['count'] += 1
                if self.flood_protection[message.author.id]['count'] >= 5:
                    await message.author.timeout(datetime.timedelta(minutes=5), reason="Flood yapma")
                    await message.channel.send(f"{message.author.mention} flood yaptığı için 5 dakika mute edildi!")
            else:
                self.flood_protection[message.author.id]['count'] = 1
        else:
            self.flood_protection[message.author.id] = {
                'last_message': datetime.datetime.now(),
                'count': 1
            }

        # Yasaklı kelime kontrolü
        for word in self.banned_words:
            if word.lower() in message.content.lower():
                await message.delete()
                await message.author.timeout(datetime.timedelta(minutes=30), reason="Yasaklı kelime kullanımı")
                await message.channel.send(f"{message.author.mention} yasaklı kelime kullandığı için 30 dakika mute edildi!")
                break

        # Mesaj logları
        if await db.is_premium(message.guild.id):
            log_channel = discord.utils.get(message.guild.channels, name='message-logs')
            if log_channel:
                embed = discord.Embed(
                    title="📝 Yeni Mesaj",
                    description=f"**Kanal:** {message.channel.mention}\n"
                               f"**Yazar:** {message.author.mention}\n"
                               f"**İçerik:** {message.content}",
                    color=discord.Color.green()
                )
                await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerWarden(bot))

# Bot'u başlat
bot.run(os.getenv('DISCORD_TOKEN')) 