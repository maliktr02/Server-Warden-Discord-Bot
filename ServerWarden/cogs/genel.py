import discord
from discord.ext import commands
import datetime
import random

class Genel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Botun gecikmesini gösterir."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'🏓 Pong! Gecikme: {latency}ms')

    @commands.command(name='saat')
    async def saat(self, ctx):
        """Şu anki saati gösterir."""
        now = datetime.datetime.now()
        await ctx.send(f'⏰ Şu anki saat: {now.strftime("%H:%M:%S")}')

    @commands.command(name='rastgele')
    async def rastgele(self, ctx, *, kelimeler):
        """Virgülle ayırarak yazılan kelimelerden rastgele birini seçer."""
        secenekler = [k.strip() for k in kelimeler.split(',') if k.strip()]
        if not secenekler:
            await ctx.send('Lütfen en az iki kelime girin!')
            return
        secim = random.choice(secenekler)
        await ctx.send(f'🎲 Seçim: **{secim}**')

    @commands.command(name='sunucuavatar')
    async def sunucuavatar(self, ctx):
        """Sunucunun avatarını gösterir."""
        if ctx.guild.icon:
            await ctx.send(ctx.guild.icon.url)
        else:
            await ctx.send('Sunucunun avatarı yok!')

    @commands.command(name='kullanıcıbilgi')
    async def kullanici_bilgi(self, ctx, member: discord.Member = None):
        """Kullanıcı hakkında bilgi verir."""
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.name} Kullanıcı Bilgisi", color=member.color)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Hesap Oluşturma", value=member.created_at.strftime('%d/%m/%Y'), inline=True)
        embed.add_field(name="Sunucuya Katılma", value=member.joined_at.strftime('%d/%m/%Y'), inline=True)
        embed.add_field(name="Roller", value=", ".join([r.mention for r in member.roles if r.name != '@everyone']), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='sunucubilgi')
    async def sunucu_bilgi(self, ctx):
        """Sunucu hakkında bilgi verir."""
        guild = ctx.guild
        embed = discord.Embed(title=f"{guild.name} Sunucu Bilgisi", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Sahip", value=guild.owner.mention, inline=True)
        embed.add_field(name="Üye Sayısı", value=guild.member_count, inline=True)
        embed.add_field(name="Kanal Sayısı", value=len(guild.channels), inline=True)
        embed.add_field(name="Rol Sayısı", value=len(guild.roles), inline=True)
        embed.add_field(name="Oluşturulma Tarihi", value=guild.created_at.strftime('%d/%m/%Y'), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='davet')
    async def davet(self, ctx):
        """Botun davet linkini gönderir."""
        client_id = (await self.bot.application_info()).id
        url = f'https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands'
        await ctx.send(f'🤖 Beni sunucuna eklemek için: {url}')

async def setup(bot):
    await bot.add_cog(Genel(bot)) 