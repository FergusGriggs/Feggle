import pygame, sys, math, time, os, random, pygame.midi
from pygame.locals import *


screenW=1100
screenH=1000
screen=pygame.display.set_mode((screenW,screenH))
pygame.display.set_caption('ball line physics')
pygame.init()



fontPath="Fonts/pixeled.ttf"

maxBalls=10
availableBalls=maxBalls
canFire=True

multiplier=0
shotScore=0
feverMode=False
score=0

shotAngle=-math.pi/2
shotPoint=(screenW/2,200)

gameState="intro"

valToIncrease=0
scoreIncrement=0

gravity=0.2

fontsize=25
scoreTextSize=0

greenPegNum=2
redPegNum=20
purplePegNum=1

ballSize=10

redNum=redPegNum

abilities=["explode","multiball","rayshot"]
ability=abilities[random.randint(0,len(abilities)-1)]
specialShots=0
pegMultiplier=1

decayPegDelay=0
decaySpeed=0

polys=[]
boxes=[]
pegs=[]
polyPegs=[]
regions=[]
pegsToRemove=[]
textFloaters=[]
messages=[]
sounds=[]
effects=[]
balls=[]

music = True
explosionStrings=["BOOM!","KAPOW!","KABOOM!"]
multiballStrings=["Multiball!","Another one!","Have another!"]
rayshotStrings=["+1 Ray shot ball!","Ray shot on next ball!","Reeeeeeeee shot!"]
messageDelay=1000
songs=[["Music/Dreamy Flashback.mp3",0.5],["Music/Happy Bee.mp3",0.35]]

SONG_END = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(SONG_END)

if music:
   rnum=random.randint(0,len(songs)-1)
   pygame.mixer.music.load(songs[rnum][0])
   pygame.mixer.music.set_volume(songs[rnum][1])
   pygame.mixer.music.play()
pygame.midi.init()
player = pygame.midi.Output(0)

#98,108,114 for hits
#126 for applause
scoreFont=pygame.font.Font(fontPath,fontsize)
shotFont=pygame.font.Font(fontPath,fontsize-15)
def updateSounds():
   global sounds
   for sound in sounds:
      sound.tick+=deltaTime
      if sound.tick>sound.duration:
         sound.stop()
def stopSounds():
   for sound in sounds:
      sound.stop()
def drawNextShot():
   points=[]
   pos=(shotPoint[0]-math.cos(shotAngle)*40,shotPoint[1]-math.sin(shotAngle)*40)
   vel=(-math.cos(shotAngle)*10,-math.sin(shotAngle)*10)
   for i in range(20):
      for peg in pegs:
         if distance(peg.pos,pos)<10+peg.size:
            speed=math.sqrt((vel[0])**2+(vel[1])**2)
            angle=math.atan2(pos[1]-peg.pos[1],pos[0]-peg.pos[0])
            vel=(math.cos(angle)*speed*peg.bounce,math.sin(angle)*speed*peg.bounce)
      vel=(vel[0]*0.997,vel[1]*0.997+gravity)
      pos=(pos[0]+vel[0],pos[1]+vel[1])
      points.append(pos)
   pygame.draw.lines(screen,(0,0,0),False,points,2)
class pegDisappear():
   def __init__(self,pos,size,colour):
      global effects
      self.pos=pos
      self.size=size/2
      self.targetSize=size*1.3
      self.colour=colour
      self.tick=0
      effects.append(self)
   def update(self):
      self.size=self.size+(self.targetSize-self.size)/5
      if self.size>self.targetSize-1 and self.size<self.targetSize+1:
         self.targetSize=0
      self.tick+=deltaTime
      if self.tick>400:
         effects.remove(self)
   def draw(self):
      pygame.draw.circle(screen,self.colour,(int(self.pos[0]),int(self.pos[1])),int(self.size),0)
def updateEffects():
   for effect in effects:
      effect.update()
def drawEffects():
   for effect in effects:
      effect.draw()  
def handleShots():
   global canFire, shotAngle, multiplier, shotScore, score, gameState, availableBalls, pegsToRemove, messageDelay, pegMultiplier, specialShots, decayOldPegs, decayPegIndex, decayPegDelay, decaySpeed
   if len(balls)==0 and not canFire:
      if feverMode:
         shotScore+=10000*availableBalls
         textFloater((screenW-120,175),1000,(255,255,0),(-2,0),fontsize-10,"10,000 x"+str(availableBalls),fontPath)
         availableBalls=0
      pegMultiplier=1
      if not pygame.mouse.get_pressed()[0]:
         canFire=True
      if shotScore!=0:
         addToMainScore(multiplier*shotScore)
         sound(124,60,500)
      shotScore=0
      multiplier=0
      decayOldPegs=True
      decayPegIndex=0
      if multiplier>0:
         decaySpeed=1000/multiplier
         if decaySpeed<4:
            decaySpeed=4
   if decayOldPegs:
      if len(pegsToRemove)>0:
         if decayPegDelay<0:
            decayPegDelay+=decaySpeed
            pegDisappear(pegsToRemove[decayPegIndex].pos,pegsToRemove[decayPegIndex].size,(255,255,255))
            if pegsToRemove[decayPegIndex] in pegs:
               pegs.remove(pegsToRemove[decayPegIndex])
            decayPegIndex+=1
            if decayPegIndex>len(pegsToRemove)-1:
               decayOldPegs=False
               pegsToRemove=[]
         else:
            decayPegDelay-=deltaTime
      else:
         decayOldPegs=False
   if len(balls)==0:
      if availableBalls<=0:
         if messageDelay==0:
            message(":(",["What a shame, looks like you're","out of balls. You scored ","{:,}".format(score)+" points!"],"Retry","Quit :(")
            gameState="over"
            messageDelay=1000
            sound(126,64,3000)
         else:
            messageDelay-=deltaTime
            if messageDelay<0:
               messageDelay=0
   m=pygame.mouse.get_pos()
   shotAngle=math.atan2(shotPoint[1]-m[1],shotPoint[0]-m[0])
   if shotAngle>0 and shotAngle<=math.pi/2:
      shotAngle=0
   if shotAngle>math.pi/2 and shotAngle<math.pi:
      shotAngle=math.pi
   shotAngle=rotate(rotate(shotAngle,math.pi/2)*1.2,-math.pi/2)
   if canFire and availableBalls>0:
      if pygame.mouse.get_pressed()[0]:
         canFire=False
         sound(115,40,1000)
         availableBalls-=1
         if availableBalls<0:
            availableBalls=0
         startPoint=(shotPoint[0]-math.cos(shotAngle)*40,shotPoint[1]-math.sin(shotAngle)*40)
         vel=(-math.cos(shotAngle)*10,-math.sin(shotAngle)*10)
         if specialShots>0:
            specialShots-=1
            balls.append(ball(startPoint,vel,ability))
         else:
            balls.append(ball(startPoint,vel,"none"))
def drawCannon():
   pygame.draw.rect(screen,(80,80,80),Rect(shotPoint[0]-15,150,30,50),0)
   pygame.draw.polygon(screen,(80,80,80),[(shotPoint[0]-math.cos(shotAngle+math.pi/2)*15,shotPoint[1]-math.sin(shotAngle+math.pi/2)*15),
                                          (shotPoint[0]+math.cos(shotAngle+math.pi/2)*15,shotPoint[1]+math.sin(shotAngle+math.pi/2)*15),
                                          (shotPoint[0]+math.cos(shotAngle+math.pi/2)*15-math.cos(shotAngle)*50,shotPoint[1]+math.sin(shotAngle+math.pi/2)*15-math.sin(shotAngle)*50),
                                          (shotPoint[0]-math.cos(shotAngle+math.pi/2)*15-math.cos(shotAngle)*50,shotPoint[1]-math.sin(shotAngle+math.pi/2)*15-math.sin(shotAngle)*50),],0)
   pygame.draw.circle(screen,(130,130,130),(int(shotPoint[0]),int(shotPoint[1])),30,0)
class sound():
   def __init__(self,instrument,pitch,duration):
      global sounds
      self.instrument=instrument
      self.pitch=pitch
      self.duration=duration
      self.tick=0
      player.set_instrument(instrument,1)
      player.note_on(pitch,127,1)
      sounds.append(self)
   def stop(self):
      player.set_instrument(self.instrument,1)
      player.note_off(self.pitch,127,1)
      sounds.remove(self)
class ball():
   def __init__(self,pos,vel,effect):
      self.pos=pos
      self.vel=vel
      self.size=ballSize
      self.angle=0
      self.effect=effect
      self.oldcount=0
      self.colour=(70,70,70)
      self.lastContactPos=pos
   def update(self):
      global balls, pegs
      self.oldpos=self.pos
      self.vel=(self.vel[0]*0.997,self.vel[1]*0.997+gravity)
      self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1])
      self.angle=math.atan2(self.vel[1],self.vel[0])
      for i in range(len(polys)):
         if polys[i].active:
            intersectData=ballIntersect(self.pos,self.size,polys[i].points,polys[i].bounce,self)
            if intersectData[0]:
               self.pos=(self.pos[0]-self.vel[0],self.pos[1]-self.vel[1])
               speed=math.sqrt((self.vel[0])**2+(self.vel[1])**2)
               if intersectData[2]:
                  if speed<0.1:
                     intersectData[3]=1
                  self.vel=(math.cos(intersectData[1])*speed*intersectData[3],math.sin(intersectData[1])*speed*intersectData[3])
               else:
                  diff=intersectData[1]-self.angle
                  self.angle=intersectData[1]+diff
                  self.vel=(math.cos(self.angle)*speed*intersectData[3],math.sin(self.angle)*speed*intersectData[3])
      if self.oldpos==self.pos:
         self.oldcount+=1
         if self.oldcount>40:
            toRemove=[]
            for peg in pegs:
               if distance(peg.pos,self.pos)<peg.size+self.size+4:
                  toRemove.append(peg)
                  break
            if len(toRemove)>0:
               for item in toRemove:
                  pegs.remove(item)
         if self.oldcount>50:
            balls.remove(self)
      else:
         self.oldcount=0
   def draw(self):
      if self.effect=="rayshot":col=(255,0,0)
      else:col=self.colour
      pygame.draw.circle(screen,col,(int(self.pos[0]),int(self.pos[1])),self.size,0)
class message():
   def __init__(self,head,lines,button1Text,button2Text):
      self.head=head
      self.button1Text=pygame.font.Font(fontPath,fontsize-12).render(str(button1Text),False,(80,80,80))
      self.button2Text=pygame.font.Font(fontPath,fontsize-12).render(str(button2Text),False,(80,80,80))
      self.button1col=(190,190,190)
      self.button2col=(190,190,190)
      self.button1Rect=Rect(screenW/2-190,screenH/2+50,185,50)
      self.button2Rect=Rect(screenW/2+5,screenH/2+50,185,50)
      self.headText=pygame.font.Font(fontPath,fontsize-5).render(str(head),False,(190,190,190))
      self.lines=[pygame.font.Font(fontPath,fontsize-12).render(str(lines[i]),False,(190,190,190)) for i in range(3)]
      messages.append(self)
   def draw(self):
      pygame.draw.rect(screen,(80,80,80),Rect(screenW/2-210,screenH/2-120,420,240),0)
      pygame.draw.rect(screen,(190,190,190),Rect(screenW/2-200,screenH/2-110,400,220),5)
      pygame.draw.rect(screen,self.button1col,self.button1Rect,0)
      pygame.draw.rect(screen,self.button2col,self.button2Rect,0)
      screen.blit(self.button1Text,(screenW/2-100-self.button1Text.get_width()/2,screenH/2+70-self.button1Text.get_height()/2))
      screen.blit(self.button2Text,(screenW/2+100-self.button2Text.get_width()/2,screenH/2+70-self.button2Text.get_height()/2))
      screen.blit(self.headText,(screenW/2-self.headText.get_width()/2,screenH/2-90-self.headText.get_height()/2))
      for i in range(3):
         screen.blit(self.lines[i],(screenW/2-self.lines[i].get_width()/2,screenH/2-60+30*i))
class polyPeg():
   def __init__(self,pos,angle,curveAmt,resolution):
      self.pos=pos
      self.cornerPoints=[(pos[0]-math.cos(angle)*20+math.cos(angle+math.pi/2)*10,pos[1]-math.sin(angle)*20+math.sin(angle+math.pi/2)*10),
                      (pos[0]+math.cos(angle)*20+math.cos(angle+math.pi/2)*10,pos[1]+math.sin(angle)*20+math.sin(angle+math.pi/2)*10),
                      (pos[0]+math.cos(angle)*20-math.cos(angle+math.pi/2)*10,pos[1]+math.sin(angle)*20-math.sin(angle+math.pi/2)*10),
                      (pos[0]-math.cos(angle)*20-math.cos(angle+math.pi/2)*10,pos[1]-math.sin(angle)*20-math.sin(angle+math.pi/2)*10)]
      self.poly=poly([self.cornerPoints[0],self.cornerPoints[1],self.cornerPoints[2],self.cornerPoints[3],self.cornerPoints[0]],1,False,True,(10,10,235),False)
      self.colour=(10,10,235)
      self.midColour=adjustCol(self.colour,1.4)
      polyPegs.append(self)
   def draw(self):
      pygame.draw.polygon(screen,self.colour,self.cornerPoints,0)
      
class peg():
   def __init__(self,pos):
      self.pos=pos
      self.special=False
      self.specialUsed=False
      self.active=True
      self.colour=(10,10,235)
      self.score=100
      self.midColour=adjustCol(self.colour,1.4)
      self.size=12
      self.bounce=1
      self.multiply=1
      self.target=False
      pegs.append(self)
   def hit(self):
      global shotScore, multiplier, specialShots, pegMultiplier, redNum, feverMode, buckets, bucket1, bucket2, bucket3, bucket4, bucket5
      self.active=False
      shotScore+=self.score*pegMultiplier
      multiplier+=1
      if self.multiply>1:
         pegMultiplier*=self.multiply
      self.bounce=0.65
      if self.target:
         redNum-=1
      if redNum==0:
         if not feverMode:
            textFloater((self.pos[0],self.pos[1]-60),1000,(230,230,10),(0,random.randint(-20,-10)/10),fontsize-10,"Extreme Fever!",fontPath)
            feverMode=True
            pegMultiplier=10
         bucketRegion.active=False
         bucketPoly.active=False
         buckets.active=True
         buckets.visible=False
         bucket1.active=True
         bucket2.active=True
         bucket3.active=True
         bucket4.active=True
         bucket5.active=True
         
      if self.score==1000:size=25
      else:size=20
      if self.special and not self.specialUsed:
         self.specialUsed=True
         if ability=="explode":
            for peg in pegs:
               if peg != self:
                  if peg.active:
                     if distance(peg.pos,self.pos)<120:
                        peg.hit()
            abilityString=explosionStrings[random.randint(0,len(explosionStrings)-1)]
         if ability=="multiball":
            colliding=True
            angle=random.random()*math.pi*2-math.pi
            while colliding:
               angle=rotate(angle,0.001)       
               pos=(self.pos[0]+math.cos(angle)*self.size*4,self.pos[1]+math.sin(angle)*self.size*4)
               colliding=False
               for peg in pegs:
                  if distance(pos,peg.pos)<ballSize+self.size:
                     colliding=True
            balls.append(ball((pos[0],pos[1]),(math.cos(angle)*5,math.sin(angle)*5),"none"))
            abilityString=multiballStrings[random.randint(0,len(multiballStrings)-1)]
            sound(97,64,500)
         if ability=="rayshot":
            abilityString=rayshotStrings[random.randint(0,len(rayshotStrings)-1)]
            specialShots+=1
            sound(97,64,500)
         textFloater((self.pos[0],self.pos[1]-20),1000,self.colour,(0,random.randint(-20,-10)/10),fontsize-(35-size),abilityString,fontPath)
      elif self.multiply>1:
         textFloater((self.pos[0],self.pos[1]-20),1000,self.colour,(0,random.randint(-20,-10)/10),fontsize-(35-size),"Pin points x10",fontPath)
         sound(114,64,1000)
      else:
         pitch=multiplier+40
         if pitch>80:
            pitch=80
         sound(11,pitch,200)
         if feverMode:col=(255,255,0)
         else:col=self.colour
         textFloater((self.pos[0],self.pos[1]-20),1000,col,(0,random.randint(-20,-10)/10),fontsize-(35-size),"{:,}".format(self.score*pegMultiplier),fontPath)
      self.colour=adjustCol(self.colour,0.7)
      self.midColour=adjustCol(self.midColour,0.5)
      pegsToRemove.append(self)
   def draw(self):
      pygame.draw.circle(screen,self.colour,(int(self.pos[0]),int(self.pos[1])),self.size,0)
      pygame.draw.circle(screen,self.midColour,(int(self.pos[0]),int(self.pos[1])),int(self.size/1.5),0)
class poly():
   def __init__(self,points,bounce,fixed,active,colour,visible):
      global polys
      self.points=points
      self.colour=colour
      self.bounce=bounce
      self.fixed=fixed
      self.active=active
      self.visible=visible
      polys.append(self)
   def draw(self):
      if self.active:
         if self.visible:
            pygame.draw.lines(screen,self.colour,False,self.points,2)
class region():
   def __init__(self,rect,score,ballAction,active):
      self.rect=rect
      self.score=score
      self.ballAction=ballAction
      self.active=active
      regions.append(self)
   def draw(self):
      if self.active:
         pygame.draw.rect(screen,(255,0,0),self.rect,1)
class textFloater():
   def __init__(self,pos,life,colour,vel,size,text,font):
      self.textImage=pygame.font.Font(font,size).render(text,False,colour)
      self.pos=(pos[0]-self.textImage.get_width()/2,pos[1]-self.textImage.get_height()/2)
      self.life=life
      self.vel=vel
      textFloaters.append(self)
   def update(self):
      self.vel=(self.vel[0]*0.98,self.vel[1]*0.9)
      self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1])
      self.life-=deltaTime
      if self.life<0:
         textFloaters.remove(self)
   def draw(self):
      screen.blit(self.textImage,self.pos)
  
def rotate(angle,val):
   angle+=val
   if angle<-math.pi:
      angle=math.pi-(abs(angle)-math.pi)
   elif angle>math.pi:
      angle=-math.pi+(angle-math.pi)
   return angle
def ballIntersect(pos,radius,points,bounce,ball):
   global multiplier
   circleInPoly=False
   polyInCircle=False
   pegHit=False
   cps=[closestpointonline(points[i-1],points[i],pos) for i in range(1,len(points))]
   for i in range(len(cps)):
      if distance(pos,cps[i])<radius:
         circleInPoly=True
         angle=math.atan2(points[i+1][1]-points[i][1],points[i+1][0]-points[i][0])
         ball.lastContactPos=pos
   for i in range(len(points)):
      if distance(pos,points[i])<radius:
         if not circleInPoly:
            angle=math.atan2(pos[1]-points[i][1],pos[0]-points[i][0])
         polyInCircle=True
         ball.lastContactPos=pos
   for peg in pegs:
      if ball.effect=="rayshot":
         if distance(peg.pos,pos)<70:
            if peg.active:
               peg.hit()
      else:
         if distance(peg.pos,pos)<peg.size+radius:
            angle=math.atan2(pos[1]-peg.pos[1],pos[0]-peg.pos[0])
            bounce=peg.bounce
            if peg.active:
               if multiplier>0:
                  if distance(peg.pos,ball.lastContactPos)>300:
                     multiplier*=2
                     textFloater((peg.pos[0],peg.pos[1]-40),1000,(225,255,0),(0,random.randint(-20,-10)/10),fontsize-15,"Longshot! Mult x2",fontPath)
               peg.hit()
            ball.lastContactPos=peg.pos
            pegHit=True
   if circleInPoly:
      return [1,angle,0,bounce]
   elif polyInCircle or pegHit:
      return [1,angle,1,bounce]
   return[0]
def distance(p1,p2):
   return math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)
def closestpointonline(p1, p2, cp): 
      A1 = p2[1] - p1[1]
      B1 = p1[0] - p2[0]
      C1 = (p2[1] - p1[1])*p1[0] + (p1[0] - p2[0])*p1[1]
      C2 = -B1*cp[0] + A1*cp[1]
      det = A1*A1 - -B1*B1
      cx = 0 
      cy = 0
      if det != 0:
          cx = ((A1*C1 - B1*C2)/det)
          cy = ((A1*C2 + B1*C1)/det)
      else:
          cx = cp[0]
          cy = cp[1]
      lx=min(p1[0],p2[0])
      if cx >= lx:
         mx=max(p1[0],p2[0])
         if cx <= mx:
            ly=min(p1[1],p2[1])
            if cy >= ly:
               my=max(p1[1],p2[1])
               if cy <= my:
                  return (cx, cy)
      return (-10000,-10000)
def updateBalls():
   for ball in balls:
      ball.update()
def drawBalls():
   for ball in balls:
      ball.draw()
def drawPolys():
   for poly in polys:
      poly.draw()
def drawPegs():
   for peg in pegs:
      peg.draw()
def drawRegions():
   for region in regions:
      region.draw()
def checkRegions():
   global shotScore, balls, availableBalls, multiplier
   toRemove=[]
   for ball in balls:
      for region in regions:
         if region.active:
            if region.rect.collidepoint(ball.pos):
               if region.ballAction=="destroy":
                  toRemove.append(ball)
               elif region.ballAction=="win":
                  shotScore+=region.score
                  textFloater((region.rect.centerx,ball.pos[1]-40),1000,(235,235,10),(0,-10),fontsize+5,"+"+str(region.score),fontPath)
                  toRemove.append(ball)
               elif region.ballAction=="freeball":
                  availableBalls+=1
                  multiplier+=5
                  textFloater((ball.pos[0],ball.pos[1]-30),1000,(235,235,10),(math.sin(bucketSinVal)*305-math.sin(bucketSinVal-0.015)*305,-7),fontsize-10,"Free Ball!",fontPath)
                  sound(53,64,1000)
                  toRemove.append(ball)
   for ball in toRemove:
      balls.remove(ball)
def drawTextFloaters():
   for floater in textFloaters:
      floater.draw()
def updateTextFloaters():
   for floater in textFloaters:
      floater.update()
region(Rect(0,screenH,screenW,200),0,"destroy",True)
bucket1=region(Rect(120,880,40,40),10000,"win",False)
bucket2=region(Rect(300,880,40,40),25000,"win",False)
bucket3=region(Rect(480,880,40,40),50000,"win",False)
bucket4=region(Rect(660,880,40,40),25000,"win",False)
bucket5=region(Rect(840,880,40,40),10000,"win",False)
poly([(50,screenW),(50,150),(screenW-50,150),(screenW-50,screenH)],0.8,True,True,(0,0,0),False)
buckets=poly([(45,screenH),(45,800),
      (85,815),(120,850),(120,920),(160,920),(160,850),(195,815),(230,800),
      (265,815),(300,850),(300,920),(340,920),(340,850),(375,815),(410,800),
      (445,815),(480,850),(480,920),(520,920),(520,850),(555,815),(590,800),
      (625,815),(660,850),(660,920),(700,920),(700,850),(735,815),(770,800),
      (805,815),(840,850),(840,920),(880,920),(880,850),(915,815),(955,800),(955,screenH)
      ],0.8,True,False,(0,0,0),True)#end screen poly
scale=screenW/1000
bucket1.rect.left*=scale;bucket1.rect.width*=scale
bucket2.rect.left*=scale;bucket2.rect.width*=scale
bucket3.rect.left*=scale;bucket3.rect.width*=scale
bucket4.rect.left*=scale;bucket4.rect.width*=scale
bucket5.rect.left*=scale;bucket5.rect.width*=scale
for i in range(len(buckets.points)):
   buckets.points[i]=(buckets.points[i][0]*scale,buckets.points[i][1])
bucketPoly=poly([(400,850),(400,900),(600,900),(600,850)],1.0,True,True,(0,0,0),False)
bucketRegion=region(Rect(400,860,200,40),0,"freeball",True)
bucketSinVal=0
def updateBucket():
   global bucketPoly, bucketRegion, bucketSinVal
   bucketSinVal+=0.015
   if not feverMode:
      bucketPoly.points=[(screenW/2-100+math.sin(bucketSinVal)*305,850),
                         (screenW/2-140+math.sin(bucketSinVal)*305,900),
                         (screenW/2+140+math.sin(bucketSinVal)*305,900),
                         (screenW/2+100+math.sin(bucketSinVal)*305,850)]
      bucketRegion.rect.left=screenW/2-100+math.sin(bucketSinVal)*305
def drawBucketTop():
   pygame.draw.polygon(screen,(80,80,80),[bucketPoly.points[0],bucketPoly.points[1],(bucketPoly.points[1][0]+30,bucketPoly.points[1][1]+30),(bucketPoly.points[2][0]-30,bucketPoly.points[2][1]+30),bucketPoly.points[2],bucketPoly.points[3],(bucketPoly.points[0][0]+100,bucketPoly.points[0][1]+25)],0)
def drawUI():
   pygame.draw.polygon(screen,(80,80,80),[(0,0),(screenW,0),(screenW,screenH),(screenW-50,screenH),(screenW-50,150),(50,150),(50,screenH),(0,screenH)],0)
def adjustCol(col,val):
   col=[col[0]*val,col[1]*val,col[2]*val]
   for i in range(len(col)):
      if col[i]>255:
         col[i]=255
   return tuple(col)
def drawScore():
   font=pygame.font.Font(fontPath,fontsize+scoreTextSize)
   t1=scoreFont.render("TOTAL: ",False,(190,190,190))
   t2=font.render("{:,}".format(score),False,(190+65*(scoreTextSize/30),190+65*(scoreTextSize/30),190-190*(scoreTextSize/30)))
   screen.blit(t1,(50,60-t1.get_height()/2))
   screen.blit(t2,(200,95-t2.get_height()))
def drawShotScore():
   text=scoreFont.render("CURRENT: "+"{:,}".format(shotScore)+" x"+"{:,}".format(multiplier),False,(190,190,190))
   screen.blit(text,(50,100-text.get_height()/2))
def drawPowerUp():
   text=scoreFont.render("ABIL: "+ability.upper(),False,(190,190,190))
   screen.blit(text,(screenW-450,60-text.get_height()/2))
def drawAvailableBalls():
   if availableBalls<10:
      string="0"+str(availableBalls)
   else:
      string=str(availableBalls)
   text=scoreFont.render(string,False,(190,190,190))
   screen.blit(text,(screenW-50-text.get_width(),60-text.get_height()/2))
   for i in range(maxBalls):
      if i>=availableBalls:col=(30,30,30)
      elif i >=availableBalls-specialShots:col=(255,0,0)
      else:col=(190,190,190)
      pygame.draw.circle(screen,col,(screenW-70-i*41,110),20,0)
def addToMainScore(val):
   global valToIncrease, scoreIncrement, scoreTextSize
   scoreTextSize=30
   valToIncrease+=val
   scoreIncrement=int(valToIncrease/50)
def updateMainScore():
   global score, valToIncrease, scoreTextSize
   if valToIncrease>0:
      score+=scoreIncrement
      valToIncrease-=scoreIncrement
   if scoreTextSize>0:
      scoreTextSize-=1
def handleMessages():
   global canFire, gameState
   for message in messages:
      message.draw()
      if gameState=="over":
         if message.button1Rect.collidepoint(pygame.mouse.get_pos()):
            message.button1col=(210,210,210)
            if pygame.mouse.get_pressed()[0]:
               restartMap()
               sound(115,80,1000)
         else:message.button1col=(190,190,190)
         if message.button2Rect.collidepoint(pygame.mouse.get_pos()):
            message.button2col=(210,210,210)
            if pygame.mouse.get_pressed()[0]:
               stopSounds()
               pygame.quit()
               sys.exit()
         else:message.button2col=(190,190,190)
      else:
         if message.button1Rect.collidepoint(pygame.mouse.get_pos()):
            message.button1col=(210,210,210)
            if pygame.mouse.get_pressed()[0]:
               messages.remove(message)
               canFire=False
               gameState="playing"
               sound(115,80,1000)
         else:message.button1col=(190,190,190)
         if message.button2Rect.collidepoint(pygame.mouse.get_pos()):
            message.button2col=(210,210,210)
            if pygame.mouse.get_pressed()[0]:
               stopSounds()
               pygame.quit()
               sys.exit()
         else:message.button2col=(190,190,190)
clock=pygame.time.Clock()
def restartMap():
   global score, shotScore, multiplier, balls, pegs, availableBalls, messages, gameState, canFire, bucketSinVal, ability, redNum, feverMode
   availableBalls=maxBalls
   score=0
   shotScore=0
   multiplier=0
   balls=[]
   messages=[]
   gameState="playing"
   canFire=False
   createPegs(random.randint(0,1))
   bucketSinVal=0
   ability=abilities[random.randint(0,len(abilities)-1)]
   redNum=redPegNum
   feverMode=False
   bucketRegion.active=True
   bucketPoly.active=True
   buckets.active=False
   bucket1.active=False
   bucket2.active=False
   bucket3.active=False
   bucket4.active=False
   bucket5.active=False
def createPegs(mapID):
   global pegs
   pegs=[]
   if mapID==0:
      for i in range(9):
         for j in range((i%2)+12):
            peg((160-(i%2)*35+j*70,400+i*40))
   elif mapID==1:
      for i in range(-20,21):
         peg((screenW/2+math.cos(i/10+math.pi/2)*350,screenH/2-50+math.sin(i/10+math.pi/2)*300))
      for i in range(-20,21):
         peg((screenW/2+math.cos(i/10+math.pi/2)*280,screenH/2-50+math.sin(i/10+math.pi/2)*230))
      for i in range(-20,21):
         peg((screenW/2+math.cos(i/10+math.pi/2)*210,screenH/2-50+math.sin(i/10+math.pi/2)*160))
   rnums=[]
   for i in range(redPegNum):
      rnum=random.randint(0,len(pegs)-1)
      while rnum in rnums:
         rnum=random.randint(0,len(pegs)-1)
      rnums.append(rnum)
      pegs[rnum].colour=(235,64,10)
      pegs[rnum].score=1000
      pegs[rnum].midColour=adjustCol(pegs[rnum].colour,1.4)
      pegs[rnum].target=True
   for i in range(greenPegNum):
      rnum=random.randint(0,len(pegs)-1)
      while rnum in rnums:
         rnum=random.randint(0,len(pegs)-1)
      rnums.append(rnum)
      pegs[rnum].colour=(75,235,10)
      pegs[rnum].score=1000
      pegs[rnum].midColour=adjustCol(pegs[rnum].colour,1.4)
      pegs[rnum].special=True
   for i in range(purplePegNum):
      rnum=random.randint(0,len(pegs)-1)
      while rnum in rnums:
         rnum=random.randint(0,len(pegs)-1)
      rnums.append(rnum)
      pegs[rnum].colour=(230,64,230)
      pegs[rnum].midColour=adjustCol(pegs[rnum].colour,1.4)
      pegs[rnum].score=1000
      pegs[rnum].multiply=10
def drawBucketValues():
   font=pygame.font.Font(fontPath,fontsize-15)
   t1=font.render("{:,}".format(bucket1.score),False,(80,80,80))
   t2=font.render("{:,}".format(bucket2.score),False,(80,80,80))
   t3=font.render("{:,}".format(bucket3.score),False,(80,80,80))
   t4=font.render("{:,}".format(bucket4.score),False,(80,80,80))
   t5=font.render("{:,}".format(bucket5.score),False,(80,80,80))
   screen.blit(t1,(screenW/2-t1.get_width()/2-screenW*0.36,screenH-1.6*screenH/10-t1.get_height()/2))
   screen.blit(t2,(screenW/2-t2.get_width()/2-screenW*0.18,screenH-1.6*screenH/10-t2.get_height()/2))
   screen.blit(t3,(screenW/2-t3.get_width()/2,screenH-1.6*screenH/10-t3.get_height()/2))
   screen.blit(t4,(screenW/2-t4.get_width()/2+screenW*0.18,screenH-1.6*screenH/10-t4.get_height()/2))
   screen.blit(t5,(screenW/2-t5.get_width()/2+screenW*0.36,screenH-1.6*screenH/10-t5.get_height()/2))
createPegs(random.randint(0,1))
message("Welcome to Feggle!",["The newest hit game","by mr Fergus Griggs.","Check it out?"],"um, sure","i have autismo")
def drawPolyPegs():
   for polyPeg in polyPegs:
      polyPeg.draw()
while 1:
   updateSounds()
   deltaTime=clock.tick()*4
   updateBucket()
   updateTextFloaters()
   updateMainScore()
   checkRegions()
   updateBalls()
   updateEffects()
   if gameState=="playing":
      handleShots()
   screen.fill((190,190,190))
   if feverMode:
      drawBucketValues()
   drawNextShot()
   drawPolys()
   drawBalls()
   drawPegs()
   drawPolyPegs()
   drawTextFloaters()
   if not feverMode:   
      drawBucketTop()
   else:
      pygame.draw.polygon(screen,(80,80,80),buckets.points,0)
      pygame.draw.rect(screen,(80,80,80),Rect(0,screenH-1.05*screenH/10,screenW,screenH/10),0)
   drawCannon()
   drawEffects()
   drawUI()
   drawScore()
   drawShotScore()
   drawPowerUp()
   #drawRegions()
   drawAvailableBalls()
   handleMessages()
   for event in pygame.event.get():
       if event.type==QUIT:
          stopSounds()
          pygame.quit()
          sys.exit()
       if event.type==SONG_END:
          rnum=random.randint(0,len(songs)-1)
          pygame.mixer.music.load(songs[rnum][0])
          pygame.mixer.music.set_volume(songs[rnum][1])
          pygame.mixer.music.play()
   clock.tick(80)
   pygame.display.update()
   pygame.display.flip()
