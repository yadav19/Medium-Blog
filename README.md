# Medium-Blog
- CRUD application
- A Blog server built completely on flask web framework 
- SPA (Single Page Application)

## Features
- User management 
  - login
  - logout
  - registration
  - user session record
 
 - Database 
  - Posts (database table for user Posts)
  - Users (database table to record user details)
 
 ## Source Code Navigator:
 
 ### Python modules used:
    1. flask
    2. os
    3. PIL
    4. flask_sqlalchemy
    5. secrets
    6. datetime
    7. flask_bcrypt
    8. flask_wtf
    9. wtforms
    10. flask_login
 
 ### WEB UI
 1. base()
    - base layout template
    - built using bootstrap
    - location static/base.html
    
 2. index()
    - no args
    - home page
    - location: static/index.html
   
 3. login()
    - no args
    - login page
    - only open when no user logged in
    - location: static/login.html
 
 4. register()
    - no args
    - registration page
    - location: static/register.html
 
 5. profile()
    - no args
    - needs login
    - user details profile page built for user personal detail updation
    - location: static/profile.html
    
6. logout()
    - logout page redirected to index/home page 
 
### CRUD operation on posts:
  1. create_post()
      - no args
      - route: /post/new
      - location: mediumapp.py
      - template: static/create_post.html
      - page to create a post(new)
  2. update_post()
      - route: /posts/<post_id>/update
      - requires login
      - requires post id as argument
      - location: mediumapp.py
      - template: static/createa_post.html
  3. delete_post()
      - route: /post/<post_id>/delete
      - requires login
      - location: mediumapp.py
      - requires post_id as arg
    - route
