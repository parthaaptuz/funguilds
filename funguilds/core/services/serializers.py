import pytz
from rest_framework import serializers
from datetime import datetime
from django.conf import settings
from core.authentication.models import Users
from .models import Tags, Guild, GuildManaged, GuildMembers, GameDetail, GuildAcceptance, GuildGames



class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags

class TagsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('tag_name',)


class GuildGamesSerializer(serializers.ModelSerializer):
    
    pk = serializers.SerializerMethodField('getPk')
    game_name = serializers.SerializerMethodField('getGameName')
    game_desc = serializers.SerializerMethodField('getGameDesc')
    tags = serializers.SerializerMethodField('getTags')
    profile_pic = serializers.SerializerMethodField('getProfilePic')

    def getPk(self, obj):
        return obj.game.pk

    def getGameName(self, obj):
        return obj.game.name

    def getGameDesc(self, obj):
        return obj.game.description

    def getProfilePic(self, obj):
        return obj.game.profile_pic

    def getTags(self, obj):
        tags = Tags.objects.filter(game = obj)
        output = []
        for tag in tags:
            output.append(tag.tag_name)
        return output



    class Meta:
        model = GuildGames
        fields = ('pk', 'game_name', 'game_desc', 'tags', 'profile_pic')

class GameDetailListSerializer(serializers.ModelSerializer):
    
    game_tags = TagsListSerializer(many = True, read_only = True)

    class Meta:
        model = GameDetail
        fields = ('id','name', 'description', 'created_by', 'game_tags', 'profile_pic')

class GameDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameDetail
        fields = ('name', 'description', 'profile_pic')
        



class GuildListSerializer(serializers.ModelSerializer):
    guild_tags = TagsSerializer(many=True, read_only = True)
    no_of_members = serializers.SerializerMethodField('get_members')
    no_of_active_members = serializers.SerializerMethodField('get_active_members')
    no_of_games = serializers.SerializerMethodField('get_games')

    def get_members(self,obj):
        members = GuildMembers.objects.filter(guild=obj.pk).count()
        return members

    def get_active_members(self,obj):
        #return 0
        actives = Users.objects.filter(pk__in=GuildMembers.objects.filter(guild=obj.pk).values_list('user',flat=True)).values_list('last_activity',flat=True)
        actives = [active for active in actives if active != None and active != '']
        if len(actives) > 0:
            pactives = 0
            now = datetime.utcnow().replace(tzinfo=pytz.UTC)
            for active in actives:
                diff = now-active
                if diff.seconds < settings.ACTIVE_TIME_DELTA:
                    pactives = pactives+1
            return pactives
        else:
            return 0

    def get_games(self,obj):
        games = GuildGames.objects.filter(guild=obj.pk).count()
        return games

    class Meta:
        model = Guild
        fields = ('pk','name', 'description', 'cover_pic', 'group_type', 'guild_tags', 'created_by', 'no_of_members', 'no_of_games', 'no_of_active_members')

class GuildDetailSerializer(serializers.ModelSerializer):
    guild_tags = TagsListSerializer(many=True, read_only = True)
    game_guild = GuildGamesSerializer(many = True, read_only = True)
    guild_members = serializers.SerializerMethodField('get_members')
    is_guild_admin = serializers.SerializerMethodField('isGuildAdmin')

    def get_members(self,obj):
        members = GuildMembers.objects.filter(guild=obj.pk)
        output = []
        for member in members:
            temp = {}
            temp['username'] = member.user.username
            temp['pk'] = member.user.pk
            temp['profile_pic'] = member.user.profile_pic
            output.append(temp)
        return output
    def isGuildAdmin(self, obj):
        if self.context['request'].user.is_authenticated():
            if self.context['request'].user == obj.created_by:
                return True
            else:
                return False
        else:
            return False


    class Meta:
        model = Guild
        fields = ('pk','name', 'description', 'cover_pic', 'group_type', 'guild_tags','game_guild','created_by','guild_members', 'is_guild_admin')


class GuildCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = ('name', 'description', 'cover_pic', 'group_type')
        

class GuildAcceptanceSerializer(serializers.ModelSerializer):
    requested_user = serializers.SerializerMethodField('get_userdata')

    def get_userdata(self,obj):
        temp = {}
        temp['username'] = obj.requested_from.username
        temp['pk'] = obj.requested_from.pk
        temp['profile_pic'] = obj.requested_from.profile_pic
        return temp

    class Meta:
        model = GuildAcceptance
        fields = ('id','guild','requested_from','status','requested_on', 'requested_user')

class GuildAcceptanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuildAcceptance
        fields = ('guild','status')

class GuildAcceptanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuildAcceptance
        fields = ('status',)