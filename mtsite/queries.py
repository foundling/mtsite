CREATE_POST = 'insert into post (author_id, pub_date, title, content, published) values (?, ?, ?, ?, ?)'
UPDATE_POST = 'update post set pub_date = ?, title = ?, content = ?, published = ? where id = ?' 
TAGS_FOR_POST_BY_POST_ID = 'select tag.tag, tag.id from tag join post_tag on tag.id = post_tag.tag_id join post on post.id = post_tag.post_id where post_id = ?' 
CREATE_TAG = 'insert or ignore into tag (tag) values (?)'
ADD_TAG_TO_POST = 'insert or ignore into post_tag (post_id, tag_id) values (?, ?)'
DELETE_TAG_FROM_POST = 'delete from post_tag where post_tag.post_id = ? and post_tag.tag_id = ?'
ALL_POSTS_WITH_TAGS = '''
select
    author.first_name, author.author_id, post.id, post.title, post.content, post.pub_date, post.published, group_concat(tag.tag, ",") as post_tags
    from post
    join author on post.author_id = author.author_id
    LEFT join post_tag on post.id = post_tag.post_id
    LEFT join tag on post_tag.tag_id = tag.id
    group by post.id;
'''
POST_WITH_TAGS_BY_POST_ID = '''
select

    author.first_name, author.author_id,
    post.id, post.title, post.content, post.pub_date, post.published, group_concat(tag.tag, ",") as post_tags

    from post
    join author on post.author_id = author.author_id
    LEFT join post_tag on post.id = post_tag.post_id
    LEFT join tag on post_tag.tag_id = tag.id
    where post.id = ?;
'''

