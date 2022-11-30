from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel 
from typing import Optional

app = FastAPI()

## Class Post extends baseModel
class Post(BaseModel):
    title: str
    content: str
    published: bool = True ##default to true if not provided
    rating: Optional[int] = None

my_posts = [{"title" : "title of post 1", "content" : "content of post 1", "id" : 1}, 
{"title" : "title of post 2", "content" : "content of post 2", "id": 2}] ##local storage as temp testing alt to database

## Path Operation
@app.get("/") # Decorator allows someone to reach these functions using fastAPI (@)
# HTTP get request response to root path "/" of host website (base URL)
async def root(): ## function with arbitrary name, it helps to be as descriptive as possible
     return{"message": "Hello Worlds"} ## fastAPI converts this to JSON format

@app.get("/posts") ## Get is used for retrieving data, if they send this request at "/posts" do get_posts
async def get_posts():
    return{"data" : my_posts} ##fastAPI automatically converts array to JSON

@app.get("/posts/{id}") ##id field is a path parameter
async def get_post(id: int, response: Response): ##fastAPI checks for an int ID
    post = findPost(id)
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, # repeats the effect of the commented code down below
                            detail = f"post with id {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND ##status is an enumerator with the values and definitions saved
        # return {'message': f'post with id {id} was not found'}
    return {"content" : post}

def findPost(id):
    for i in my_posts:
        if i["id"] == int(id):
            return i

@app.post("/posts", status_code= status.HTTP_201_CREATED) ##posts to adhere to API conventions, sets a default status code
async def create_post(post: Post): ## extracts all the information from the post request body and converts it to class Post if possible or error
    ## store extracted data inside payLoad variable
    post_dict = post.dict()
    post_dict['id'] = my_posts[len(my_posts) - 1]['id'] + 1
    my_posts.append(post_dict) ##our array is of dictionaries so need to covnert pydantic array
   
    return{"new_post": post_dict}
    #title: string, content: str

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_posts(id: int):
    post_num = return_post_num(id)
    if post_num:
        my_posts.pop(post_num)
        return
    raise HTTPException(status_code = 404, detail = f"Post with id {id} does not exist.")

@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    new_post = Post(title = post.title, content = post.content, published = post.published, rating = post.rating).dict()
    new_post["id"] = id
    post_num = return_post_num(id)
    if post_num:
        my_posts[post_num] = new_post
        return {"data" : new_post}
    raise HTTPException(statues_code = 404, detail = f"Post with id {id} not found")

def return_post_num(id):
    for i in range(len(my_posts)):
        if my_posts[i]["id"] == int(id):
            return i
