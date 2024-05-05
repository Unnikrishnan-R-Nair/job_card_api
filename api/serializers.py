from rest_framework import serializers

from .models import JobCard, Job

from django.contrib.auth.models import User


class AdminSerializer(serializers.ModelSerializer):

    password1=serializers.CharField(write_only=True)
    password2=serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields=["username", "email", "password1", "password2", "password"]

        read_only_fields=["password"]

    def create(self, validated_data):

        password1=validated_data.pop("password1")
        password2=validated_data.pop("password2")

        if password1!=password2:
            raise serializers.ValidationError("passwords don't match!!!")
        
        return User.objects.create_superuser(**validated_data, password=password1)

class UserSerializer(serializers.ModelSerializer):

    password1=serializers.CharField(write_only=True)
    password2=serializers.CharField(write_only=True)

    class Meta:

        model=User
        fields=["username", "email", "first_name", "last_name", "password1", "password2", "password"]

        read_only_fields = ["password"]

    def create(self, validated_data):

        # print(validated_data)
        password1 = validated_data.pop("password1")
        password2 = validated_data.pop("password2")

        if password1 != password2:

            raise serializers.ValidationError("Passwords don't match!!!")

        return User.objects.create_user(**validated_data, password=password1)
    
    
class AdvisorSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=["first_name","last_name", "username", "is_active"]



class JobCardSerializer(serializers.ModelSerializer):

    advisor=serializers.StringRelatedField()

    class Meta:

        model=JobCard
        exclude=('is_active',)

        read_only_fields=["id", "advisor"]

class JobSerializer(serializers.ModelSerializer):

    advisor=serializers.StringRelatedField()
    
    class Meta:

        model=Job
        fields=["id", 
                "job_card_object", 
                "advisor", 
                "title", 
                "description",
                "amount",
                "created_date",
                "updated_date",
                ]
        read_only_fields=["id", "advisor", "job_card_object"]


class JobSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model=Job
        fields=["id", "title", "description", "amount"]

class JobCardSummarySerializer(serializers.ModelSerializer):

    pass

    
    
    
