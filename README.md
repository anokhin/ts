ts
==

vk.py:
    How to get $OAUTH_KEY:
        Go here
        https://oauth.vk.com/authorize?client_id=4288249&scope=friends,offline,photos,audio,status,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&v=5.17&response_type=token
        Copy the key from url after it redirects you
    Print resulting tsv to stdout:
        python2 vk.py $OAUTH_KEY $USER_ID
    Create (or overwrite) file, its 1st line will contain column names,
    its following lines will contain the tsv.
        python2 vk.py $OAUTH_KEY $USER_ID $FILENAME
    Append to existing file, this won't add column names.
        python2 vk.py $OAUTH_KEY $USER_ID $FILENAME --append

