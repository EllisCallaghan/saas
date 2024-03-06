from django.shortcuts import render

from django.http import HttpResponse,HttpRequest

from instaloader import Instaloader, Profile
from pathlib import Path
import csv
import shutil
import os
from selenium import webdriver
from selenium.webdriver.common.by import By


def csvdownload(request :HttpRequest):
  print(request.GET.get('profiles',''))
  target = request.GET.get('profiles','')
  target = target.split(",")

  L = Instaloader()
  
  # CHANGE THESE VARIABLES

  # the user you signed into instagram with
  USER = '90soldschool.hiphop'
  # the profiles you want to get suggested users from
  target_profiles = target

  # allow duplicate entries 
  global allow_Duplicate
  allow_Duplicate = 0

  # END OF VARIABLES
  os.system("python session.py")
  L.load_session_from_file(USER)

  def main(target_profile : str, allow_Duplicate: bool):
    profile = Profile.from_username(L.context,target_profile)
    def get_suggested_users():
      similar_accounts_list = []
      for account in profile.get_similar_accounts():
          similar_accounts_list.append(account.username)
      if len(similar_accounts_list) == 0:
          print(f"[WARNING]: Profile '{target_profile}' did not return any suggested profiles.")
      
      with open('main.csv','rt',newline='') as readCsv:
        duplicate_found = []
        reader = csv.reader(readCsv,delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == target_profile:
              duplicate_found.append(True)
            else:
              duplicate_found.append(False)
        if True in duplicate_found and allow_Duplicate == 0:
          print(f"[WARNING]: Profile '{target_profile}' is duplicated, Duplication is disabled in config.")
          return []
        else:
          return [target_profile,*similar_accounts_list]

                      
    with open('main.csv','r',newline='') as readCsv:
      reader = csv.reader(readCsv,delimiter=' ', quotechar='|')
      if len(list(reader)) != 0:
        with open('main.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            suggested_users = get_suggested_users()
            if(len(suggested_users)) != 0:
              writer.writerow(suggested_users)
      else:
          with open('main.csv', 'w', newline='') as file:
              writer = csv.writer(file)
              writer.writerow(['Profile',*range(1,81)])
              suggested_users = get_suggested_users()
              if(len(suggested_users)) != 0:
                writer.writerow(suggested_users)

  filename = Path('main.csv')
  if os.path.exists('main.csv'):
    os.remove(filename)
  filename.touch(exist_ok=True)
  for target_profile in target_profiles:
    try:
      main(target_profile, allow_Duplicate=allow_Duplicate)
    except:
      response = HttpResponse("An error Occurred",content_type='text/plain')
      response["Access-Control-Allow-Origin"] = "*"
      return response
  data = None
  with open('main.csv','rb') as f:
    data = f.read()
  response = HttpResponse(data, content_type='text/csv')
  response["Content-Disposition"] = "attachment;filename=main.csv"
  response["Access-Control-Allow-Origin"] = "*"
  return response

def download(request : HttpRequest):
  print(request.GET.get('profile',''))
  target = request.GET.get('profile','')
  L = Instaloader()

  # NOTE: rename .env.template to .env, then edit these variables in .env
  USER = "beatles_.mania"

  #NOTE: make sure you have logged into instagram in firefox, DO NOT USE UR MAIN ACCOUNT AS YOU COULD GET BANNED
  L.load_session_from_file(USER)      
  

  # the profile you want to download from
  PROFILE = target
  DOWNLOAD_AMOUNT = 3

  class Main:
      def __init__(self,target_profile:str,download_amount:int,username:str=None):
          self.username = username
          self.target_profile = target_profile
          self.download_amount= download_amount
      def run(self):

          profile = Profile.from_username(L.context,self.target_profile)

          posts_sorted_by_likes = sorted(profile.get_posts(),key=lambda post: post.likes, reverse = True)

          # NOTE: comment out thhe block of code below if you want to download videos/reels only

          def post_is_video(post):
              if post.is_video == True:
                  return post
          posts_sorted_by_likes = list(map(post_is_video,posts_sorted_by_likes))


          for post in range(self.download_amount):
              L.download_post(posts_sorted_by_likes[post],PROFILE)
              
  x= Main(target_profile=PROFILE,download_amount=DOWNLOAD_AMOUNT,username=USER)
  x.run()
  shutil.make_archive('test','zip','ilovemythebeatles')
  data = None
  with open('test.zip','rb') as f:
    data = f.read()

  response = HttpResponse(data, content_type='application/zip')
  response['Content-Disposition'] = 'attachment; test.zip'
  try:
    return response
  finally:
    shutil.rmtree('ilovemythebeatles')
    if os.path.exists('test.zip'):
      os.remove('test.zip')