from fastapi import APIRouter, Depends, HTTPException, status
from .. import oath2, database, schemas

cursor = database.cursor
conn = database.conn

router = APIRouter(
    prefix = "/votes",
    tags = ['Vote']
)

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.vote)
async def vote(vote:schemas.vote, user:int = Depends(oath2.get_current_user)):
    cursor.execute("SELECT * FROM posts WHERE id = %s LIMIT 1;", (vote.post_id,))
    voted_post = cursor.fetchone()
    if not voted_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with id {vote.post_id} does not exist")
    cursor.execute("SELECT * FROM votes WHERE post_id = %s AND user_id = %s LIMIT 1;", (vote.post_id, user['id']))
    vote_present = cursor.fetchone()

    if vote_present and (vote_present['vote_status'] == vote.vote_status):
        cursor.execute("DELETE FROM votes WHERE post_id = %s AND user_id = %s;", (vote.post_id, user["id"]))
        vote = {"vote_status" : 0, "post_id" : vote.post_id, "user_id" : user['id']} 
    elif vote_present:  
        cursor.execute("UPDATE votes SET vote_status = %s WHERE post_id = %s AND user_id = %s;", (vote.vote_status, vote.post_id, user['id']))
        vote = {"vote_status" : vote.vote_status, "post_id" : vote.post_id, "user_id" : user['id']}
    else:
        cursor.execute("INSERT INTO votes (post_id, user_id, vote_status) VALUES (%s, %s, %s) RETURNING *;", 
            (vote.post_id, user['id'], vote.vote_status))
        vote = cursor.fetchone()

    conn.commit()
    return vote