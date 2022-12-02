from .. import schemas, util, database, oath2
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from typing import List


##each dot makes you go up a directory
router = APIRouter(
    prefix= "/posts", ##adds itself before each route here as a prefix
    tags = ['Posts']
)



cursor = database.cursor
conn = database.conn

@router.get("/", response_model= List[schemas.Post]) ## Get is used for retrieving data, if they send this request at "/posts" do get_posts
async def get_posts(limit: int = 10, offset: int = 0):
    cursor.execute("""SELECT posts.*, COALESCE(SUM(vote_status), 0) AS votes FROM posts LEFT JOIN votes ON posts.id = votes.post_id 
                    GROUP BY posts.id LIMIT %s OFFSET %s;""", (limit,  offset))
    posts = cursor.fetchall()
    for post in posts:
        post = append_user(post)
    return posts ##fastAPI automatically converts array to JSON

@router.get("/{id}", response_model= schemas.Post) ##id field is a path parameter
async def get_post(id: int, response: Response): ##fastAPI checks for an int ID
    cursor.execute("""SELECT posts.*, COALESCE(SUM(vote_status), 0) FROM posts LEFT JOIN votes ON posts.id = votes.post_id 
                    WHERE posts.id = %s GROUP BY posts.id;""", (id, ))
    selected_post = cursor.fetchone()
    if not selected_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, # repeats the effect of the commented code down below
                            detail = f"post with id {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND ##status is an enumerator with the values and definitions saved
        # return {'message': f'post with id {id} was not found'}
    else: 
        selected_post = append_user(selected_post)
    return selected_post

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=schemas.Post) ##posts to adhere to API conventions, sets a default status code
async def create_post(post: schemas.PostCreate, curr_user:int = Depends(oath2.get_current_user)): ## extracts all the information from the post request body and converts it to class Post if possible or error
    ## store extracted data inside payLoad variable
    cursor.execute('INSERT INTO posts (title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING *;', 
            (post.title, post.content, post.published, curr_user['id']))
    ## we use %s to indicate the string variables and assignment them later with execute, prevents SQL injection vulnerability, never pass data directly
    new_post = append_user(cursor.fetchone())
    conn.commit() ## prior changes are stages, this pushes them out
    return new_post
    #title: string, content: str

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_posts(id: int, curr_user:int = Depends(oath2.get_current_user)):
    if (not post_owner(curr_user, id)):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")
    cursor.execute("DELETE FROM posts WHERE id = %s returning *;", (id, ))
    deleted_post = cursor.fetchone()
    if deleted_post:
        conn.commit()   
        return deleted_post
    raise HTTPException(status_code = 404, detail = f"Post with id {id} does not exist.")

@router.put("/{id}", response_model=schemas.Post)
async def update_post(id: int, post: schemas.PostCreate, curr_user:int = Depends(oath2.get_current_user)):
    if (not post_owner(curr_user, id)):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;"
            ,(post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post:
        return updated_post
    raise HTTPException(statues_code = 404, detail = f"Post with id {id} not found")


def post_owner(curr_user: int, post_id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s LIMIT 1;", (post_id,))
    post = cursor.fetchone()
    if post:
        return post['user_id'] == curr_user['id']
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post does not exist")

def append_user(post):
    cursor.execute("SELECT * from users WHERE id = %s LIMIT 1;", (post['user_id'],))
    posted_user = cursor.fetchone()
    post['poster'] =  posted_user
    return post