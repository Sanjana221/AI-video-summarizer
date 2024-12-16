from django.shortcuts import render,redirect
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import BlogPost
import json
import google.generativeai as genai
from .transcript import extract_transcript_details , generate_gemini_content , extract_title,to_html
from markupsafe import Markup
import markdown
# Create your views here.

def index(request):
    return render(request,"index.html")

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError,json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'},status = 400)
        
        
        #get title

        title = extract_title(yt_link)

        #get transcript

        transcript_text = extract_transcript_details(yt_link)
        #use open AI to generate blog

        if transcript_text:
            summary = generate_gemini_content(transcript_text)
            formatted = to_html(summary)
            content = Markup(formatted)
            if not summary:
                return JsonResponse({'error':'failed to generate summary'},status =500)
        else:
            return JsonResponse({'error':'failed to get transcript'},status = 500)
        #save blog artice to database
        new_blog_artice = BlogPost.objects.create(
            user= request.user,
            youtube_title= title,
            youtube_link= yt_link,
            generated_content = summary,
        )
        new_blog_artice.save()
        #return blog artice as a respose
        return JsonResponse({'content':content})
    else:
        return JsonResponse({'error': 'Invalid request method'},status = 405)
    
def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    formatted = []
    for article in blog_articles:
        article.generated_content = to_html(article.generated_content)
        formatted.append(article)
    return render(request,'blogs.html',{'blog_articles':formatted})

def blog_details(request,pk):
    md = markdown.Markdown(extensions=["fenced_code"])
    blog_article = BlogPost.objects.get(id=pk)
    if request.user == blog_article.user:
        blog_article.generated_content = md.convert(blog_article.generated_content)
        return render(request,'blog_details.html',{'blog_article':blog_article})
    else:
        redirect('/')

def delete_post(request,pk):
    post_to_delete = BlogPost.objects.get(id=pk)
    post_to_delete.delete()
    return redirect('/blog-list')

@login_required
def user_login(request):
    if request.method == 'POST':
        username= request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request,'login.html',{'error_message':error_message})
    return render(request,"login.html")

def user_signup(request):
    if request.method == 'POST':
        username=request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeat_password = request.POST['repeat-password']

        if password == repeat_password:
            try:
                user = User.objects.create_user(username,email,password)   
                user.save()
                login(request,user)
                return redirect('/')  
            except:
                error_message = 'Error creating account'
                return render(request,"signup.html")
        else:
            error_message = 'Password do not match'
            return render(request,'signup.html',{'error_message':error_message})
        
    return render(request,"signup.html")

def user_logout(request):
    logout(request)
    return redirect('/')

