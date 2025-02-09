from django.shortcuts import render,get_object_or_404,redirect
import video.views
# 지연 
from .models import Video,VComment
# 윤아
from .models import Upload
from .forms import UploadForm

from django.http import HttpResponse

from django.utils import timezone
from datetime import datetime
from django.utils.dateformat import DateFormat
from member.models import *

# 로그인 데코레이터
# from django.contrib.auth.decorators import login_required

## 장르별 영상 보여주기 : minjuhui
def search(request, genre):
    if genre==1: # 랩/힙합
        vs = Video.objects.filter(tags="1")
    if genre==2: # 발라드
        vs = Video.objects.filter(tags="2")
    if genre==3: # POP
        vs = Video.objects.filter(tags="3")
    if genre==4: # 여름
        vs = Video.objects.filter(tags="4")
    if genre==5: # 밤/새벽
        vs = Video.objects.filter(tags="5")
    if genre==6: # 청량한
        vs = Video.objects.filter(tags="6")
    if genre==7: # 신나는
        vs = Video.objects.filter(tags="7")
    return render(request,'videolist.html', {'vs':vs})

## 동영상 조회수 : minjuhui
def vhits(request, video_id):
    video_detail=get_object_or_404(Video, pk=video_id)
    if video_detail.vhits==None:
        video_detail.vhits=0
    Video.objects.filter(id=video_detail.pk).update(vhits=video_detail.vhits +1)
    return redirect('/video/vdetail/'+str(video_detail.id))

# 지연 : 비디오 재생 페이지를 로드
def videolist(request):
    videos=Video.objects 
    return render(request,'videolist.html',{'videos':videos})


# 지연 : 비디오 한개 보여주는 페이지 로드
def vdetail(request,video_id):
    videos=Video.objects 
    video_detail=get_object_or_404(Video,pk=video_id)
    vcomments=VComment.objects.filter(vpost=video_detail)
    vlikes=video_detail.likes.count()

    if vlikes is None:
        vlikes="a"

    # 색 바뀌도록   
    flag="ㅎㅎ"
    video=Video.objects.all()
    polldict={}
    user=request.user
    real=[]
    for poll in Video.objects.all():
        index=poll.title
        choicedict={}
            
        choicedict[index] = poll.likes.all()
        sedex=0
        for x in choicedict[index]:
            if x==user:
                flag=False
                real.append(index)
            else:
                flag=True
    
        polldict[index]=choicedict
            #print(polldict[index])
    
        # real이 진짜 좋아요를 누른 영상들
        # video객체를 가져 오겠다
    like_videos=[]
    for y in real:
        #like_videos.append(Video.objects.filter(title=y).values('video_key'))
        like_videos.append(Video.objects.filter(title=y))
    
    yyy=[]
    for ob in like_videos:
        for o in ob:
            for vo in video:
                if vo.title==o:
                    yyy.append(vo)
                else:
                    yyy.append(o)
    yyy = list(set(yyy))                
    
            #obs=Video.objects.filter(title=ob)
        #like_videos = Video.objects.filter(title="1")        
  
    return render(request,'vdetail.html',{'video':video_detail,'flag':flag,'vcomments':vcomments,'vlikes':vlikes})

# 지연 : 댓글 저장 기능만 하는 함수
def vcsave(request,video_id):
    videos=Video.objects
    video_detail=get_object_or_404(Video,pk=video_id)
    if request.method=="POST":
        vcomment=VComment()
        vcomment.vpost=video_detail
        vcomment.author = request.user.profile.nickname
        
        vcomment.text = request.POST['text']
        vcomment.save()

        vcomments=VComment.objects.filter(vpost=video_detail)
        return render(request,'vdetail.html',{'video':video_detail,'vcomments':vcomments})
        #return redirect('/video/vdetail',pk=video_id)
    else:
        return render(request, 'comment.html', {'form': form})
def post_like(request, pk):
    video_detail=get_object_or_404(Video,pk=pk)

    if request.method=="POST":
        vcomment=VComment()
        vcomment.vpost=video_detail
        vcomment.author = request.user.profile.nickname
        
        vcomment.text = request.POST['text']
        vcomment.save()

        vcomments=VComment.objects.filter(vpost=video_detail)
    # 포스트 정보 받아옴
    post = get_object_or_404(Video, pk=pk)

    # 사용자가 로그인 된건지 확인
    if not request.user.is_active:
        return redirect('vdetail',pk=pk, username=post.author, url=post.url)    

    # 사용자 정보 받아옴
    user = User.objects.get(username=request.user)
    # 좋아요에 사용자가 존재하면
    if post.likes.filter(id = user.id).exists():
        # 사용자를 지움
        
        post.likes.remove(user)
        flag=False
    else:
        # 아니면 사용자를 추가
        post.likes.add(user)
        flag=True
    vlikes=post.likes.count()
    if vlikes is None:
        vlikes="a"    
    # 포스트로 리디렉션
    return render(request,'vdetail.html',{'video':video_detail,'flag':flag,'vlikes':vlikes})
    #return redirect('vdetail',pk=pk, username=post.author, url=post.url)  

# 윤아
# 비디오 업로드 목록
def vread(request):
    uploads = Upload.objects.order_by('-id')
    up = uploads.filter(uname=request.user)
    if not up: ## 현재 로그인 한 유저가 올린 비디오가 없는 경우
        return render(request, 'vread.html', {'novd':'업로드한 동영상이 없습니다.'})
    else: ## 업로드 한 비디오가 있는 경우
        return render(request, 'vread.html',{'uploads':uploads})

# 비디오 업로드 폼 생성
def vcreate(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.pub_date = timezone.now()
            post.uname = request.user
            post.save()
            return redirect('vread')
    else:
        form = UploadForm()
        return render(request,'vcreate.html', {'form':form})

# 비디오 업로드 폼 수정
def vupdate(request, pk):
        upload = get_object_or_404(Upload, pk=pk)

        if request.method == "POST":
                form = UploadForm(request.POST, request.FILES, instance=upload) 

                if form.is_valid(): 
                        upload = form.save(commit=False) 
                        print(form.cleaned_data)
                        upload.utitle = form.cleaned_data['utitle']
                        upload.update_date=timezone.now()
                        # upload.uname = request.user
                        upload.ubody = form.cleaned_data['ubody']
                        upload.uvideo = form.cleaned_data['uvideo'] 
                        upload.save()
                        return redirect('vread') 

        else:
                form = UploadForm(instance=upload) 
                return render(request, 'vupdate.html',{'form' : form})

# 비디오 업로드 삭제
def vdelete(request, pk):
    upload = Upload.objects.get(id=pk)
    upload.delete()
    return redirect('vread')
    
# 비디오 업르드 자세히
def udetail(request, upload_id):
    upload = get_object_or_404(Upload, pk=upload_id)
    return render(request,'udetail.html',{'upload':upload})

